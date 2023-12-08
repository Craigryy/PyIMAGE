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
        userid = self.request.user.id
        context = super().get_context_data(**kwargs)
        # Prepare the context for rendering the dashboard
        context['form'] = UploadImageForm()
        context['images'] = UploadImage.objects.filter(user_id=userid, edited=0)
        context['processed_images'] = UploadImage.objects.filter(user_id=userid, edited=1)
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



class DeleteImage(LoginRequiredMixin, TemplateView):
    """Deletes Photos and records."""

    def get(self, request, id):
        """Delete record and images."""
        image = UploadImage.objects.get(id=id)
        if image:
            return HttpResponse(image.delete())
        return HttpResponse(image.delete())



class ImageProcessingView(View):

    template_name = 'main/index.html' 

    def get(self, request, *args, **kwargs):
        form = UploadImageForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UploadImageForm(request.POST, request.FILES)

        if form.is_valid():
            # Save the uploaded image
            uploaded_image = form.save()

            # Get the path of the uploaded image
            image_path = uploaded_image.image.path

            # Get the selected effect from the form
            effect = request.POST.get('effect')  # Use get() to avoid KeyError if 'effect' is not in POST data

            try:
                # Create an instance of ApplyEffects with the image path
                apply_effects_instance = ApplyEffects(image_path)

                # Apply the specified effect
                edited_image_path = apply_effects_instance.apply_effect(effect)

                # Get the relative path from the base directory
                relative_path = os.path.relpath(edited_image_path, settings.BASE_DIR)

                # Set the 'edited' flag and save the model
                uploaded_image.edited = True  # Fix the variable name here
                uploaded_image.save()

                # Return the relative path in the HTTP response
                return HttpResponse('success', content_type="text/plain")

            except FileNotFoundError as e:
                return HttpResponse(f"Error: File not found at path: {image_path}", status=404)

            except ValueError as e:
                return HttpResponse(f"Error: {str(e)}", status=400)

            except Exception as e:
                return HttpResponse(f"Error: An unexpected error occurred: {str(e)}", status=500)

        return HttpResponse("Invalid form data", status=400)

class SaveProcessedImage(TemplateView, LoginRequiredMixin):

    '''Class used to view uploaded photos.'''

    template_name = 'main/index.html'

    def get(self, request, *args, **kwargs):

        userid = self.request.user.id

        context = self.get_context_data(**kwargs)
        context['images'] = UploadImage.objects.filter(user_id=userid)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):

        imageForm = UploadImageForm(request.POST, request.FILES)

        if imageForm.files['image'].size > settings.MAX_UPLOAD_SIZE:
            return HttpResponseNotAllowed('largefile')

        try:
            img = imageForm.save(commit=False)
            img.user = request.user
            img.save()
            return HttpResponse("success", content_type="text/plain")

        except:
            return HttpResponseBadRequest('Unknownerror')

