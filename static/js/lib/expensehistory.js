// SUMMARY: this file handles all of the functionality to view, update, or delete a users expense history on the 'Expense History' page of Tendie Tracker.

// When the document is ready, initialize the necessary functionality
$(document).ready(function() {
    // While the modal is showing (CSS transitions aren't 100% finished yet), set the title of the modal and the expense fields
    $('#updateModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget) // Button that triggered the modal
        var description = button.data('description') // Extract info from data-* attributes
        var category = button.data('category') // Extract info from data-* attributes
        var date = button.data('date') // Extract info from data-* attributes
        var name = button.data('name') // Extract info from data-* attributes
        var amount = button.data('amount') // Extract info from data-* attributes
        var submitTime = button.data('submittime')
        var modal = $(this)
        modal.find('.modal-title').text("Update Expense Record")
        // Fields for current expense values
        modal.find('#oldDescription').val(description)
        modal.find('#oldCategory').val(category)
        modal.find('#oldDate').val(date)
        modal.find('#oldName').val(name)
        modal.find('#oldAmount').val(amount)
        modal.find('#submitTime').val(submitTime)
        // Fields for updating the expense
        modal.find('#description').val(description)
        modal.find('#category').val(category)
        modal.find('#date').val(date)
        modal.find('#name').val(name)
        modal.find('#amount').val(amount)
    })

    // As the modal becomes hidden (CSS transitions are 100% finished), clear the fields from the modal
    $('#updateModal').on('hidden.bs.modal', function () {
        $('#description').val('')
        $('#category').val('')
        $('#date').val('')
        $('#name').val('')
        $('#amount').val('')

        // Make sure the UX toggles back to the default 'update expense' mode (instead of delete)
        if (isDeleteUX == true) {
            toggleDeleteUX();
            isDeleteUX = false;
        }
    })
});
