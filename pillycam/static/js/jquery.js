$("#applyEffect").click(function() {
    // Get the selected effect
    var selectedEffect = $("select[name='effect']").val();

    // Apply the selected effect using AJAX
    $.get({
        url: "{% url 'apply_effect' %}",
        data: {
            effect: selectedEffect,
            image_path: $("#uploadedImage").attr("src")
        },
        success: function(data) {
            // Display the processed image
            $("#processedImage").attr("src", data);
        },
        error: function() {
            alert("Error applying effect.");
        }
    });
});

// Submit the form to upload and save the image
$("#uploadForm").submit(function(e) {
    e.preventDefault();

    $.ajax({
        url: "{% url 'main:home' %}",
        type: "post",
        data: new FormData(this),
        processData: false,
        contentType: false,
        success: function(data) {
            // Display the uploaded image
            $("#uploadedImage").attr("src", data);
            // Clear the processed image
            $("#processedImage").attr("src", "");
        },
        error: function() {
            alert("Error uploading image.");
        }
    });
});