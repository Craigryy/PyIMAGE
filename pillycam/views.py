# from PIL import Image
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.http import HttpResponseRedirect, HttpResponse
# from django.views.generic.base import TemplateView
# from django.urls import reverse
# from django.shortcuts import render
# from datetime import datetime
# import os
# import shutil
# from .forms import UploadImageForm
# from .models import UploadImage
# from .effects import effect
# from pills.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR
# from .clean import housekeeping
# import random

# # View to display available image effects
# class EffectsView(TemplateView):
#     template_name = "effects.html"

#     def get(self, request, *args, **kwargs):
#         # Get a list of available effects and render them
#         effect_names = list(effect.keys())
#         return self.render_to_response({'effects': effect_names})

# # Main dashboard view with file upload functionality
# class Home(LoginRequiredMixin, TemplateView):
#     login_url = 'account_login'
#     template_name = 'main/index.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Prepare the context for rendering the dashboard
#         context['form'] = UploadImageForm()
#         context['images'] = UploadImage.objects.filter(user=self.request.user)
#         context['effects'] = effect.keys()
#         return context

#     def post(self, request):
#         form = UploadImageForm(request.POST, request.FILES)
#         if form.is_valid():
#             # Save the uploaded image and redirect to the dashboard
#             new_image = UploadImage(image=request.FILES['image'], user=request.user)
#             new_image.save()
#             return HttpResponseRedirect(reverse('main:home'))
#         return HttpResponse("Error", status=403)

# # View to save a processed image
# class SaveProcessedImage(LoginRequiredMixin, TemplateView):
#     login_url = 'account_login'
#     template_name = 'main/index.html'

#     def post(self, request):
#         if request.POST.get('path'):
#             today = datetime.now()
#             today_path = today.strftime("%Y/%m/%d")
#             path = request.POST.get('path')
#             imagename = os.path.basename(path)
#             media_path = os.path.join('profile', today_path, imagename)
#             new_path = os.path.join(MEDIA_ROOT, media_path)
#             path_ready = self.copy_files(path, new_path)

#             if path_ready:
#                 # Update or create a record of the processed image and return to the dashboard
#                 UploadImage.objects.update_or_create(image=media_path, user=request.user, edited=1)
#                 return HttpResponseRedirect(reverse('main:home'))
#             return HttpResponse("Error occurred", status=405)

#     def copy_files(self, source, destination):
#         # Copy the uploaded file to the specified destination
#         if not os.path.isdir(os.path.dirname(destination)):
#             os.makedirs(os.path.dirname(destination))
#         abs_source = os.path.join(BASE_DIR, source)
#         try:
#             shutil.copy(abs_source, destination)
#         except Exception as e:
#             return False
#         return True

# # View to process and temporarily save an image
# class ImageProcessing(LoginRequiredMixin, TemplateView):
#     def get(self, request):
#         user_id = request.user.id
#         effect_name = request.GET.get('effect', '').replace(u'\xa0', '')
#         image_path = request.GET.get('path', '')
#         image_name = os.path.basename(image_path)
#         image_base_name, image_extension = os.path.splitext(image_name)
#         unique_filename = f"{request.user.username}_{int(time.time())}{image_extension}"
#         output = os.path.join(BASE_DIR, MEDIA_URL, 'CACHE/temp', str(user_id))

#         if not os.path.exists(output):
#             os.makedirs(output)

#         temp_image_location = os.path.join(output, unique_filename)
#         image = Image.open(os.path.join(BASE_DIR, image_path))
#         final_image = effect.get(effect_name, lambda x: x)(image)
#         housekeeping(output)
#         final_image.save(temp_image_location, 'PNG')

#         image_url = os.path.join(MEDIA_URL, 'CACHE', 'temp', str(user_id), unique_filename)
#         return HttpResponse(image_url)

# # View to delete images and associated records
# class DeleteImage(LoginRequiredMixin, TemplateView):
#     def get(self, request, id):
#         image = UploadImage.objects.get(id=id)
#         if image:
#             # Delete the selected image and return to the dashboard
#             image.delete()
#         return HttpResponseRedirect(reverse('main:home'))

# from django.core.files.storage import default_storage

# def delete_image_file(image_path):
#     if default_storage.exists(image_path):
#         default_storage.delete(image_path)




from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from .models import UploadImage
from .forms import UploadImageForm
from .effects import applyEffects
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

# Main dashboard view with file upload functionality
class HomeView(LoginRequiredMixin, TemplateView):
    login_url = 'account_login'
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Prepare the context for rendering the dashboard
        context['form'] = UploadImageForm()
        context['images'] = UploadImage.objects.filter(user=self.request.user)
       
        return context

    def post(self, request):
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded image and redirect to the dashboard
            new_image = UploadImage(image=request.FILES['image'], user=request.user)
            new_image.save()
            return HttpResponseRedirect(reverse('main:home'))
        return HttpResponse("Error", status=403)


class UploadImageView(TemplateView, LoginRequiredMixin):
    template_name = 'main/home.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response()

    def post(self, request, *args, **kwargs):
        uploadImageform = UploadImageForm(request.POST, request.FILES)

        if uploadImageform.files['image'].size > settings.MAX_UPLOAD_SIZE:
            return HttpResponse(status=413)  # Payload Too Large

        try:
            img = UploadImageForm.save(commit=False)
            img.user = request.user
            img.save()
            return HttpResponseRedirect(reverse_lazy('main:home'))
        except:
            return HttpResponse(status=500)  # Internal Server Error

from django.http import HttpResponseNotAllowed, HttpResponseBadRequest

class ViewUploadedPicturesView(TemplateView, LoginRequiredMixin):
    template_name = 'main/dashboard.html'

    def get(self, request, *args, **kwargs):
        userid = self.request.user.id
        context = self.get_context_data(**kwargs)
        context['images'] = UploadImage.objects.filter(user_id=userid)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        photoform = UploadImageForm(request.POST, request.FILES)

        if photoform.files['image'].size > settings.MAX_UPLOAD_SIZE:
            return HttpResponseNotAllowed('largefile')

        try:
            img = photoform.save(commit=False)
            img.user = request.user
            img.save()
            return HttpResponse("success", content_type="text/plain")
        except:
            return HttpResponseBadRequest('Unknownerror')


class DeleteAllPhotosView(View, LoginRequiredMixin):
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
      

class ApplyFilterView(TemplateView, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        image_id = request.GET.get('image_id')
        effect = request.GET.get('effect')

        image = UploadImage.objects.get(id=image_id)

        # Assuming you have a path to the original image file
        original_image_path = image.image.path

        # Apply the selected effect
        apply_effects = Applyeffects(original_image_path)
        apply_effects.effect(effect)

        # Assuming you have a path to the edited image file
        edited_image_path = original_image_path.replace('profile/', 'profile/edited/')

        # Save the edited image path to the model
        image.image = edited_image_path
        image.edited = 1
        image.save()

        return redirect('main:view_uploaded_pictures')
