// Function to handle applying effects and saving images
function applyAndSaveEffect(imagePath, effect, saveButton, imagePathElement) {
    // Get CSRF token from the page
    var csrfToken = $('[name=csrfmiddlewaretoken]').val();

    // Make an AJAX request to apply effect
    $.ajax({
        url: "{% url 'main:apply_effect' %}", 
        type: 'GET',
        data: {
            'image': imagePath,
            'effect': effect,
            'csrfmiddlewaretoken': csrfToken
        },
        success: function (data) {
            // Check if the image path has changed (effect applied)
            if (data !== imagePath) {
                // Save the new image with the current date and time
                var currentDate = new Date();
                var formattedDate = currentDate.toISOString().slice(0, 19).replace("T", " ");
                var newImageName = 'new_image_' + formattedDate + '.png';

                // Create a new image element with the updated path
                var newImage = $('<img>').attr('src', data).attr('alt', 'New Image');
                // Append the new image to the body (you can adjust this based on your needs)
                $('body').append(newImage);
                alert("yeeeee");

                // Update the download link
                saveButton.attr('href', data);
                console.log('Successful');

                // Optionally, you can reload or update the wrapper and image-collection
                $(".wrapper").load("/ .image-collection", function () {
                    // Additional logic after loading
                    // For example, you can attach click events directly here
                    $('.wrapper img').on('click', function () {
                        // Your click event logic here
                    });
                    $(".thumbholder .delete").on('click', function () {
                        // Your delete event logic here
                    });
                });
            }
        },
        error: function (error) {
            console.error('Error applying effect:', error);
            // Handle error, show an alert, etc.
        }
    });
}

// Event listener for Apply Effect button
$('#applyEffect').click(function () {
    var imagePath = $('[name=image]').val();  // Get the image path from the input
    var selectedEffect = $('[name=effect]').val();  // Get the selected effect

    // Check if image path and effect are not empty
    if (imagePath && selectedEffect) {
        // Apply and save the effect
        applyAndSaveEffect(imagePath, selectedEffect, $('#saveButton'), $('#previewImage'));
    } else {
        // Handle case where image path or effect is not selected
        alert('Please select an image and an effect.');
    }
});

// Event listener for image thumbnail click
$('.img-thumbnail').on('click', function () {
    var imagePath = $(this).attr('src');
    $('#previewImage').attr('src', imagePath);
    $('#previewModal').modal('show');
});

// Event listener for Save Button
$('#saveButton').click(function () {
    var imagePath = $('[name=image]').val();  // Get the image path from the input
    var selectedEffect = $('[name=effect]').val();  // Get the selected effect
    var csrfToken = $('[name=csrfmiddlewaretoken]').val();

    // Make an AJAX request to save effects
    $.ajax({
        url: "save-effects/",  // For save_effects
        type: 'POST',
        data: {
            'image': imagePath,
            'effect': selectedEffect,
            'csrfmiddlewaretoken': csrfToken
        },
        success: function (data) {
            // Assuming the response includes the updated image or relevant information
            // Update the images on the page or handle the response accordingly
            console.log('Effect saved successfully:', data);

            // Example: Reload the page after saving effects
            window.location.reload();
        },
        error: function (error) {
            console.error('Error saving effects:', error);
            // Handle error, show an alert, etc.
        }
    });
});

// Attach a click event to all delete buttons with class 'delete-button'
$('.delete-button').on('click', function () {
    // Get the image ID from the button's data attribute or any other attribute you prefer
    var imageId = $(this).attr('id');

    // Confirm deletion
    var confirmDelete = confirm('Are you sure you want to delete this image?');

    if (confirmDelete) {
        // Send an AJAX request to the delete URL
        $.ajax({
            type: 'POST',
            url: '/image/' + imageId + '/delete/',
            data: {
                'csrfmiddlewaretoken': '{{ csrf_token }}',  // Include CSRF token for security
            },
            success: function (data) {
                // Handle success, e.g., remove the deleted image from the UI
                console.log('Image deleted successfully');
                // Optionally, you can reload the page or update the UI accordingly
                // window.location.reload();
            },
            error: function (xhr, textStatus, errorThrown) {
                // Handle errors
                console.error('Error deleting image:', errorThrown);
            }
        });
    }
});

// Event listener for Upload and Save button
$('#uploadForm').submit(function (event) {
    event.preventDefault();
    // Submit the form using AJAX
    $.ajax({
        url: '{% url "main:save_effect" %}',
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
