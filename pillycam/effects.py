import os
from PIL import Image, ImageFilter, ImageEnhance

def make_linear_ramp(white):
    ramp = []
    r, g, b = white
    for i in range(256):
        ramp.extend((int(r * i / 255), int(g * i / 255), int(b * i / 255)))
    return ramp

class applyEffects:
    def __init__(self, pil_image):
        self.pil_image = pil_image

    def apply_effect(self, effect):
        img = Image.open(self.pil_image)
        edit_path = f"{os.path.splitext(self.pil_image)[0]}_edited.png"

        effects_map = {
            'brightness': lambda img: ImageEnhance.Brightness(img).enhance(1.8),
            'grayscale': lambda img: img.convert('L'),
            'blackwhite': lambda img: img.convert('1'),
            'sepia': lambda img: img.convert('L').putpalette(make_linear_ramp((255, 240, 192))),
            'contrast': lambda img: ImageEnhance.Contrast(img).enhance(2.0),
            'blur': lambda img: img.filter(ImageFilter.BLUR),
            'findedges': lambda img: img.filter(ImageFilter.FIND_EDGES),
            'bigenhance': lambda img: img.filter(ImageFilter.EDGE_ENHANCE_MORE),
            'enhance': lambda img: img.filter(ImageFilter.EDGE_ENHANCE),
            'smooth': lambda img: img.filter(ImageFilter.SMOOTH_MORE),
            'emboss': lambda img: img.filter(ImageFilter.EMBOSS),
            'contour': lambda img: img.filter(ImageFilter.CONTOUR),
            'sharpen': lambda img: img.filter(ImageFilter.SHARPEN),
            # Add more effects as needed
        }

        if effect in effects_map:
            img = effects_map[effect](img)
            img.save(edit_path, format='PNG', quality=100)
        else:
            print(f"Effect '{effect}' not supported.")


