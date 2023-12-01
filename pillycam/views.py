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

LOGIN_URL = 'account_login'  

class LoginRequiredMixin(object):
    """View mixin that requires the user to be authenticated."""
    @method_decorator(login_required(login_url=LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

class PillowImageView(TemplateView):
    ''' Class defined to apply effect to image.'''

    def get(self, request, *args, **kwargs):
        pilimage = str(request.GET.get('image'))
        effect = request.GET.get('effect')

        filepath, ext = os.path.splitext(pilimage)
        edit_path = filepath + 'edited' + ext

        image_effects = ApplyEffects(pilimage)
        edited_path = image_effects.apply_effect(effect)

        return HttpResponse(os.path.relpath(edited_path, settings.BASE_DIR), content_type="text/plain")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photos = [f for f in os.listdir(settings.MEDIA_ROOT) if f.endswith(('.jpg', '.jpeg', '.png'))]
        context['photos'] = photos
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)


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

            return HttpResponseRedirect(reverse('main:home'))
        return HttpResponse("Error", status=403)


class ImageProcessing(LoginRequiredMixin, TemplateView):
    """Process image and return the route of the processed image."""

    BASE_DIR = settings.BASE_DIR
    MEDIA_URL = settings.MEDIA_URL
    MEDIA_ROOT = settings.MEDIA_ROOT

    def apply_effect(self, image_path, effect_name):
        try:
            # Load the image
            image = Image.open(os.path.join(self.BASE_DIR, image_path))

            # Create an instance of ApplyEffects
            applier = ApplyEffects(image)

            # Apply the selected effect
            processed_image_path = applier.apply_effect(effect_name)

            # Return the processed image path
            return processed_image_path
        except Exception as e:
            # Handle exceptions, e.g., image not found or unsupported effect
            print(f"Error processing image: {str(e)}")
            return None

    def get(self, request):
        user_id = request.user.id
        effect_name = request.GET.get('effect')
        image_path = request.GET.get('path')

        # Replace non-breaking space with a regular space
        effect_name = effect_name.replace(u'\xa0', '')

        if image_path:
            # Extract the file name and extension
            file_name = os.path.basename(image_path)
            file, ext = os.path.splitext(file_name)

            # Create an absolute path for folder creation
            output = os.path.join(self.BASE_DIR, self.MEDIA_URL, 'CACHE/temp/', str(user_id))
            os.makedirs(output, exist_ok=True)

            # Set the path to save the processed image
            temp_file_location = "{}{}.PNG".format(file, effect_name)

            # Set route for exclusive to thumbnails
            if request.GET.get('preview'):
                temp_file_location = "thumbnails/{}.PNG".format(effect_name)

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
        else:
            # Handle the case when image_path is None
            return HttpResponseNotFound("Image not found")


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
                
                return HttpResponseRedirect(reverse('main:home'))

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


def custom_404(request,exception):
    return render(request, 'main/404.html')


def custom_500(request):
    return render(request, 'main/500.html')