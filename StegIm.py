"""
StegIm is a steganography program that allows for hiding data in images with out any noticeable change in the images. It works by "hiding" bits in an image through changing the rgbt values to be either even or odd.

Note that this program is rather primitive and likely has a number of bugs. This was done as a 1 hour hack as part of a larger different project. Also, note that ANY compression of the photo will lead to dataloss. 
"""
from PIL import Image

"""
Takes a PIL image and makes all values even (if odd: val -=1)
"""
def makeImageEven(image):
    pixels = list(image.getdata())  # get a list of the form [(r,g,b,t),(r,g,b,t)...]
    evenPixels = [(r>>1<<1,g>>1<<1,b>>1<<1,t>>1<<1) for [r,g,b,t] in pixels]  # make all of the values even (magic bit shifting!)
    evenImage = Image.new(image.mode, image.size)  # create the new image of the same size
    evenImage.putdata(evenPixels)  # put the pixels from above into the new image
    return evenImage

"""
A replacement for the built-in bin() function but it outputs a constant length string
"""
def constLenBin(int):
    binary = "0"*(8-(len(bin(int))-2))+bin(int).replace('0b','')  # magic to strip the 0b and prepend 0 until the length is 8
    return binary

"""
Takes a PIL image and encodes a string into the image.
"""
def encodeDataInImage(image, data):
    evenImage = makeImageEven(image)  # makes an even image from the one it was given
    binary = ''.join(map(constLenBin,bytearray(bytes(data, 'utf-8'))))  # create a string of binary using some bytearray and map magic
    if len(binary) > len(image.getdata()) * 4:  # if it is impossible to encode all the data, throw an exception
        raise Exception("Error: Can't encode more than " + len(evenImage.getdata()) * 4 + " bits in this image. ")
    encodedPixels = [(r+int(binary[index*4+0]),g+int(binary[index*4+1]),b+int(binary[index*4+2]),t+int(binary[index*4+3])) if index*4 < len(binary) else (r,g,b,t) for index,(r,g,b,t) in enumerate(list(evenImage.getdata()))]  # magic list comprehension that encodes the data. Basic algorithm is that for the nth value in the image (going r1, g1, b1, t1, r2, g2, b2, t2, r3...) the nth binary bit is added to it.
    encodedImage = Image.new(evenImage.mode, evenImage.size)  # create a new image to hold the encoded image
    encodedImage.putdata(encodedPixels)  # add the encoded pixels
    return encodedImage

"""
Takes a string of 0 and 1 and converts it to ASCII
"""
def binaryToString(binary):
    string = [chr(int(bin,2)) for bin in [binary[i:i+8] for i in range(0, len(binary), 8)]]
    return ''.join(string)

"""
Takes a PIL image that was created with encodeDataInImage and returns the data that was hidden in it.
"""
def decodeImage(image):
    pixels = list(image.getdata())  # get the list of pixels
    binary = ''.join([str(int(r>>1<<1!=r))+str(int(g>>1<<1!=g))+str(int(b>>1<<1!=b))+str(int(t>>1<<1!=t)) for (r,g,b,t) in pixels])  # another magic list comprehension. This one creates a string of 0 and 1 that can then be converted back into the original data. Does so by comparing the rounded value to the original value for each value in the pixel. If they don't equal, then a bit was stored there. 
    locationDoubleNull = binary.find('0000000000000000')  # find the location of the first double null (aka the first time no data was encoded in the image)
    endIndex = locationDoubleNull+(8-(locationDoubleNull % 8)) if locationDoubleNull%8 != 0 else locationDoubleNull  # magic to find the end index that we use when extracting the original data. Basic idea is that it must be a multiple of 8 so add (8-locationDoubleNull%8) to locationDoubleNull unless locationDoubleNull%8==0
    data = binaryToString(binary[0:endIndex])  # extract the data
    return data

encodedImage = encodeDataInImage(Image.open('/home/david/Downloads/tree.png'), 'Hello world!!!')  # encode "Hello World!!!" in tree.png
print(''.join(decodeImage(encodedImage)))  # extract the data fronm the above image
