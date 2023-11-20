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
from .effects import applyEffects
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


class EffectView(TemplateView):
    template_name = 'main/index.html'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['effect'] = self.request.GET.get('effect')
        context['image_path'] = self.request.GET.get('image_path')
        return context

    def get(self, request, *args, **kwargs):
        effect = self.request.GET.get('effect')
        image_path = self.request.GET.get('image_path')

        if effect and image_path:
            applier = ApplyEffects(image_path)
            processed_image = applier.apply_effect(effect)

            if processed_image:
                # Save the processed image in the desired location
                edited_path = f"{os.path.splitext(image_path)[0]}_{effect}_edited.png"
                processed_image.save(edited_path, format='PNG', quality=100)
                
                # Pass the edited image path to the template
                self.kwargs['edited_image_path'] = edited_path

        return super().get(request, *args, **kwargs)

class HomeView(LoginRequiredMixin, TemplateView):
    login_url = 'account_login'
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Prepare the context for rendering the dashboard
        context['form'] = UploadImageForm()
        context['images'] = UploadImage.objects.filter(user=self.request.user)
        context['effects'] = ['brightness', 'grayscale', 'blackwhite', 'sepia', 'contrast', 'blur', 'findedges', 'bigenhance', 'enhance', 'smooth', 'emboss', 'contour', 'sharpen']
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
                applier = applyEffects(image_path)
                applier.apply_effect(effect)

            return HttpResponseRedirect(reverse('main:home'))
        return HttpResponse("Error", status=403)


BASE_DIR = settings.BASE_DIR
MEDIA_URL = settings.MEDIA_URL
MEDIA_ROOT = settings.MEDIA_ROOT

class ImageProcessing(LoginRequiredMixin, TemplateView):
    """Process image and return the route of the processed image."""

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

            # Load the image
            image = Image.open(os.path.join(BASE_DIR, image_path))

            # Create an absolute path for folder creation
            output = os.path.join(BASE_DIR, MEDIA_URL, 'CACHE/temp/', str(user_id))
            os.makedirs(output, exist_ok=True)

            # Set the path to save the processed image
            temp_file_location = "{}{}.PNG".format(file, effect_name)

            # Set route for exclusive to thumbnails
            if request.GET.get('preview'):
                temp_file_location = "thumbnails/{}.PNG".format(effect_name)

            temp_file = os.path.join(output, temp_file_location)

            # Apply the selected effect
            applier = applyEffects(image_path)
            applier.apply_effect(effect_name)

            # Perform housekeeping
            housekeeping(output)

            # Save the processed image
            applier.pil_image.save(temp_file, 'PNG')

            # Construct the file URL
            file_url = os.path.join(MEDIA_URL, 'CACHE', 'temp', str(user_id), temp_file_location)

            return HttpResponse(file_url)
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