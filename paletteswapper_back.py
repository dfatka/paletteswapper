try:
    from numba import jit
    using_numba = True
except ModuleNotFoundError:
    print('Module numba not found. Proceeding without, probably slower.')
    using_numba = False
    def jit(stuff):
        """Blank placeholder decorator for numba JIT, used in the absence of numba."""
        return stuff

import numpy as np
from PIL import Image

def pil_analysis(pilimg):
    """Take image as a PIL Image object, return its palette in a dictionary of the form
    tuple(color):list(color) for further editing of the palette."""
    return palette_analysis(np.array(pilimg))


def img_dimensions(img):
    """Return dimensions of an image in numpz array form. Most of the times, equivalent to np.shape(img)."""
    try:
        width, height, channels = np.shape(img)
    except ValueError:
        width, height = np.shape(img)
        channels = 1
    return (width, height, channels)


def flat_img(img, dims=None):
    """Return the image flattened, i.e. a 2-dimensional array, where the second dimension maps only colors."""
    if dims == None:
        dims = img_dimensions(img)
    return np.reshape(img, (dims[0]*dims[1], dims[2]))

@jit
def make_palette(flatimg):
    """Return all the colors in a flattened image."""
    return np.unique(flatimg, axis=0)

def dict_palette(palette):
    """Take the palette as in the output of make_palette, return them in a dictionary of the form
    tuple(color):list(color) for further editing of the palette."""
    return {tuple(col) : list(col) for col in palette}

def palette_analysis(img):
    """Take image, return its palette in a dictionary of the form
    tuple(color):list(color) for further editing of the palette."""
    return dict_palette(make_palette(flat_img(img)))

def crude_remappers(flatimg, dictpalette):
    """Not to be used alone, responsible for internal transformation. Dict comprehension just extracted to allow JITting
    of the rest with numba."""
    return {tuple(dictpalette[col]): flatimg == np.array(col) for col in dictpalette.keys()}

@jit
def cleared_remappers(crudemap):
    """Return a Boolean array where each color now belongs."""
    for col in crudemap.keys():
        crudemap[col] = np.all(crudemap[col], axis=1)
    return crudemap

@jit
def remap(flatimg, clearmap):
    """Return a flattened form of an image after palette swap according to the mapping generated by cleared_remappers."""
    for col in clearmap.keys():
        flatimg[clearmap[col]] = np.array(col)
    return flatimg

def paletteswap_flat(flatimg, dictpalette):
    """Return a flattened image according to the dictionary of old and new palette as made by palette_analysis."""
    return remap(flatimg, cleared_remappers(crude_remappers(flatimg, dictpalette)))

def paletteswap(img, dictpalette):
    """Return an array representing an image with palette-swapped colors. Takes the original image in an array
    representation and a dictionary like one generated from palette_analysis, just with changed colors."""
    return np.reshape(paletteswap_flat(flat_img(img), dictpalette), img_dimensions(img))

def fullswap(pilimg, dictpalette):
    """Return a PIL Image object from taken PIL Image object and the
     dictionary of a palette (palette like the one generated from pil_analysis]."""
    return Image.fromarray(paletteswap(np.array(pilimg), dictpalette))
