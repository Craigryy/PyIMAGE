from django.shortcuts import render, redirect, get_object_or_404
from .forms import ImageUploadForm
from .models import UploadedImage
from PIL import Image, ImageEnhance

def image_list(request):
    images = UploadedImage.objects.all()
    return render(request, 'processer/image_list.html', {'images': images})

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

def edit_image(request, image_id):
    image = get_object_or_404(UploadedImage, pk=image_id)
    return render(request, 'processer/edit_image.html', {'image': image})

def apply_effect(request, image_id):
    image = get_object_or_404(UploadedImage, pk=image_id)
    effect = request.POST.get('effect')
    if effect == 'brightness':
        image = apply_brightness_effect(image)
    # Add more effects as needed
    image.save()
    return redirect('image_list')

def apply_brightness_effect(image):
    img = Image.open(image.image.path)
    enhancer = ImageEnhance.Brightness(img)
    enhanced_img = enhancer.enhance(1.5)  # Increase brightness by 50%
    image.image = enhanced_img
    return image
