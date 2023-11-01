$('#saleType').change(function(){
    let val = $(this).val()
    if (val == 1) {
        $('#sale').show()
    } else {
        $('#sale').hide()
    }
});