from datetime import datetime
import os
from PIL import Image
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseServerError,
    HttpResponseNotAllowed,
    HttpResponseBadRequest,
)
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View
from .forms import UploadImageForm
from .models import UploadImage, UserProfile
from .effects import ApplyEffects
from pills.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR
from .clean import housekeeping
from django.conf import settings

# Remove duplicate and unused imports
from django.shortcuts import render
from django.views.generic.edit import DeleteView

def login_required_class(view_func):
    if hasattr(view_func, 'as_view'):
        view_func.dispatch = method_decorator(login_required)(view_func.dispatch)
    return view_func

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs
        )

class HomeView(TemplateView):
    login_url = 'account_login'
    template_name = 'main/index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('main:home'))
        else:
            return HttpResponse("Error", status=403)

@login_required_class
class PhotoAppView(TemplateView):
    template_name = 'main/pillycam.html'

    def get(self, request, *args, **kwargs):
        userid = self.request.user.id
        context = self.get_context_data(**kwargs)
        context['photos'] = UploadImage.objects.filter(user_id=userid)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        uploadform = UploadImageForm(request.POST, request.FILES)

        if uploadform.files['image'].size > settings.MAX_UPLOAD_SIZE:
            return HttpResponseNotAllowed('largefile')

        try:
            img = uploadform.save(commit=False)
            img.user = request.user
            img.save()
            return HttpResponse("success", content_type="text/plain")

        except Exception as e:
            return HttpResponseBadRequest(str(e))

@login_required_class
class DeletePhotoView(View):
    def get(self, request, *args, **kwargs):
        imageid = request.GET.get('id')
        try:
            image = UploadImage.objects.get(id=imageid)
        except UploadImage.DoesNotExist:
            raise Http404

        image.delete()

        return HttpResponse("success", content_type="text/plain")

class EffectImageView(TemplateView):
    template_name = 'main/effect_image.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['edited_image_path'] = self.apply_effect()
        return context

    def apply_effect(self):
        effect_image = str(self.request.GET.get('image'))
        effect = self.request.GET.get('effect')

        filepath, ext = os.path.splitext(effect_image)
        edit_path = filepath + 'edited' + ext

        image_effects = ApplyEffects(effect_image)
        image_effects.effect(effect)

        return os.path.relpath(edit_path, settings.BASE_DIR)

def custom_404(request, exception):
    return render(request, 'main/404.html', status=404)

def custom_500(request):
    return render(request, 'main/500.html', status=500)
