from PIL import Image
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound,HttpResponseBadRequest
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
from django.core.files import File
from pills.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR

LOGIN_URL = 'account_login'  

def custom_page_not_found(request, exception=None):
    return page_not_found(request, exception, template_name='main/404.html')

    
def custom_server_error(request, *args, **kwargs):
    return server_error(request)


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

        return context

    def post(self, request, *args, **kwargs):
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded image and apply the selected effect
            new_image = UploadImage(image=request.FILES['image'], user=request.user)
            new_image.save()

            return HttpResponseRedirect(reverse('home'))
        return HttpResponse("Error", status=403)


class SaveProcessedImage(LoginRequiredMixin, TemplateView):
    """Save processed images on demand."""
    
    login_required = True
    template_name = 'main/index.html'

    def post(self, request):
        """Handle POST requests for saving processed images."""
        user_id = request.user.id  # Get the user ID
        context = {}  # Initialize context for rendering the template

        # Check if the form data includes the path of the processed image
        if request.POST.get('path'):
            try:
                # Get the path of the processed image from the form data
                path = request.POST.get('path')
                
                # Generate a relative path in the 'profile' folder with today's date
                today = datetime.now()
                today_path = today.strftime("%Y/%m/%d")
                media_path = os.path.join('profile', today_path, os.path.basename(path))

                # Create an absolute path to save the processed image
                new_path = os.path.join(MEDIA_ROOT, media_path)

                # Check if the file has been successfully copied
                if self.copyfiles(path, new_path):
                    # Update or create a new entry in the UploadImage model
                    UploadImage.objects.update_or_create(
                        file=media_path, owner=request.user, edited=1
                    )
                    # Redirect to the home page on successful save
                    return HttpResponseRedirect(reverse('main:home'))
                else:
                    # Handle case where the file copying failed
                    context['error_message'] = "Error occurred while copying the file."
            except Exception as e:
                # Handle unexpected errors
                context['error_message'] = f"An unexpected error occurred: {str(e)}"
        
        # Render the template with the context (including any error message)
        return render(request, self.template_name, context)

    def copyfiles(self, source, destination):
        """Create Folder and files."""
        try:
            # Ensure the directory for the destination exists, create if not
            os.makedirs(os.path.dirname(destination), exist_ok=True)

            # Create an absolute source path
            abs_source = os.path.join(BASE_DIR, source)

            # Copy the file from source to destination
            shutil.copy(abs_source, destination)
            return True  # Return True if copying is successful
        except Exception as e:
            # Handle errors during copying
            return False


class DeleteImage(LoginRequiredMixin, TemplateView):
    """Deletes Photos and records."""

    def get(self, request, id):
        """Delete record and images."""
        image = UploadImage.objects.get(id=id)
        if image:
            return HttpResponse(image.delete())
        return HttpResponse(image.delete())


def apply_effect_view(request):
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded image
            uploaded_image = form.save()

            # Get the path of the uploaded image
            image_path = uploaded_image.image.path

            # Get the selected effect from the form
            effect = request.POST['effect']

            try:
                # Create an instance of ApplyEffects with the image path
                apply_effects_instance = ApplyEffects(image_path)

                # Apply the specified effect
                edited_image_path = apply_effects_instance.apply_effect(effect)

                # Get the relative path from the base directory
                relative_path = os.path.relpath(edited_image_path, settings.BASE_DIR)

                # Perform housekeeping to delete temporary files
                housekeeping(settings.MEDIA_ROOT)

                # Return the relative path in the HTTP response
                return HttpResponse(relative_path, content_type="text/plain")

            except FileNotFoundError as e:
                return HttpResponse(f"Error: File not found at path: {image_path}", status=404)

            except ValueError as e:
                return HttpResponse(f"Error: {str(e)}", status=400)

            except Exception as e:
                return HttpResponse(f"Error: An unexpected error occurred: {str(e)}", status=500)

    return HttpResponse("Method not allowed", status=405)