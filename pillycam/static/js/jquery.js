// Function to handle applying effects and saving images

var applyEffectUrl = '{% url "apply_effect" %}';

function applyAndSaveEffect(imagePath, effect) {
    // Get CSRF token from the page
    var csrfToken = $('[name=csrfmiddlewaretoken]').val();

    // Make an AJAX request to apply effect
    $.ajax({
        url: applyEffectUrl,  
        type: 'GET', // Changed to POST since you are sending file data
        data: {
            'image': imagePath, 
            'effect': effect,
            'csrfmiddlewaretoken': csrfToken
        },
        success: function (processedImagePath) {
            // Display the processed image in a modal or preview
            $('#previewImage').attr('src', processedImagePath);
            $('#imagePreviewModal').modal('show');
            console.log('Successful effect application');

            // Update the value of the image input for saving
            $('#imageInput').val(processedImagePath);
            // Enable the save button
            $('#saveButton').prop('disabled', false);
        },
        error: function (error) {
            console.error('Error applying effect:', error);
            // Handle error, show an alert, etc.
        }
    });
}

// Click event for applying effect
$('#applyEffect').click(function () {
    var imagePath = $('#imageInput').val();  // Get the image path from the input
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

// Event listener for Upload and Save button
$('#uploadForm').submit(function (event) {
    event.preventDefault();  
    // Submit the form using AJAX
    $.ajax({
        url: '/save_effect/',  
        type: 'POST',
        data: new FormData(this),
        processData: false,
        contentType: false,
        success: function (response) {
            window.location.href = '{% url "home" %}' ;
        },
        error: function (error) {
            console.error('Error saving effects:', error);
        }
    });
});

// Function to handle deleting effects
function deleteEffect(imagePath) {
    // Get CSRF token from the page
    var csrfToken = $('[name=csrfmiddlewaretoken]').val();

    // Make an AJAX request to delete effect
    $.ajax({
        url: '/delete_effect/',  
        type: 'POST',
        data: {
            'image': imagePath,
            'csrfmiddlewaretoken': csrfToken
        },
        success: function (response) {
            // Handle successful deletion (e.g., update UI, show a message)
            console.log('Effect deleted successfully');
        },
        error: function (error) {
            console.error('Error deleting effect:', error);
            // Handle error, show an alert, etc.
        }
    });
}

// Click event for deleting effect
$('#deleteEffect').click(function () {
    var imagePath = $('[name=image]').val();  // Get the image path from the input

    // Check if the image path is not empty
    if (imagePath) {
        // Delete the effect
        deleteEffect(imagePath);
    } else {
        // Handle case where the image path is not selected
        alert('Please select an image to delete the effect.');
    }
});
