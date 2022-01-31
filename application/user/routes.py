from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message

from application import app, db, bcrypt, login_manager
from application.utils import validate_signature, is_safe_url, generate_signed_url, send_email
from .models import User
from .api import api

app.register_blueprint(api, url_prefix='/api')

login_manager.login_view = '.login'
login_manager.login_message_category = 'error'


@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))


@app.route('/')
@login_required
def index():
    if not current_user.is_active:
        flash('This email has not yet been authenticated', 'info')
    return render_template('dashboard.html'), 200


@app.route('/activate/<token>')
def activate(token=None):
    is_valid, data = validate_signature(token, 'activate')
    if not is_valid:
        return data, 200
    user = User.query.get(data)
    user.verified = True
    db.session.add(user)
    db.session.commit()
    return 'Your account has successfully been activated', 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user, force=True)

            _next = request.args.get('next')
            if not is_safe_url(_next):
                abort(400)

            return redirect(_next or url_for('index'))
        flash('Invalid email and or password', 'error')
    return render_template('auth/login.html'), 200


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if request.form['password'] == request.form['confirmPassword']:
            password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            user = User(fullname=request.form['fullname'], company_name=request.form['companyName'],
                        email=request.form['email'], password=password)
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully', 'success')

            signed_url = generate_signed_url(user.id, 'activate')
            msg = Message('Account Activation', recipients=[user.email])
            msg.html = f'Activation link: <a href="{signed_url}" target="_blank">{signed_url}</a>'
            if send_email(msg):
                flash('An activation link has been sent to your email', 'info')
            else:
                flash('An error occurred in sending an activation link. Login and try again', 'error')

            return redirect(url_for('login'))
        flash('Passwords don\'t match', 'error')
    return render_template('auth/register.html'), 200


@app.route('/reset', methods=['GET', 'POST'])
@app.route('/reset/<token>')
def reset(token=None):
    if token:
        is_valid, data = validate_signature(token, 'reset')
        if is_valid:
            user = User.query.get(data)
            return render_template('auth/password-reset.html', email=user.email), 200
        flash(data, 'error')
        return render_template('auth/reset.html'), 200

    if request.method == 'POST' and request.form.get('password'):
        user = User.query.filter_by(email=request.form['email']).first_or_404()
        user.password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        db.session.add(user)
        db.session.commit()
        flash('Password successfully changed', 'success')
        return redirect(url_for('login'))
    elif request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first_or_404()

        if not user.is_active:
            flash('This email has not yet been authenticated', 'info')
            return render_template('auth/reset.html'), 200

        reset_link = generate_signed_url(user.id, 'reset')
        msg = Message('Password Reset', recipients=[email])
        msg.html = f'Reset link: <a href="{reset_link}" target="_blank">{reset_link}</a>'
        if send_email(msg):
            flash('A reset link has been sent to your email', 'info')
        else:
            flash('An error occurred. Try again', 'error')
    return render_template('auth/reset.html'), 200


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
