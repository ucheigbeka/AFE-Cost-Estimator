$(document).ready(function(event){
    // Floating Action Button
    let fabParent = $('.fab').parent();
    fabParent.addClass('fab-container');
});

function showErrorAlert(msg) {
    let errorAlert = $('#errorAlert');
    errorAlert.find('.modal-body').html(`<p>${msg}</p>`)
    errorAlert.modal('show');
  }
