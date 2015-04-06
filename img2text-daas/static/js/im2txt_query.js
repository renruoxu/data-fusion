$(function() {
    $('#img_form').submit(function(event) {
        event.preventDefault();
        
        $.ajax({
            type: 'GET',
            url: '/plot',
            dataType: 'json',
            cache: false,
            processData: false,
            async: true,
            beforeSend: function() {
              $("#plot").empty();
            },
            success: function(data) {
              $("#plot").append(data);
              console.log(data);
            },

        });
    });
});
