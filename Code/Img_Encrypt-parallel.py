#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cryptography.fernet import Fernet
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import os
import glob
import math
import time
import progressbar
import threading
import random
import image_slicer
from image_slicer import join

# Get the number of CPUs
# in the system using
# os.cpu_count() method
cpuCount = os.cpu_count()

exitFlag = 0

# initialize lists to hold execution times of encryption and decryption
enc_times = []
dec_times = []
#have thread list
threads = []


#thread class
class encryptionThread (threading.Thread):
   def __init__(self, threadID, chunk, key, tile):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.chunk = chunk
      self.key = key
      self.tile = tile
   def run(self):
      print ("Starting encryption on chunk " + str(self.threadID) + "\n")
      encrypt_chunk(self.chunk, self.key, self.tile)
      print ("Finished encrypting chunk " + str(self.threadID) + "\n")

def create_image(cyphertext, tile, mode):
    if mode == 0:
        c_size = len(cyphertext)
        c_pixels = int((c_size+2)/3)
        W = H = int(math.ceil(c_pixels ** 0.5))

        data = cyphertext + b'\0' * (W*H*3 - len(cyphertext))
        cypherpic = Image.frombytes('RGB', (W, H), data)
        tile.image = cypherpic


def encrypt_chunk(msg, key, tile):
    # get the cyphertext and the execution time from the encryption function
    cyphertext, encryption_time = encrypt(msg, key)
    # append the execution time to the respective list
    enc_times.append(encryption_time)
    #create the image and modify the tile
    create_image(cyphertext, tile, 0)

def decrypt_chunk(msg, key, tile):
    # get the cleartext (decrypted bytearray/text) and the execution time from the decryption function
    cleartext, decryption_time = decrypt(msg, key)
    # append the execution time to the respective list
    dec_times.append(decryption_time)
    #create the image and modify the tile
    #Image.fromarray(np.frombuffer(b_text, dtype=i_data.datatype).reshape(i_data.shape))

#global path definitions
O_path = os.path.join("./", "Original_Images")
E_path = os.path.join("./", "Encrypted_Images")
D_path = os.path.join("./", "Decrypted_Images")

# Wrapper for PIL images 
class Image_Data:
    def __init__(self, image):
        self.image = image
        self.f_name = image.filename
        self.b_array = np.array(image).tobytes()
        self.shape = np.array(image).shape
        self.datatype = np.array(image).dtype.name

# Generate Image_Data list
def get_images(path):
    img_dir = path
    data_path = os.path.join(img_dir,'*g') 
    files = glob.glob(data_path) 
    img_arr = []

    # initialize a progress bar for loading images
    widgets = ['Loading Images: ', progressbar.Bar('█'),' (', progressbar.ETA(), ') ',]
    bar = progressbar.ProgressBar(28, widgets = widgets).start()
    i = 0

    # loop through the images and append the newly created PIL image to the Image_Data list
    for f in files:
        i += 1 
        img = Image.open(f)
        img_arr.append(Image_Data(img))
        bar.update(i)
    print("\n\n")

    return img_arr

# Fernent setup
def get_key():
    key = Fernet.generate_key()
    with open('secret.key', 'wb') as new_key_file:
        new_key_file.write(key)

    print("Key: " + str(key) + "\n")

    return Fernet(key)

# Create/Empty directories for the (marked) original images, encrypted images, and decrypted images
# Note that the images have the same original filenames to keep track
def setup_directories():
    if os.path.isdir(O_path):
        try:
            files = glob.glob(O_path+'/*')
            for f in files:
                os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (O_path, e.strerror))
    else:
        try:
            os.mkdir(O_path)
        except OSError as e:
            print("Error: %s : %s" % (O_path, e.strerror))

    if os.path.isdir(E_path):
        try:
            files = glob.glob(E_path+'/*')
            for f in files:
                os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (E_path, e.strerror))
    else:
        try:
            os.mkdir(E_path)
        except OSError as e:
            print("Error: %s : %s" % (E_path, e.strerror))

    if os.path.isdir(D_path):
        try:
            files = glob.glob(D_path+'/*')
            for f in files:
                os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (D_path, e.strerror))
    else:
        try:
            os.mkdir(D_path)
        except OSError as e:
            print("Error: %s : %s" % (D_path, e.strerror))

