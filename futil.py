# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 16:45:45 2021

@author: marcu
"""
from PIL import Image

def pad_image_with_transparency(image, pixels, keep_size = False):
    """
    Pad around the outside of an image with the specified transparent
    pixels on each side. Option to keep the final image the same size
    as the original, or increase according to padding
    """
    image = image.convert('RGBA')
    width, height = image.size

    if keep_size:
        """ height/width of the final image is the same as the original.
        The original image is resized to the original minus the specified
        padding amount on each side """
        pad_width, pad_height = width - pixels*2, height - pixels*2
        new_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        image = image.resize((pad_width, pad_height),
                             resample=Image.ANTIALIAS)
    else:
        """ new height/width is the original plus the specified padding
        amount on each side """
        pad_width, pad_height = width + pixels*2, height + pixels*2
        new_image = Image.new('RGBA', (pad_width, pad_height), (0, 0, 0, 0))

    # paste the original image into the centre
    new_image.paste(image, (pixels, pixels))
    return new_image