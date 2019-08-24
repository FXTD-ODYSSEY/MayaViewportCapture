from maya.api import OpenMaya as om2
import os

# NOTE https://forums.autodesk.com/t5/maya-programming/write-image/td-p/7978803

DIR = os.path.dirname(__file__)
output = os.path.join(DIR,"redX.png")

# Create a buffer large enough to hold a 32x32 pixel RGBA image.
pixels = bytearray(32*32*4)

# Draw a red X into the buffer.
for i in range(0, 32):
    startOfRow = i * 32 * 4
    leftPixel = startOfRow + (31 - i) * 4
    rightPixel = startOfRow + i * 4

    # The buffer will have been initialized to all zeros so we
    # only need to fill in the Red and Alpha bytes of each pixel.
    pixels[leftPixel+0] = 255
    pixels[leftPixel+3] = 255

    pixels[rightPixel+0] = 255
    pixels[rightPixel+3] = 255

    if i == 3:
        break

img = om2.MImage()
img.setPixels(pixels, 32, 32)
img.writeToFile(output, 'png')


