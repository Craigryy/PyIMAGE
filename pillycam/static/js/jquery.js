$(document).ready(function () {
    // Apply Effect Form Submission
    $("#applyEffectForm").submit(function (event) {
        event.preventDefault();

        var formData = new FormData($(this)[0]);

        $.ajax({
            type: 'POST',
            url: '/apply_effect/',
            data: formData,
            contentType: false,
            processData: false,
            xhrFields: {
                responseType: 'blob'
            },
            success: function (response) {
                var imageUrl = URL.createObjectURL(response);

                // Display the processed image
                $("#result").text("Edited Image");
                $('#processedImage').attr('src', imageUrl);
            },
            error: function (error) {
                $("#result").text("Error: " + error.responseText);
            }
        });
    });

    // Reset Button Click Event
    $("#resetButton").click(function () {
        $("#applyEffectForm")[0].reset();
        $("#processedImage").attr("src", "#");
        $("#result").text("");
    });

    // Save Button Click Event
    $("#saveButton").click(function () {
        pass
    });
    
    // Upload Button Click Event
    $("#uploadButton").on("click", function () {
        // Get the form data
        var formData = new FormData($("#applyEffectForm")[0]);
    
        // Make an AJAX request
        $.ajax({
            type: "POST",
            url: "/save-effects/",  // Update this with your actual URL
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
                // Reload the container and add the new image
                $(".container").load(location.href + " .container");
                alert("yipeee");
            },
            error: function (xhr, status, error) {
                console.error("Error:", error);
            }
        });
    });
    
    // Delete Button Click Event
    $("#deleteButton").click(function () {
        // Get the image ID from the button's data-id attribute
        var imageId = $(this).attr('id');

        // Make an AJAX request to delete the image
        $.ajax({
            type: "POST",
            url: `/image/${imageId}/delete/`, 
            success: function (data) {
                // Reload the container after deletion
                $(".container").load(location.href + " .container");
            },
            error: function (xhr, status, error) {
                console.error("Error:", error);
            }
        });
    });
});



// jquery_script.js

$(document).ready(function() {
    $('#uploadForm').submit(function(e) {
        e.preventDefault();

        var formData = new FormData(this);

        $.ajax({
            type: 'POST',
            url: '/apply_effect/',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                // Display success message or handle response
                $('#result').html(response);
            },
            error: function(error) {
                console.log(error);
                // Display error message or handle error
                $('#result').html('Error processing image');
            }
        });
    });
});
