import os
from PIL import Image, ImageFilter, ImageEnhance

def make_linear_ramp(white):
    ramp = []
    r, g, b = white
    for i in range(256):
        ramp.extend((int(r * i / 255), int(g * i / 255), int(b * i / 255)))
    return ramp

class ApplyEffects:
    def __init__(self, pil_image_path):
        self.pil_image_path = pil_image_path

    def apply_effect(self, effect):
        try:
            # Open the image file
            img = Image.open(self.pil_image_path)

            # Define the output path for the edited image
            base_path, ext = os.path.splitext(self.pil_image_path)
            edited_image_path = f"{base_path}_edited{ext}"

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
                img.save(edited_image_path, format='PNG', quality=100)
                return edited_image_path
            else:
                raise ValueError(f"Effect '{effect}' not supported.")
        except FileNotFoundError as e:
            print(f"Error: File not found at path: {self.pil_image_path}")
            raise e
        except Exception as e:
            print(f"Error: An unexpected error occurred: {str(e)}")
            raise e
