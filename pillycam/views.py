from PIL import Image
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from .models import UploadImage
from .forms import UploadImageForm
from .effects import ApplyEffects
from .clean import housekeeping
from django.conf import settings
import os
from django.http import Http404
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.views.defaults import page_not_found, server_error

LOGIN_URL = 'account_login'  

class LoginRequiredMixin(object):
    """View mixin that requires the user to be authenticated."""
    @method_decorator(login_required(login_url=LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class HomeView(LoginRequiredMixin, TemplateView):
    login_url = 'account_login'
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Prepare the context for rendering the dashboard
        context['form'] = UploadImageForm()
        context['images'] = UploadImage.objects.filter(user=self.request.user)
        context['edited_images'] = UploadImage.objects.filter(user=self.request.user, edited=True)
        context['effects'] = ['brightness', 'grayscale', 'blackwhite', 'sepia', 'contrast', 'blur', 'findedges', 'bigenhance', 'enhance', 'smooth', 'emboss', 'contour', 'sharpen']
        
        # Retrieve processed images
        processed_images = []
        for edited_image in context['edited_images']:
            processed_image_path = edited_image.get_processed_image_path()
            if processed_image_path:
                processed_images.append(processed_image_path)

        context['processed_images'] = processed_images

        return context

    def post(self, request, *args, **kwargs):
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded image and apply the selected effect
            new_image = UploadImage(image=request.FILES['image'], user=request.user)
            new_image.save()

            # Apply effect if selected
            effect = request.POST.get('effect')
            if effect:
                image_path = new_image.image.path
                applier = ApplyEffects(image_path)
                applier.apply_effect(effect)

            return HttpResponseRedirect(reverse('home'))
        return HttpResponse("Error", status=403)

class SaveProcessedImage(LoginRequiredMixin, TemplateView):
    """Save processed images on demand."""
    
    template_name = 'main/index.html'

    def post(self, request):
        """Save processed image."""
        path = request.POST.get('path')
        
        if path:
            today_path = datetime.now().strftime("%Y/%m/%d")
            filename = os.path.basename(path)

            # Create relative media path
            media_path = os.path.join('profile', today_path, filename)

            # Create media path to get the file
            new_path = os.path.join(MEDIA_ROOT, media_path)

            # Copy the file
            if self.copyfiles(path, new_path):
                # Update or create the UploadFile model
                UploadImage.objects.update_or_create(
                    file=media_path, owner=request.user, edited=1)
                
                return HttpResponseRedirect(reverse('home'))

        return HttpResponse("Error occurred", status=405)

    def copyfiles(self, source, destination):
        """Create Folder and files."""
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        abs_source = os.path.join(BASE_DIR, source)

        try:
            shutil.copy(abs_source, destination)
        except Exception as e:
            print(f"Error copying file: {e}")
            return False

        return True


class ImageProcessing(LoginRequiredMixin, View):
    BASE_DIR = settings.BASE_DIR
    MEDIA_URL = settings.MEDIA_URL

    def apply_effect(self, image_path, effect_name):
        """
        Apply the specified image effect using the ApplyEffects class.

        Parameters:
        - image_path (str): Path to the original image.
        - effect_name (str): Name of the image effect to apply.

        Returns:
        - str: Path to the processed image.
        """
        try:
            # Load the original image
            image = Image.open(os.path.join(self.BASE_DIR, image_path))

            # Create an instance of ApplyEffects
            applier = ApplyEffects(image)

            # Apply the selected effect
            processed_image_path = applier.apply_effect(effect_name)

            return processed_image_path
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None

    def get(self, request):
        """
        Handle GET requests for image processing.

        Parameters:
        - request (HttpRequest): Django HttpRequest object.

        Returns:
        - HttpResponse: Response containing the processed image URL or an error message.
        """
        user_id = request.user.id
        effect_name = request.GET.get('effect', '').replace(u'\xa0', '')
        image_path = request.GET.get('path')

        if not image_path:
            return HttpResponseNotFound("Image not found")

        file_name = os.path.basename(image_path)
        file, ext = os.path.splitext(file_name)

        # Create a directory for storing the processed images
        output = os.path.join(self.BASE_DIR, self.MEDIA_URL, 'CACHE/temp/', str(user_id))
        os.makedirs(output, exist_ok=True)

        # Set the path to save the processed image
        temp_file_location = "{}{}.PNG".format(file, effect_name)
        temp_file_location = "thumbnails/{}.PNG".format(effect_name) if request.GET.get('preview') else temp_file_location
        temp_file = os.path.join(output, temp_file_location)

        # Apply the selected effect using the apply_effect method
        processed_image_path = self.apply_effect(image_path, effect_name)

        if processed_image_path:
            # Perform housekeeping
            housekeeping(output)

            # Save the processed image
            processed_image = Image.open(processed_image_path)
            processed_image.save(temp_file, 'PNG')

            # Construct the file URL
            file_url = os.path.join(self.MEDIA_URL, 'CACHE', 'temp', str(user_id), temp_file_location)

            return HttpResponse(file_url)
        else:
            # Return an error response if processing fails
            return HttpResponseNotFound("Error processing image.")
            
class DeleteImage(View, LoginRequiredMixin):
    """
    View to delete all existing photos for the logged-in user.
    """

    def get(self, request, *args, **kwargs):
        try:
            images = UploadImage.objects.filter(user=request.user)
            for image in images:
                # Trigger pre_delete signals to delete image files
                image.delete()
            return HttpResponse("success", content_type="text/plain")
        except UploadImage.DoesNotExist:
            raise Http404("No photos found for the user.")


def custom_page_not_found(request, exception=None):
    return page_not_found(request, exception, template_name='main/404.html')

    
def custom_server_error(request, *args, **kwargs):
    return server_error(request)