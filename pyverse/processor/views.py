from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from datetime import datetime
import os
import shutil
from .forms import UploadedImageForm
from .models import UploadedImage
from .effects import effect
from pyIMAGE.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR
from .clean import housekeeping
import random
from django.shortcuts import redirect
from allauth.account.views import LoginView, LogoutView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def login_required_decorator(f):
    """
    Decorator for login required.
    """
    return method_decorator(login_required)(f)

class EffectsView(view):
    """
    List all effects.
    """
    def get(self,request):
        return JsonResponse({"effects :" list(effect.keys())})

class Home(View):

    @login_required_decorator
    def get(self, request):
        """
        Home page view for authenticated users.
        """
        return redirect('home')


@login_required
def dashboard(request):
    """
    Dashboard view for authenticated users.
    Perform actions related to saving uploads and thumbnails,
    and display dashboard information.
    """
    # Example: Save uploads and thumbnails
    if request.method == 'POST':
        form = UploadedImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded image and create a thumbnail
            uploaded_image = form.save(commit=False)
            uploaded_image.user = request.user
            uploaded_image.save()
            # Create thumbnail using PIL (Pillow) library
            thumbnail = create_thumbnail(uploaded_image.image)
            # Save the thumbnail
            thumbnail_path = os.path.join(MEDIA_ROOT, 'thumbnails', thumbnail.filename)
            thumbnail.save(thumbnail_path)

            # Redirect or render a response as needed

    else:
        form = UploadedImageForm()

    # Example: Display dashboard information
    dashboard_info = {
        'total_uploads': UploadedImage.objects.filter(user=request.user).count(),
      
    }

    return render(request, 'dashboard.html', {'form': form, 'dashboard_info': dashboard_info})


def create_thumbnail(image):
    """
    Function to create a thumbnail using Pillow (PIL).
    Modify this according to your actual thumbnail creation logic.
    """
    thumbnail_size = (100, 100)
    thumbnail = image.copy()
    thumbnail.thumbnail(thumbnail_size)
    return thumbnail



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
        effect_name = request.GET.get("effect", "").replace(u"\xa0", "")
        image_path = request.GET.get("path", "")
        # Extract the image name and extension
        image_name = os.path.basename(image_path)
        image_base_name, image_extension = os.path.splitext(image_name)
        # Generate a unique filename using username and timestamp
        unique_filename = f"{request.user.username}_{int(time.time())}{image_extension}"
        # Set the output directory based on user ID
        output = os.path.join(BASE_DIR, MEDIA_URL, "CACHE/temp", str(user_id))
        if not os.path.exists(output):
            os.makedirs(output)
        # Set the path to save the processed image
        temp_image_location = os.path.join(output, unique_filename)
        # Open the image using Pillow (PIL)
        image = Image.open(os.path.join(BASE_DIR, image_path))
        # Apply the specified image processing effect
        final_image = effect.get(effect_name, lambda x: x)(image)
        # Perform housekeeping (not shown in the provided code)
        housekeeping(output)
        # Save the final processed image
        final_image.save(temp_image_location, "PNG")
        # Create the URL for the processed image
        image_url = os.path.join(MEDIA_URL, "CACHE", "temp", str(user_id), unique_filename)
        # Return the URL of the processed image
        return JsonResponse({"image_url": image_url})


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
            # extract the image path and the image name from the POST parameters.
            path = request.POST.get("path")
            imagename = os.path.basename(path)
            # create a relative/ temp path to save
            media_path = os.path.join("profile", today_path, imagename) 
            # create a finitive media path to get image 
            new_path = os.path.join(MEDIA_ROOT, media_path)
            # check if image has been copied
            path_ready = self.copyimages(path, new_path)
            if path_ready:
                new_image, created = UploadedImage.objects.update_or_create(
                    image=media_path, user=request.user, edited=1
                )
                return redirect("main:home")
            return JsonResponse({"error": "Error occurred"}, status=405)

    def copyimages(self, source, destination):
        """
        Creates Folder and images.
        """
        if not os.path.isdir(os.path.dirname(destination)):
            os.mkdir(os.path.dirname(destination))
        # create a absolute source path by combining the base directory and the source path.
        abs_source = "{}{}".format(BASE_DIR, source)
        try:
            shutil.copy(abs_source, destination)
        except:
            return False
        return True
