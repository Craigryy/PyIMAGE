from django.shortcuts import render, redirect, get_object_or_404
from .forms import ImageUploadForm
from .models import UploadedImage
from PIL import Image, ImageEnhance
from django.contrib.auth.decorators import login_required

# View to list all uploaded images
def image_list(request):
    images = UploadedImage.objects.all()
    return render(request, 'processer/image_list.html', {'images': images})

# View to handle image upload
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = request.user
            image.save()
            return redirect('image_list')
    else:
        form = ImageUploadForm()
    return render(request, 'processer/upload_image.html', {'form': form})

# View to edit an image
def edit_image(request, image_id):
    image = get_object_or_404(UploadedImage, pk=image_id)

    if request.method == 'POST':
        effect = request.POST.get('effect')
        if effect == 'brightness':
            image = apply_brightness_effect(image)
        # Add more effects as needed
        image.save()
        return redirect('image_list')

    return render(request, 'processer/edit_image.html', {'image': image})

# View to apply an effect to an image
def apply_effect(request, image_id):
    image = get_object_or_404(UploadedImage, pk=image_id)
    effect = request.POST.get('effect')
    if effect == 'brightness':
        image = apply_brightness_effect(image)
    # Add more effects as needed
    image.save()
    return redirect('image_list')

# Function to apply brightness effect to an image
def apply_brightness_effect(image):
    img = Image.open(image.image.path)
    enhancer = ImageEnhance.Brightness(img)
    enhanced_img = enhancer.enhance(1.5)  # Increase brightness by 50%
    image.image = enhanced_img
    return image

# View to display the user's profile and their uploaded images
@login_required
def user_profile(request):
    user_images = UploadedImage.objects.filter(user=request.user)
    return render(request, 'processer/user_profile.html', {'images': user_images})
