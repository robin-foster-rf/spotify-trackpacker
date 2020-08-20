"""
art.py

manipulate cover art to create playlist cover images
"""
import requests
import os

from math import sqrt
from io import BytesIO
from base64 import b64encode
from PIL import Image, ImageDraw, ImageFilter

SPOTIFY_GREEN  = ( 30, 215,  96) 
INVERT_MAGENTA = (255,  40, 159) 
LOGO_MASK = 'app/logo_mask.png'


def open_image_from_url(url):
    r = requests.get(url)
    im = Image.open(BytesIO(r.content))
    return im


def img_to_b64string(image):
    buff = BytesIO()
    image.save(buff, format='JPEG')
    img_str = b64encode(buff.getvalue())
    return img_str


def composite_covers(images):
    # combine images in diagonal stripes
    images = [force_square(i) for i in images]
    n = len(images)

    imc = images[0]
    W, H = imc.size

    for i in range(1, n):
        mask = Image.new('L', imc.size, 0)
        draw = ImageDraw.Draw(mask)
        if i<=(n//2):
            # triangles from bottom left
            p = [(0, H), (2*i*W//n, H), (0, H-2*i*H//n), (0, H)]
        else:
            # pentagons from bottom left (complement of triangle from top right)
            p = [(0,H), (W,H), (W,(H-2*i*H//n)%H), ((2*i*W//n)%W, 0), (0,0), (0,H)]
        draw.polygon(p, fill=255)
        # mask = mask.filter(ImageFilter.GaussianBlur(1))
        imc = Image.composite(imc, images[i], mask)
    return imc


def force_square(image, res=300):
    # not all cover images returned by the api are square.
    # if the api says height=300 and width=300 then it looks like this actually
    # means that at least one of the height or width is 300px but the other 
    # could be less. 
    # here we resize the image so it is exactly square with desired size.
    min_px = min(image.size)
    image = image.resize((res, res), box=(0,0,min_px,min_px))
    return image


def stamp_logo(image):
    # overlay logo in triangle on top left corner
    W, H = image.size
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    p = [(0, 0), (0, H//2), (W//2, 0), (0, 0)] # triangle from top left
    draw.polygon(p, fill=255)

    logo_mask = Image.open(LOGO_MASK).convert(mode='L')
    blank_mask = Image.new('L', image.size, 0)
    mask = Image.composite(blank_mask, mask, logo_mask)

    block_colour = Image.new('RGB', image.size, INVERT_MAGENTA)
    imc = Image.composite(block_colour, image, mask)
    return imc


def create_cover(img_urls):
    imgs = [open_image_from_url(url) for url in img_urls]
    img = composite_covers(imgs)
    img = stamp_logo(img)
    return img_to_b64string(img)