$(document).ready(function () {
    // Function to handle applying effects and saving images
    function applyAndSaveEffect(imagePath, effect) {
        // Get CSRF token from the page
        var csrfToken = $('[name=csrfmiddlewaretoken]').val();

        // Make an AJAX request to apply effect
        $.ajax({
            url: '{% url "main:apply_effect" %}',  
            type: 'GET',
            data: {
                'image': imagePath, 
                'effect': effect,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function (processedImagePath) {
                // Display the processed image in a modal or preview
                $('#previewImage').attr('src', processedImagePath);
                $('#imagePreviewModal').modal('show');
                console.console.log('successful');
            },
            error: function (error) {
                console.error('Error applying effect:', error);
                // Handle error, show an alert, etc.
            }
        });
    }

    $('#applyEffect').click(function () {
        var imagePath = $('[name=image]').val();  // Get the image path from the input
        var selectedEffect = $('[name=effect]').val();  // Get the selected effect

        // Check if image path and effect are not empty
        if (imagePath && selectedEffect) {
            // Apply and save the effect
            applyAndSaveEffect(imagePath, selectedEffect);
        } else {
            // Handle case where image path or effect is not selected
            alert('Please select an image and an effect.');
        }
    });

    // Event listener for Upload and Save button (assuming you want to upload and save separately)
    $('#uploadForm').submit(function (event) {
        event.preventDefault();  
        // Submit the form using AJAX
        $.ajax({
            url: '/save_effects/', 
            type: 'POST',
            data: new FormData(this),
            processData: false,
            contentType: false,
            success: function (response) {
                window.location.href = '/home/';
            },
            error: function (error) {
                console.error('Error saving effects:', error);
            }
        });
    });
});
