from __future__ import print_function
from PIL import Image
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from datetime import datetime
import os
import shutil
from .forms import UploadedImageForm
from .models import UploadedImage
from .effect import effect
from pyIMAGE.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR
from .clean import housekeeping
import random


def login_required_decorator(f):
    """
    Decorator for login required.
    """
    return method_decorator(login_required)(f)


class Effects(View):
    """
    Returns the available effects.
    """

    def get(self, request):
        """
        Returns all the effects available.
        """
        return JsonResponse({"effects": list(effect.keys())})


class Home(View):
    """
    Creates a dashboard and saves new upload.
    """

    @login_required_decorator
    def post(self, request):
        """
        Saves uploads and thumbnails.
        """
        form = UploadedImageForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.owner = request.user
            new_image.save()
            return redirect("main:home")
        return JsonResponse({"error": "Form is not valid"}, status=403)

    @login_required_decorator
    def get(self, request):
        """
        Handles dashboard output information.
        """
        form = UploadedImageForm()
        images = UploadedImage.objects.filter(owner=request.user)
        effects_list = list(effect.keys())
        return render(request, "main/home.html", {"form": form, "images": images, "effects": effects_list})


class SaveProcessedImage(View):
    """
    Saves processed images on demand.
    """

    @login_required_decorator
    def post(self, request):
        """
        Saves a processed image.
        """
        if request.POST.get("path"):
            today = datetime.now()
            today_path = today.strftime("%Y/%m/%d")
            path = request.POST.get("path")
            imagename = os.path.basename(path)
            # create relative
            media_path = os.path.join("proimage", today_path, imagename)
            # create media path to get image
            new_path = os.path.join(MEDIA_ROOT, media_path)
            # check if image has been copied
            path_ready = self.copyimages(path, new_path)
            if path_ready:
                new_image, created = UploadedImage.objects.update_or_create(
                    image=media_path, owner=request.user, edited=1
                )
                return redirect("main:home")
            return JsonResponse({"error": "Error occurred"}, status=405)

    def copyimages(self, source, destination):
        """
        Creates Folder and images.
        """
        if not os.path.isdir(os.path.dirname(destination)):
            os.mkdir(os.path.dirname(destination))
        abs_source = "{}{}".format(BASE_DIR, source)
        try:
            shutil.copy(abs_source, destination)
        except:
            return False
        return True


class ImageProcessing(View):
    """
    Processes an image and returns the route of the processed image.
    """

    @login_required_decorator
    def get(self, request):
        """
        Processes and temporarily saves an image.
        """
        user_id = request.user.id
        string = request.GET.get("effect")
        path = request.GET.get(r"path")
        add_effect = string.replace(u"\xa0", "")
        image_name = os.path.basename(path)
        image, ext = os.path.splitext(image_name)
        # add random number to image to make it unique
        rand = random.randint(0, 100)
        image = Image.open("{}{}".format(BASE_DIR, path))
        # create absolute path for folder creation
        output = "{}{}{}{}".format(BASE_DIR, MEDIA_URL, "CACHE/temp/", user_id)
        if not os.path.exists(output):
            os.makedirs(output)
        # set path to save processed image
        temp_image_location = "{}{}.PNG".format(rand, image)
        # set route for exclusive thumbnails
        if request.GET.get("preview"):
            temp_image_location = "thumbnails/{}.PNG".format(add_effect)
        temp_image = os.path.join(output, temp_image_location)
        if not os.path.isdir(os.path.dirname(temp_image)):
            os.makedirs(os.path.dirname(temp_image))
        final_image = effect[add_effect](image)
        housekeeping(output)
        final_image.save(temp_image, "PNG")
        image_url = os.path.join(MEDIA_URL, "CACHE", "temp", str(user_id), temp_image_location)
        return JsonResponse({"image_url": image_url})


class DeleteImage(View):
    """
    Deletes Photos and records.
    """

    @login_required_decorator
    def get(self, request, id):
        """
        Deletes record and images.
        """
        try:
            image = UploadedImage.objects.get(id=id)
            image.delete()
            return JsonResponse({"message": "Image deleted successfully"})
        except UploadedImage.DoesNotExist:
            return JsonResponse({"error": "Image not found"}, status=404)
