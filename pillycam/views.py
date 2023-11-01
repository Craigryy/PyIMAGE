from PIL import Image
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.shortcuts import render
from datetime import datetime
import os
import shutil
from .forms import UploadImageForm
from .models import UploadImage
from .effects import effect
from pills.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR
from .clean import housekeeping
import random

# View to display available image effects
class EffectsView(TemplateView):
    template_name = "effects.html"

    def get(self, request, *args, **kwargs):
        # Get a list of available effects and render them
        effect_names = list(effect.keys())
        return self.render_to_response({'effects': effect_names})

# Main dashboard view with file upload functionality
class Home(LoginRequiredMixin, TemplateView):
    login_url = 'account_login'
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Prepare the context for rendering the dashboard
        context['form'] = UploadImageForm()
        context['images'] = UploadImage.objects.filter(user=self.request.user)
        context['effects'] = effect.keys()
        return context

    def post(self, request):
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded image and redirect to the dashboard
            new_image = UploadImage(image=request.FILES['image'], user=request.user)
            new_image.save()
            return HttpResponseRedirect(reverse('main:home'))
        return HttpResponse("Error", status=403)

# View to save a processed image
class SaveProcessedImage(LoginRequiredMixin, TemplateView):
    login_url = 'account_login'
    template_name = 'main/index.html'

    def post(self, request):
        if request.POST.get('path'):
            today = datetime.now()
            today_path = today.strftime("%Y/%m/%d")
            path = request.POST.get('path')
            imagename = os.path.basename(path)
            media_path = os.path.join('profile', today_path, imagename)
            new_path = os.path.join(MEDIA_ROOT, media_path)
            path_ready = self.copy_files(path, new_path)

            if path_ready:
                # Update or create a record of the processed image and return to the dashboard
                UploadImage.objects.update_or_create(image=media_path, user=request.user, edited=1)
                return HttpResponseRedirect(reverse('main:home'))
            return HttpResponse("Error occurred", status=405)

    def copy_files(self, source, destination):
        # Copy the uploaded file to the specified destination
        if not os.path.isdir(os.path.dirname(destination)):
            os.makedirs(os.path.dirname(destination))
        abs_source = os.path.join(BASE_DIR, source)
        try:
            shutil.copy(abs_source, destination)
        except Exception as e:
            return False
        return True

# View to process and temporarily save an image
class ImageProcessing(LoginRequiredMixin, TemplateView):
    def get(self, request):
        user_id = request.user.id
        effect_name = request.GET.get('effect', '').replace(u'\xa0', '')
        image_path = request.GET.get('path', '')
        image_name = os.path.basename(image_path)
        image_base_name, image_extension = os.path.splitext(image_name)
        unique_filename = f"{request.user.username}_{int(time.time())}{image_extension}"
        output = os.path.join(BASE_DIR, MEDIA_URL, 'CACHE/temp', str(user_id))

        if not os.path.exists(output):
            os.makedirs(output)

        temp_image_location = os.path.join(output, unique_filename)
        image = Image.open(os.path.join(BASE_DIR, image_path))
        final_image = effect.get(effect_name, lambda x: x)(image)
        housekeeping(output)
        final_image.save(temp_image_location, 'PNG')

        image_url = os.path.join(MEDIA_URL, 'CACHE', 'temp', str(user_id), unique_filename)
        return HttpResponse(image_url)

# View to delete images and associated records
class DeleteImage(LoginRequiredMixin, TemplateView):
    def get(self, request, id):
        image = UploadImage.objects.get(id=id)
        if image:
            # Delete the selected image and return to the dashboard
            image.delete()
        return HttpResponseRedirect(reverse('main:home'))

from django.core.files.storage import default_storage

def delete_image_file(image_path):
    if default_storage.exists(image_path):
        default_storage.delete(image_path)

