from django import forms
from .models import UploadedImage

class UploadedImageForm(forms.ModelForm):
    """
    Form for uploading images.
    """
    class Meta:
        model = UploadedImage
        fields = ['image']
    
    def clean_image(self):
        """
        Validate the uploaded image.
        """
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError('You must upload an image.')
        return image
