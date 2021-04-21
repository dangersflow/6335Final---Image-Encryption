#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cryptography.fernet import Fernet
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import math
import time

key = Fernet.generate_key()

with open('secret.key', 'wb') as new_key_file:
    new_key_file.write(key)

print("\nKey: " + str(key) + "\n")

input_image = "testimg.jpg"

with Image.open("./"+input_image) as image:
    arr = np.array(image)
    shape = arr.shape
    datatype = arr.dtype.name
    msg = arr.tobytes()
    d1 = ImageDraw.Draw(image)
    d1.text((28,36), "Original Image", font=ImageFont.truetype(font="Keyboard.ttf", size=40), fill=(255,0,0))
    print("Original Image: \t./"+input_image+"\n")
    image.show()

f = Fernet(key)

timer1 = time.time()
cyphertext = f.encrypt(msg)
enc_time = time.time() - timer1
print("Time to encrypt: "+str(round(enc_time, 4))+" seconds\n")

c_size = len(cyphertext)
c_pixels = int((c_size+2)/3)
W = H = int(math.ceil(c_pixels ** 0.5))

img_data = cyphertext + b'\0' * (W*H*3 - len(cyphertext))

with Image.frombytes('RGB', (W, H), img_data) as cypherpic:
    d2 = ImageDraw.Draw(cypherpic)
    d2.text((28,36), "Encrypted Image", font=ImageFont.truetype(font="Keyboard.ttf", size=40), fill=(255,0,0))
    c_name = "encrypted_img.jpg"
    cypherpic.show()
    cypherpic.save(c_name)
    print("Encrypted Image:\t./"+c_name+"\n")

timer2 = time.time()
cleartext = f.decrypt(cyphertext)
dec_time = time.time() - timer2
print("Time to decrypt: "+str(round(dec_time, 4))+" seconds\n")


if cleartext == msg:
    print("It Worked!\n")
    output = Image.fromarray(np.frombuffer(cleartext, dtype=datatype).reshape(shape))
    o_name = "output_img.jpg"
    d3 = ImageDraw.Draw(output)
    d3.text((28,36), "Decrypted Image", font=ImageFont.truetype(font="Keyboard.ttf", size=40), fill=(255,0,0))
    output.show()
    output.save(o_name)
    print("Decrypted Image:\t./"+o_name+"\n")
else:
    print("FAIL.\n")


