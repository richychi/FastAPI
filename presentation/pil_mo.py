from PIL import Image, ImageFilter
import configparser

conf=configparser.ConfigParser()
conf.read('config.ini')
server=conf["SERVER"]
output=server["OUTPUT_PATH"]

im = Image.open(output+"test.png")
print(im.size)
im.show()
im = im.rotate(45)
im.show()
im = im.filter(ImageFilter.BLUR)
im.show()
im.save('image/OIP3.png')