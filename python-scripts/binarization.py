'''
	Binariza as imagens geradas pela Rede Neural.
	Serve para funcionar como mascara de entrada para o ODD
'''

import cv2
import numpy as np
from matplotlib import pyplot as plt


def callFromDirectory(p_folder,p_outfolder,createPath):
	'''
		Acessa um diretório e seleciona todos os arquivos a serem processados
	'''
    allowedExtensions = ['png','jpg','raw','bmp']
    os.system("mkdir "+p_outfolder)
    folders = glob.glob(p_folder+"/*")
    print "PASTAS:", folders, "\n"
    for folder in folders:
        if(len(folder.split("."))<=1):
            if(createPath):
                print "CRIANDO PASTA: ", folder[len(p_folder):]
                os.system("mkdir "+p_outfolder+"/"+folder[len(p_folder):])
            files = glob.glob(folder+"/*.*")
            print "Arquivos: ", files, "\n"
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
                    binarize(image,imgPath)
                    #run_crfasrnn(image,imgPath,gpudevice)
        else:
            print "NAO E DIRETORIO"


def resizeImage(image,p_height,p_width):
	'''
		Redimensiona imagem para p_height e p_width
		@returns image
	'''
    width = image.shape[0]
    height = image.shape[1]
    maxDim = max(width,height)
    if height>width:
        ratio = float(p_height/height)
    else:
        ratio = float(p_width/width)
    image = PILImage.fromarray(np.uint8(image))
    image = image.resize((int(height*ratio), int(width*ratio)),resample=PILImage.BILINEAR)
    image = np.array(image)
    return image

def binarize(input_img,output_img):
	'''
		Binariza imagem em preto e branco
	'''
    img = cv2.imread(input_img,0)
    img = cv2.medianBlur(img,5)
    ret,th1 = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
    th2 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
    th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
    titles = ['Original Image', 'Global Thresholding (v = 127)','Adaptive Mean Thresholding', 'Adaptive Gaussian Thresholding']
    images = [img, th1, th2, th3]
    
    for i in xrange(4):
        plt.subplot(2,2,i+1),plt.imshow(images[i],'gray')
        plt.title(titles[i])
        plt.xticks([]),plt.yticks([])
    plt.show()


def main(argv):
   inputfile = 'input.jpg'
   outputfile = 'output.png'
   inputfolder = ""
   outputfolder = "out"
   createpath = False
   try:
      opts, args = getopt.getopt(argv,'hi:o:g:f:p:c:',["ifile=","ofile=","gpu=","inputfolder=","outputfolder=","createPath="])
   except getopt.GetoptError:
      print 'binarization.py -i <inputfile> -o <outputfile> -f <inputfolder> -p <outputfolder> -c <createpath>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'binarization.py -i <inputfile> -o <outputfile> -f <inputfolder> -p <outputfolder> -c <createpath>'
         sys.exit()
      elif opt in ("-i", "ifile"):
         inputfile = arg
      elif opt in ("-o", "ofile"):
         outputfile = arg
      elif opt in ("-f", "inputfolder"):
         inputfolder = arg
      elif opt in ("-p", "outputfolder"):
         outputfolder = arg
      elif opt in ("-c", "createPath"):
         createpath = (arg == "1")

   if(inputfolder != ""):
      print 'CALL FROM FOLDER',inputfolder
      callFromDirectory(inputfolder,outputfolder,createpath)
      return

   print 'Input file is "', inputfile
   print 'Output file is "', outputfile
   binarize(inputfile,outputfile)
   #run_crfasrnn(inputfile,outputfile,gpu_device)



if __name__ == "__main__":
    main(sys.argv[1:])