# Helper function for build_and_save()
# Write text on the images and save them to their respective directories
def label_and_save(image, label, filename, save_dir):
    d = ImageDraw.Draw(image)
    d.text((28,36), label, font=ImageFont.truetype(font="arial.ttf", size=40), fill=(255,0,0))
    #image.save(save_dir + "/" + filename.replace("./SmallSet_Images/", ''))
    image.save(save_dir + "/" + str(random.randint(1, 1000000)) + ".jpg")

# Create the images from the bytearray and save them to their respective directories for logging
def build_and_save(i_data, image, mode):
    if mode == 0: # encrypted image
        label_and_save(image, "Encrypted Image", i_data.f_name, E_path)
    elif mode == 1: #decrypted image
        #output = Image.fromarray(np.frombuffer(b_text, dtype=i_data.datatype).reshape(i_data.shape))
        label_and_save(image, "Decrypted Image", i_data.f_name, D_path)

# Encrypt plaintext and get execution time
def encrypt(message, F):
    timer1 = time.time()
    c_text = F.encrypt(message)
    extime = round(time.time() - timer1, 4)

    return c_text, extime

# Decrypt cyphertext and get execution time
def decrypt(cypher, F):
    timer2 = time.time()
    p_text = F.decrypt(cypher)
    extime = round(time.time() - timer2, 4)

    return p_text, extime

# print out the number of images used, and the average encryption and decryption times with a decimal precision of 4
def print_results(num_images, e_times, d_times):
    print("Number of images: "+str(num_images)+"\n")
    print("Average Encryption Time: "+str(round(np.mean(e_times), 4))+" seconds\n")
    print("Average Decryption Time: "+str(round(np.mean(d_times), 4))+" seconds\n")

# main driver code
def main():
    # Print the number of
    # CPUs in the system
    print("Number of CPUs in the system:", cpuCount)

    # for debugging use the small dataset
    images = get_images("./SmallSet_Images/")

    # uncomment the following line to do testing on larger dataset
    # images = get_images("./Sample_Images/")

    # if directories already exist, empty them, else create them
    setup_directories()

    # get the key
    k = get_key()

    # initialize progress bar
    widgets = ['Batch Encryption/Decryption: ', progressbar.Bar('█'),' (', progressbar.ETA(), ') ',]
    bar = progressbar.ProgressBar(28, widgets = widgets).start()
    t = 0

    # loop through loaded images and run encryption and decryption
    # timing information is gathered in the encrypt() and decrypt() functions
    for i in images:

        #slice up the image according to the number of cpu threads you have
        tiles = image_slicer.slice(i.f_name, cpuCount)

        t += 1

        # mark and save the input image to the respective directory
        label_and_save(i.image, "Original Image", i.f_name, O_path)

        for tile in tiles:
            # initialize message variable for input to encryption function (turn each tile into a byte array)
            msg = np.array(tile.image).tobytes()
            #create new thread & pass along the chunk with the key
            newThread = encryptionThread(tile.number, msg, k, tile)
            newThread.start()
            threads.append(newThread)
        
        #wait for all of the threads to finish their work
        print("Waiting for all the threads to finish...")
        for thread in threads:
            thread.join()

        # join all of the tiles and save it to its respective directory
        image = join(tiles)
        image.save(".\\Encrypted_Images\\" + str(random.randint(1, 1000000)) + ".png")
        #build_and_save(i, image, 0)

        
        # create an image from the cleartext and save it to its respective directory
        ##build_and_save(i, cleartext, 1)
        bar.update(t)
    print("\n\n")

    # output the results
    print_results(len(images), enc_times, dec_times)

if __name__ == '__main__':
    main()