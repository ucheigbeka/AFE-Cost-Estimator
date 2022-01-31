let is_deleting = false;

function initJsGrid(config) {
    let {fields, url} = config;

    let jsGridConfig = {
        fields: fields,
        autoload: true,

        width: '100%',

        controller: {
            loadData: loadData,
            insertItem: insertItem,
            updateItem: updateItem,
            deleteItem: deleteItem
        },

        sorting: true,
        editing: true,
        inserting: true,

        confirmDeleting: false,
        onItemDeleting: confirmItemDelete,
    };

    function loadData(filter) {
        return $.ajax({
            url: url,
            dataType: 'json'
        });
    }

    function insertItem(item) {
        return $.ajax({
            url: url,
            type: 'POST',
            data: item
        });
    }

    function updateItem(item) {
        return $.ajax({
            url: url,
            type: 'PUT',
            data: item
        });
    }

    function deleteItem(item) {
        return $.ajax({
            url: url,
            type: 'DELETE',
            data: item
        });
    }

    function confirmItemDelete(args) {
        if (!is_deleting) {
            args.cancel = true;
            $('#deleteAlert').modal('show');
            $('#btnDelete').one('click', {item: args.item}, function(arg) {
                is_deleting = true;
                $("#jsGrid").jsGrid("deleteItem", arg.data.item);
                $('#deleteAlert').modal('hide');
            });
            $('#deleteAlert').one('hidden.bs.modal', function() {
                $('#btnDelete').off('click');
            });
        } else {
            is_deleting = false;
        }
    }

    let uploadBtn = $('<button class="btn btn-primary">Upload Record</button>');
    uploadBtn.on('click', function() {
        $('#uploadAlert').modal('show');
    });

    $('#jsGrid').jsGrid(jsGridConfig);
    $('#jsGrid').append(uploadBtn);
}