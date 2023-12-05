// your_app/static/your_app/js/apply_effect.js
$(document).ready(function() {
    $("#applyEffectForm").submit(function(event) {
        event.preventDefault();

        var formData = new FormData($(this)[0]);

        $.ajax({
            type: 'POST',
            url: '/apply_effect/',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                // Display the relative path in the 'result' div
                $("#result").text("Edited Image Path: " + response);
            },
            error: function(error) {
                // Display the error message in the 'result' div
                $("#result").text("Error: " + error.responseText);
            }
        });
    });
});
