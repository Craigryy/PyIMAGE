from PIL import Image, ImageFilter, ImageEnhance
import os

def make_linear_ramp(white):
    '''Create a linear ramp.'''
    ramp = []
    r, g, b = white
    for i in range(255):
        ramp.extend((r * i // 255, g * i // 255, b * i // 255))
    return ramp

class ApplyEffects:
    '''Apply various image effects to an image.'''

    @staticmethod
    def get_effect_names():
        '''Return a list of available effect names.'''
        return [
            'brightness', 'grayscale', 'blackwhite', 'sepia',
            'contrast', 'blur', 'findedges', 'bigenhance',
            'enhance', 'smooth', 'emboss', 'contour', 'sharpen'
        ]

    @staticmethod
    def apply_effect(edited_image, effect):
        '''Apply the specified effect to the image.'''
        # Output edited image path
        filepath, ext = os.path.splitext(edited_image)
        edit_path = f"{filepath}_edited{ext}"

        # Dictionary to map effect names to corresponding functions
        effects = {
            'brightness': ApplyEffects.apply_brightness,
            'grayscale': ApplyEffects.apply_grayscale,
            'blackwhite': ApplyEffects.apply_black_white,
            'sepia': ApplyEffects.apply_sepia,
            'contrast': ApplyEffects.apply_contrast,
            'blur': ApplyEffects.apply_blur,
            'findedges': ApplyEffects.apply_find_edges,
            'bigenhance': ApplyEffects.apply_edge_enhance_more,
            'enhance': ApplyEffects.apply_edge_enhance,
            'smooth': ApplyEffects.apply_smooth_more,
            'emboss': ApplyEffects.apply_emboss,
            'contour': ApplyEffects.apply_contour,
            'sharpen': ApplyEffects.apply_sharpen
        }

        # Check if the effect exists in the dictionary; if not, return
        if effect not in effects:
            return f"{effect} is not a supported effect."

        img = Image.open(edited_image)
        img = effects[effect](img)
        img.save(edit_path, format='PNG', quality=100)
        return f"Effect '{effect}' applied successfully."

    def apply_brightness(self, img):
        '''Apply brightness effect.'''
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(1.8)

    def apply_grayscale(self, img):
        '''Apply grayscale effect.'''
        return img.convert('L')

    def apply_black_white(self, img):
        '''Apply black and white effect.'''
        return img.convert('1')

    def apply_sepia(self, img):
        '''Apply sepia effect.'''
        serpia = make_linear_ramp((255, 240, 192))
        img = img.convert('L')
        img.putpalette(serpia)
        return img

    # Additional filter effects
    def apply_contrast(self, img):
        '''Apply contrast effect.'''
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(2.0)

    def apply_blur(self, img):
        '''Apply blur effect.'''
        return img.filter(ImageFilter.BLUR)

    def apply_find_edges(self, img):
        '''Apply find edges effect.'''
        return img.filter(ImageFilter.FIND_EDGES)

    def apply_edge_enhance_more(self, img):
        '''Apply edge enhancement effect.'''
        return img.filter(ImageFilter.EDGE_ENHANCE_MORE)

    def apply_edge_enhance(self, img):
        '''Apply edge enhancement effect.'''
        return img.filter(ImageFilter.EDGE_ENHANCE)

    def apply_smooth_more(self, img):
        '''Apply smooth more effect.'''
        return img.filter(ImageFilter.SMOOTH_MORE)

    def apply_emboss(self, img):
        '''Apply emboss effect.'''
        return img.filter(ImageFilter.EMBOSS)

    def apply_contour(self, img):
        '''Apply contour effect.'''
        return img.filter(ImageFilter.CONTOUR)

    def apply_sharpen(self, img):
        '''Apply sharpen effect.'''
        return img.filter(ImageFilter.SHARPEN)
