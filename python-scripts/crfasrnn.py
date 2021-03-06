# -*- coding: utf-8 -*-
"""
This package contains code for the "CRF-RNN" semantic image segmentation method, published in the
ICCV 2015 paper Conditional Random Fields as Recurrent Neural Networks. Our software is built on
top of the Caffe deep learning library.

Contact:
Shuai Zheng (szheng@robots.ox.ac.uk), Sadeep Jayasumana (sadeep@robots.ox.ac.uk), Bernardino Romera-Paredes (bernard@robots.ox.ac.uk)

Supervisor:
Philip Torr (philip.torr@eng.ox.ac.uk)

For more information about CRF-RNN, please vist the project website http://crfasrnn.torr.vision.
"""

caffe_root = '../caffe/'
import sys, getopt
sys.path.insert(0, caffe_root + 'python')

import os
import glob
import cPickle
import logging
import numpy as np
import pandas as pd
from PIL import Image as PILImage
#import Image
import cStringIO as StringIO
import caffe
import matplotlib.pyplot as plt


def tic():
    #http://stackoverflow.com/questions/5849800/tic-toc-functions-analog-in-python
    #Homemade version of matlab tic and toc functions
    import time
    global startTime_for_tictoc
    startTime_for_tictoc = time.time()

def toc():
    import time
    if 'startTime_for_tictoc' in globals():
        print "Elapsed time is " + str(time.time() - startTime_for_tictoc) + " seconds."
    else:
        print "Toc: start time not set"


def getpallete(num_cls):
        # this function is to get the colormap for visualizing the segmentation mask
        n = num_cls
        pallete = [0]*(n*3)
        for j in xrange(0,n):
                lab = j
                pallete[j*3+0] = 0
                pallete[j*3+1] = 0
                pallete[j*3+2] = 0
                i = 0
                while (lab > 0):
                        pallete[j*3+0] |= (((lab >> 0) & 1) << (7-i))
                        pallete[j*3+1] |= (((lab >> 1) & 1) << (7-i))
                        pallete[j*3+2] |= (((lab >> 2) & 1) << (7-i))
                        i = i + 1
                        lab >>= 3
        return pallete

def crfasrnn_segmenter(model_file, pretrained_file, gpudevice, inputs):
    if gpudevice >= 0:
        #Do you have GPU device? NO GPU is -1!
        has_gpu = 1
        #which gpu device is available?
        gpu_device=gpudevice#assume the first gpu device is available, e.g. Titan X
    else:
        has_gpu = 0
    if has_gpu==1:
        caffe.set_device(gpu_device)
        caffe.set_mode_gpu()
    else:
        caffe.set_mode_cpu()


    net = caffe.Net(model_file, pretrained_file, caffe.TEST)

    input_ = np.zeros((len(inputs),
        500, 500, inputs[0].shape[2]),
        dtype=np.float32)
    for ix, in_ in enumerate(inputs):
        input_[ix] = in_

    # Segment
    caffe_in = np.zeros(np.array(input_.shape)[[0,3,1,2]],
                        dtype=np.float32)
    for ix, in_ in enumerate(input_):
        caffe_in[ix] = in_.transpose((2, 0, 1))
    tic()
    out = net.forward_all(**{net.inputs[0]: caffe_in})
    toc()
    predictions = out[net.outputs[0]]

    return predictions[0].argmax(axis=0).astype(np.uint8)

