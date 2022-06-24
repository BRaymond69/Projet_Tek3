#!/bin/python3

from sys import argv
from PIL import Image
import numpy as np
import os
from more_itertools import partition

def usage():
    print("""USAGE
    ./preprocess.py img1.png [img2.png img3.png ...] [-d=] [-v]

DESCRIPTION
    imgX.png    image of a funiture you want to prepare for the ai to handle
    -d=         set the dimentions of the image (default 64)
    -v          visualize the output image
""")

def get_args():
    if "-h" in argv or len(argv) < 2:
        usage()
        exit(0)
    return argv[1:]

def process(image_path, dimentions=64, visualisation=False):
    img = Image.open(image_path).resize((dimentions, dimentions), Image.ANTIALIAS)
    pixels = [[[(int(r) + int(g) + int(b)) / 3] * 3 for r, g, b, *_ in list(y)] for y in np.array(img)]
    out = Image.fromarray(np.array(pixels, dtype=np.uint8))

    if "dataset/" in image_path:
        output_path = image_path.replace("dataset/", "training/")
    else:
        output_path = "out.jpg"

    out.save(output_path)
    img.close()

    if visualisation:
        out.show()

if __name__ == '__main__':
    images, flags = partition(lambda x: x.startswith("-"), get_args())
    images = list(images)
    flags = list(flags)

    if not os.path.isdir("training/"):
        os.mkdir("./training/")

    nbimages = len(images)
    dimentions = int(next((x for x in flags if x.startswith("-d=")), "-d=64")[3:])
    print("Generating images with size {}x{}".format(dimentions, dimentions))
    for i, img in enumerate(images):
        process(img, dimentions, "-v" in flags)
        print("Progress %i/%i (%.2f%%)" % (i, nbimages, i * 100 / nbimages), end='\r')
    print("Progress %i/%i (%.2f%%)" % (nbimages, nbimages, 100))