def run_crfasrnn(inputfile, outputfile, gpudevice):
    MODEL_FILE = 'TVG_CRFRNN_new_deploy.prototxt'
    PRETRAINED = 'TVG_CRFRNN_COCO_VOC.caffemodel'
    IMAGE_FILE = inputfile

    input_image = 255 * caffe.io.load_image(IMAGE_FILE)
    input_image = resizeImage(input_image)

    width = input_image.shape[0]
    height = input_image.shape[1]
    maxDim = max(width,height)

    image = PILImage.fromarray(np.uint8(input_image))
    image = np.array(image)

    pallete = getpallete(256)

    mean_vec = np.array([103.939, 116.779, 123.68], dtype=np.float32)
    reshaped_mean_vec = mean_vec.reshape(1, 1, 3);

    # Rearrange channels to form BGR
    im = image[:,:,::-1]
    # Subtract mean
    im = im - reshaped_mean_vec

    # Pad as necessary
    cur_h, cur_w, cur_c = im.shape
    pad_h = 500 - cur_h
    pad_w = 500 - cur_w
    im = np.pad(im, pad_width=((0, pad_h), (0, pad_w), (0, 0)), mode = 'constant', constant_values = 0)
    # Get predictions
    #segmentation = net.predict([im])
    segmentation  = crfasrnn_segmenter(MODEL_FILE,PRETRAINED,gpudevice,[im])

    segmentation2 = segmentation[0:cur_h, 0:cur_w]
    output_im = PILImage.fromarray(segmentation2)
    output_im.putpalette(pallete)
    output_im.save(outputfile)


def resizeImage(image):
        width = image.shape[0]
        height = image.shape[1]
        maxDim = max(width,height)
        if maxDim>500:
            if height>width:
                ratio = float(500.0/height)
            else:
                ratio = float(500.0/width)
            image = PILImage.fromarray(np.uint8(image))
            image = image.resize((int(height*ratio), int(width*ratio)),resample=PILImage.BILINEAR)
            image = np.array(image)
        return image

'''
    Chama Rede neural direto do diretório
'''
def callFromDirectory(p_folder,p_outfolder,createPath,gpudevice):
    allowedExtensions = ['png','jpg','raw','bmp']
    os.system("mkdir "+p_outfolder)
    folders = glob.glob(p_folder+"/*")
    print "Logs:", folders, "\n"
    for folder in folders:
        if(len(folder.split("."))<=1):
            if(createPath):
                print "CRIANDO PASTA: ", folder[len(p_folder):]
                os.system("mkdir "+p_outfolder+"/"+folder[len(p_folder):])
            files = glob.glob(folder+"/*.*")
            print "LOGS: ", files, "\n"
            for image in files:
                ext = image.split(".")
                ext.reverse()
                if(ext[0] in allowedExtensions):
                    if(createPath):
                        imgPath = p_outfolder+image[len(folder):]
                    else:
                        imgPath = p_outfolder+"/"+image[len(p_folder)+1:].replace("/","-")
                    print "EXECUTANDO IMAGEM: ",image
                    print "SALVAR EM: ",imgPath
                    run_crfasrnn(image,imgPath,gpudevice)
        else:
            print "NAO E DIRETORIO"

def main(argv):
   inputfile = 'input.jpg'
   outputfile = 'output.png'
   inputfolder = ""
   outputfolder = "out"
   createpath = False
   gpu_device = -1#0 # use -1 to run only on CPU, use 0-3[7] to run on GPU
   try:
      opts, args = getopt.getopt(argv,'hi:o:g:f:p:c:',["ifile=","ofile=","gpu=","inputfolder=","outputfolder=","createPath="])
   except getopt.GetoptError:
      print 'crfasrnn.py -i <inputfile> -o <outputfile> -g <gpu_device> -f <inputfolder> -p <outputfolder> -c <createpath>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'crfasrnn.py -i <inputfile> -o <outputfile> -g <gpu_device> -f <inputfolder> -p <outputfolder> -c <createpath>'
         sys.exit()
      elif opt in ("-i", "ifile"):
         inputfile = arg
      elif opt in ("-o", "ofile"):
         outputfile = arg
      elif opt in ("-g", "gpudevice"):
         gpu_device = int(arg)
      elif opt in ("-f", "inputfolder"):
         inputfolder = arg
      elif opt in ("-p", "outputfolder"):
         outputfolder = arg
      elif opt in ("-c", "createPath"):
         createpath = (arg == "1")

   if(inputfolder != ""):
      print 'CALL FROM FOLDER',inputfolder
      print 'GPU_DEVICE is ', gpu_device
      callFromDirectory(inputfolder,outputfolder,createpath,gpu_device)
      return
   
   print 'Input file is "', inputfile
   print 'Output file is "', outputfile
   print 'GPU_DEVICE is "', gpu_device
   run_crfasrnn(inputfile,outputfile,gpu_device)



if __name__ == "__main__":
    main(sys.argv[1:])
