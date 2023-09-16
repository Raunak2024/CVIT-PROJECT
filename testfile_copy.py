import codecs,subprocess,os,sys,glob
import random
import cv2
import numpy as np
import PIL
from PIL import Image
from subprocess import call
random.seed()
#language='Arabic'
#process='intialRender'
#iteration="One"
#get the list of unique font family Names
with open(sys.argv[2]) as f:
	fontsList = f.read().splitlines()
print ('number of unique fonts being considered= ', len(fontsList))
#a set of images , whose random crops can be used as background for the rendered word images. We used Validation set of Places dataset for this

# replace the below path with your location of images
#PlacesImList=glob.glob("image1.jpg")

# Specify the base directory path
base_directory = os.path.expanduser("~/places365_val_dataset/val")

# Create an empty list to store all image file paths
PlacesImList = []

# Recursively traverse the directory structure and gather all image file paths
for root, _, files in os.walk(base_directory):
    for file in files:
        if file.lower().endswith(".jpg"):
            image_path = os.path.join(root, file)
            try:
                # Attempt to open the image to check if it's valid
                Image.open(image_path)
                PlacesImList.append(image_path)
                # If the image is valid, append the path to PlacesImList
            except Exception as e:
                # If the image in invalid, just skip
                pass

#Now, the PlacesImList list contains all the valid file paths for the JPG images in the directory and its subdirectories

writeDirParent=sys.argv[3]+sys.argv[5]+'/'
xmlFileName=sys.argv[3]+sys.argv[4]+'_DetailedAnnotation.csv'

print("writeDirParent:", writeDirParent)
print("xmlFileName:", xmlFileName)

field_names = [
    "ImageFilePath",
    "TextWord",
    "Index",
    "FontName",
    "FontSize",
    "FontStretch",
    "ArcValue",
    "PerspectiveBoolean",
    "FGBlendBoolean",
    "BGNaturalImage",
    "Density",
    "Erosion",
    "Dilation",
    "Gaussian Blur",
    "Median Blur",
    "Salt Pepper Noise",
    "Gaussian Noise"
]

if not os.path.exists(xmlFileName):
    # Open the CSV file in write mode ('w') to create a new file and write the header
    with codecs.open(xmlFileName, 'w', encoding='utf8') as myfile:
        # Write the field names as the header row
        myfile.write(','.join(field_names) + '\n')

vocabFile = codecs.open(sys.argv[1],'r',encoding='utf8')
myfile = codecs.open(xmlFileName,'a',encoding='utf8')
words = vocabFile.read().split()

##distortArcOptions={'40','60','70','80','40','40','30'}
#skewOptions={'1','2','3','4','5','-1','-2','-3','-4','-5'}
distorArcBooleanOptions={0,0,0,0,0,0,0,0,1}
#skewBooleanOptions={0,0,0,0,0,1}
##densityOptions={'100','150','150','150','200','200','200','250','250','300','300','200','150','200','300','300','300','250','250'}
boldBooleanOptions={0,0,1}
italicBooleanOptions={0,0,0,0,0,0,0,0,0,0,0,0,1}
##fontSizeOptions={'12','14','16','18','20','22','24','26','28','32','34','36'}
##fontSizeOptions={'44','46','56','58','66','72'}
fontStretchOptions={'semicondensed', 'normal', 'semiexpanded',  'normal', 'normal', 'normal','normal','normal','normal', 'normal','normal','normal','semicondensed','semicondensed','semicondensed','semicondensed','semicondensed', 'semiexpanded', 'semiexpanded', 'semiexpanded', 'semiexpanded','normal', 'normal', 'normal','normal','normal','normal', 'normal','normal','normal'}
shadowBooleanOptions={0,0,0,0,0,0,0,0,1}
perspectiveBooleanOptions={0,0,0,1,1,1,1}

##shadowWidthOptions={'0','0','0','2','3','4'}
##shadowSigmaOptions={'1','3'}
##shadowOpacityOptions={'100','100','100','100','90','80','70'}
##shadowWidthSignOptions={'+','-'}
#outputfile = open('render_commands_'+language+'_'+process+'_'+iteration+'.sh','w')
#gtfile = open('ocr_gt.txt','w')

min_arc_value = 20
max_arc_value = 20
distortArcOptions = [str(i) for i in range(min_arc_value, max_arc_value+1)]

min_density = 50
max_density = 50
densityOptions = [str(i) for i in range(min_density, max_density+1)]

min_font_size = 10  
max_font_size = 10
fontSizeOptions = [str(i) for i in range(min_font_size, max_font_size+1)]

trimOptions={0,1}

min_shadow_width = 2
max_shadow_width = 2
shadowWidthOptions = [str(i) for i in range(min_shadow_width, max_shadow_width+1)]

min_shadow_sigma = 1
max_shadow_sigma = 1
shadowSigmaOptions = [str(i) for i in range(min_shadow_sigma, max_shadow_sigma+1)]

min_shadow_opacity = 50
max_shadow_opacity = 50
shadowOpacityOptions = [str(i) for i in range(min_shadow_opacity, max_shadow_opacity+1)]

shadowWidthSignOptions = ['+', '-']

numWords=len(words)
print ('number of words in the vocab= ', numWords)

for i in range(0, numWords):
    if i % 1000 == 0:
        print("completed", i)
        thousand = i // 1000
        writeDir = writeDirParent + str(thousand) + "/"
        if not os.path.exists(writeDir):
            os.makedirs(writeDir)
        filelist = glob.glob("*.png")  # remove all temp png files after every 1000 words
        for f in filelist:
            os.remove(f)
        textImageName = str(i) + "_text.png"

    #print("textImageName:",textImageName)


# to convert and rgb in tuple to rgb hex representation '#%02x%02x%02x' % (fg[0], fg[1], fg[2])
    fg=random.sample(range(0, 255), 3) ###### making fg color more brighter ##
    bg=random.sample(range(0, 255), 3)
    bg[0]=abs(fg[0]+100-255)
    bg[1]=abs(fg[0]+100-255)
    bg[2]=abs(fg[2]+125-255)
    sd=random.sample(range(0, 255), 3)

    fg_hex='#%02x%02x%02x' % (fg[0], fg[1], fg[2])
    bg_hex='#%02x%02x%02x' % (bg[0], bg[1], bg[2])
    sd_hex='#%02x%02x%02x' % (sd[0], sd[1], sd[2])

    if bool(random.getrandbits(1)):
 	   tmp=fg_hex
 	   fg_hex=bg_hex
 	   bg_hex=tmp

## random density skew slant font fontsize kerning

### FUNCTION CALLS ###


    density=random.sample(list(densityOptions),1)[0]
    distortArcBoolean=random.sample(list(distorArcBooleanOptions),1)[0]
    boldBoolean=random.sample(list(boldBooleanOptions),1)[0]
    italicBoolean=random.sample(list(italicBooleanOptions),1)[0]
    fontSize=random.sample(list(fontSizeOptions),1)[0]
    fontName=random.sample(list(fontsList),1)[0]
    fontStretch=random.sample(list(fontStretchOptions),1)[0]

    shadowOpacity=random.sample(list(shadowOpacityOptions),1)[0]
    shadowSigma=random.sample(list(shadowSigmaOptions),1)[0]
    shadowWidth=random.sample(list(shadowWidthOptions),1)[0]
    shadowWidthSign=random.sample(list(shadowWidthSignOptions),1)[0]

### making the convert command ####

    command='convert  -alpha set  -background none'
    skewValue='0'
    arcValue='0'
    if distortArcBoolean==1:
	    distortArc=random.sample(list(distortArcOptions),1)[0]
	    command+=' -distort Arc '+ distortArc
	    arcValue=distortArc
    command+=' pango:\'   <span '
    command+='font_stretch='+'\"'+fontStretch+'\" '
    command+='foreground='+'\"'+fg_hex+'\" '
    print("Value of i:",i)
    textWord=words[i]
    #textWord = random.choice(words)
    print("textWord:",textWord)

    if italicBoolean==1:
	    textWord='<i>'+textWord+'</i>'
    if boldBoolean==1:
	    textWord='<b>'+textWord+'</b>'

    #if italicBoolean == 1:
        #textWord = f'<i>{textWord}</i>'
    #if boldBoolean == 1:
        #textWord = f'<b>{textWord}</b>'

    #fontName='Roboto Black'
    print("fontName:",fontName)
    fontString='font='+'\"'+fontName+' '+fontSize+' \">  '
    fontString+=' '+ textWord + '</span> \''
    command+=fontString
    #command+=' rendered_image.jpeg'
    trimBoolean=random.sample(list(trimOptions),1)[0]
    #command+=' -trim ' #do trim in all cases
    command+=' png:-|'

#### add shadow/border ######

    command+='convert - ' + ' \\( +clone -background ' + '\''+str(sd_hex)+'\' -shadow '
    command+= shadowOpacity+'x'+shadowSigma+shadowWidthSign+shadowWidth+shadowWidthSign+shadowWidth + ' \\) +swap  -background none   -layers merge  +repage '+ 'png:-| '

######  distort the perspective of the image ########
    perspectiveBoolean=random.sample(list(perspectiveBooleanOptions),1)[0]
    if perspectiveBoolean==1:
        sx=random.uniform(0.7, 1.3)
        ry=random.uniform(-0.8, 0.8)
        rx=random.uniform(-0.15, 0.15)
        sy=random.uniform(0.7, 1.3)
        px=random.uniform(0.0001, 0.001)
        py=random.uniform(0.0001, 0.001)
	#print "boom"
        command+='convert - ' + ' -alpha set -virtual-pixel transparent +distort Perspective-Projection '
        command+= '\''+str(sx)+ ', ' + str(ry) + ', 1.0\t' + str(rx) + ', ' + str(sy) + ', 1.0\t' + str(px) + ', ' + str(py) + '\'  png:-| '
    command+= ' convert - '
    if trimBoolean==1:
	    command+='  -trim '
   #command+=' png:-|'
    command+=' -resize x32 '
    command+=textImageName

   #print '*******'
   #print command.encode('utf-8')
    os.system(command.encode('utf-8'))
    finalFgLayerName=textImageName
    im=Image.open(textImageName)
    imWidth, imHeight = im.size

   #print bgCommand.encode('utf-8')
   #convert -background none -alpha set -channel A -evaluate set 100%   -size "88x50" xc:yellow  yellow100.png
   ####### blend fg and bg with a natural scene images separately ##########
	#fgBlendBooleanOptions={0,0} #should a natural image be blended with the text stroke ie the fg layer
	#bgBlendBooleanOptions={0,0} #should the bg (which is a uniform color for now) be blended with a natural scene
	#fgBlendBoolean=random.sample(fgBlendBooleanOptions,1)[0]
	#bgBlendBoolean=random.sample(bgBlendBooleanOptions,1)[0]
	#################################################################################################################
	# to make the rendering simpler, the blending part is only done in this manner				#
	# 1. blend the fg with a natural image and keep the bg a uniform color itself				#
	# 2. keep fg color uniform and overlay it on a natural image ( ie the bg is a crop from a natural image)	#
	#################################################################################################################
    fgorBgBooleanOptions={0,1} # 0 means text should be blended 1 means bg is just a natural image crop
    fgOrBgBoolean=random.sample(list(fgorBgBooleanOptions),1)[0]
	# pick a random image from places dataset and get a crop from it, of the same size as our textImage
    naturalImageName = random.sample(PlacesImList,1)[0]
    fgImage=Image.open(naturalImageName)
    fgWidth, fgHeight = fgImage.size
    if fgWidth < imWidth+5 or  fgHeight < imHeight+5:
        fgImage=fgImage.resize((imWidth+10,imHeight+10),PIL.Image.ANTIALIAS)
        fgWidth, fgHeight = fgImage.size

				#get a random crop from the image chosen from blending
    x=random.sample(range(0,fgWidth-imWidth+2 ),1)[0]
    y=random.sample(range(0, fgHeight-imHeight+2),1)[0]
    w=imWidth
    h=imHeight
    fgImageCrop=fgImage.crop((x ,y ,x+w, y+h))
    fgImageCropName=str(i) + '_naturalImage.png'
    fgImageCrop.save(fgImageCropName)
    fgBlendBoolean=0
    bgNaturalImage=0
    #print fgOrBgBoolean   
    #if fgOrBgBoolean==0:
    if  False:
        #fgComposeModeOptions={'Multiply','over','Dst_out', 'Screen', 'Bumpmap', 'Divide', 'plus', 'minus', 'ModulusAdd', 'difference'  }
        #fgComposeMode=random.sample(fgComposeModeOptions,1)[0]
        textBgBlendImageName=str(i)+'_textBgBlend.png' #the image which is blend of natural image and the fg text layer
        textBgBlendCommand='composite ' + textImageName + ' -compose Dst_in ' + fgImageCropName + ' -alpha set ' +  textBgBlendImageName

        #textBgBlendCommand='composite ' + textImageName +  ' -compose ' + fgComposeMode + ' ' + fgImageCropName + ' -alpha set ' + textBgBlendImageName
        
        os.system(textBgBlendCommand.encode('utf-8'))
        finalFgLayerName=textBgBlendImageName
        ####  now in this case our bg wll be a uniform color ####
        bgCommand='convert -background none -alpha set -size '
        bgCommand+='\"' + str(imWidth) + 'x' + str(imHeight) + '\" xc:' + '\"' + bg_hex + '\" '
        bgLayerName=str(i)+'_bgLayer.png'
        bgCommand+= bgLayerName

        #print bgCommand.encode('utf-8')
        os.system(bgCommand.encode('utf-8'))
        fgBlendBoolean=1

    else:
        #when fgorBgBoolean==1 we dont to fg blend but choose bg as a natural image crop
	    #print ('bgisnatural')
        bgLayerName=fgImageCropName
        bgNaturalImage=1
    #finalFgLayerName=textImageName
    finalBgLayerName=bgLayerName

    ###FUNCTION CODE###

    finalBlendImageName=writeDir+str(i)+'.jpeg'
    finalBlendCommand='composite -gravity center ' + finalFgLayerName + ' ' +  finalBgLayerName
    finalBlendCommand+=' jpeg:-|'
    finalBlendCommand += 'convert - ' + finalBlendImageName
#print finalBlendCommand.encode('utf-8')
    os.system(finalBlendCommand.encode('utf-8'))
    #print(finalBlendImageName)
    #this is the name of the actual rendered image file along with its directory path

    image = cv2.imread(finalBlendImageName)
    #print("image:",image) ##
    #this is for reading this image in the form of a numpy array for performing image processing functions

    #this is the erosion function that will/will not be called based upon a chosen random boolean value
    
    erotion=0
    dilation=0
    gaussianblur=0
    medianblur=0
    saltpeppernoise=0
    gaussiannoise=0

    #def erotion_image(image):
    #    global erotion
    #    height,width,channel = image.shape
    #    image_erotion = image
    #    if (height>13 and width>13):
    #        window = random.randint(3,13) 
    #        kernel = np.ones((window, window), np.uint8)
    #        image_erotion = cv2.erode(image, kernel, iterations=1)
    #        image_erotion = image_erotion.astype('uint8')
    #        image_erotion = np.array(image_erotion)
    #        print("Erosion Applied on Image")
    #        erotion=1
    #        return(image_erotion)
    
    def erotion_image(image):
        global erotion
        height,width,channel = image.shape
        image_erotion = image
        if (height>21 and width>21):
            #max_window = min(height, width)
            window = random.randint(3, 3)
            kernel = np.ones((window, window), np.uint8)
            image_erotion = cv2.erode(image, kernel, iterations=1)
            image_erotion = image_erotion.astype('uint8')
            image_erotion = np.array(image_erotion)
            print("Erosion Applied on Image")
            erotion=1
            return(image_erotion)
    
    #def dilation_image(image):
    #    global dilation
    #    height,width,channel = image.shape
    #    image_dilation = image
    #    if(height>7 and width>7):
    #        window = random.randint(3,7)
    #        kernel = np.ones((window, window), np.uint8)
    #        image_dilation = cv2.dilate(image, kernel, iterations=1)
    #        image_dilation = image_dilation.astype('uint8')
    #        image_dilation = np.array(image_dilation)
    #        print("Dilation Applied on Image")
    #        dilation=1
    #        return(image_dilation)
    
    def dilation_image(image):
        global dilation
        height,width,channel = image.shape
        image_dilation = image
        if(height>7 and width>7):
            #max_window = min(height, width)
            window = random.randint(3, 5)
            kernel = np.ones((window, window), np.uint8)
            image_dilation = cv2.dilate(image, kernel, iterations=1)
            image_dilation = image_dilation.astype('uint8')
            image_dilation = np.array(image_dilation)
            print("Dilation Applied on Image")
            dilation=1
            return(image_dilation)
    
    #def gaussian_blur(image):
    #    global gaussianblur
    #    height,width,channel = image.shape
    #    image1 = image
    #    if (height>19 and width>19):
    #        window1 = random.randrange(11,19+1, 2)
    #        image1 = cv2.GaussianBlur(image,(window1, window1),0)
    #        image1 = image1.astype('uint8')
    #        image1 = np.array(image1)
    #        print("GaussianBlur Applied on Image")
    #        gaussianblur=1
    #        return(image1)

    def gaussian_blur(image):
        global gaussianblur
        height,width,channel = image.shape
        image1 = image
        if (height>19 and width>19):
            #window1 = random.randrange(3, 8, 2)
            window1 = random.randrange(3, 6, 2)
            image1 = cv2.GaussianBlur(image,(window1, window1),0)
            image1 = image1.astype('uint8')
            image1 = np.array(image1)
            print("GaussianBlur Applied on Image")
            gaussianblur=1
            return(image1) 
    
    #def mediun_blur(image):
    #    global medianblur
    #    height,width,channel = image.shape
    #    image1 = image
    #    if (height>13 and width>13):
    #        window1 = random.randrange(3, 13+1, 2)
    #        image1 = cv2.medianBlur(image,window1)
    #        image1 = image1.astype('uint8')
    #        image1 = np.array(image1)
    #        print("MedianBlur Applied on Image")
    #        medianblur=1
    #        return(image1)

    def mediun_blur(image):
        global medianblur
        height,width,channel = image.shape
        image1 = image
        if (height>13 and width>13):
            window1 = random.randrange(3, 6, 2)
            image1 = cv2.medianBlur(image,window1)
            image1 = image1.astype('uint8')
            image1 = np.array(image1)
            print("MedianBlur Applied on Image")
            medianblur=1
            return(image1)
    
    #def salt_pepper_noise(image):
    #    global saltpeppernoise
    #    height,width,channel = image.shape 
    #    probability1 = random.randint(1, 2)
    #    noise_probability = random.randint(1, 2)
    #    noise_probability = noise_probability/50.0
    #    no_noisy_pixel = int(height * width * noise_probability)
    #    if probability1 == 1:
    #        probability = random.randint(1, 2)
    #        for s in range (no_noisy_pixel):
    #            x = random.randint(0, height-1)
    #            y = random.randint(0, width-1)
    #            if probability == 1:
    #                image[x][y][0] = 0
    #                image[x][y][1] = 0
    #                image[x][y][2] = 0
    #            else:
    #                image[x][y][0] = 255
    #                image[x][y][1] = 255
    #                image[x][y][2] = 255
    #    else:
    #        for s in range (no_noisy_pixel):
    #            x = random.randint(0, height-1)
    #            y = random.randint(0, width-1)
    #            probability = random.randint(1, 2)
    #            if probability == 1:
    #                image[x][y][0] = 255
    #                image[x][y][1] = 255
    #                image[x][y][2] = 255
    #            else:
    #                image[x][y][0] = 0
    #                image[x][y][1] = 0
    #                image[x][y][2] = 0		
    #    print("SaltPepperNoise Applied on Image")
    #    saltpeppernoise=1
    #    return(image)
    
    def salt_pepper_noise(image):
        global saltpeppernoise
        height,width,channel = image.shape
        probability1 = random.randint(1, 2)
        noise_probability = random.uniform(0.01, 0.1)
        no_noisy_pixel = int(height * width * noise_probability)
        if probability1 == 1:
            probability = random.randint(1, 2)
            for s in range (no_noisy_pixel):
                x = random.randint(0, height-1)
                y = random.randint(0, width-1)
                if probability == 1:
                    image[x][y][0] = 0
                    image[x][y][1] = 0
                    image[x][y][2] = 0
                else:
                    image[x][y][0] = 255
                    image[x][y][1] = 255
                    image[x][y][2] = 255
        else:
            for s in range (no_noisy_pixel):
                x = random.randint(0, height-1)
                y = random.randint(0, width-1)
                probability = random.randint(1, 2)
                if probability == 1:
                    image[x][y][0] = 255
                    image[x][y][1] = 255
                    image[x][y][2] = 255
                else:
                    image[x][y][0] = 0
                    image[x][y][1] = 0
                    image[x][y][2] = 0     
        print("SaltPepperNoise Applied on Image")
        saltpeppernoise=1
        return(image)
    
    #def gaussian_noise(image):
    #    global gaussiannoise
    #    height,width,channel = image.shape
    #    image1 = image
    #    mean = 0
    #    var = 3
    #    sigma = var ** 0.5 
    #    gaussian_noise = np.random.normal(mean, sigma, (height, width, channel))
    #    noisy_image = np.zeros(image.shape, np.float32)
    #    if ((height>=10 and height<70) and (width>=10 and width<70)):
    #        r1 = random.randint(5, 10)
    #        noisy_image = image.astype(np.float32) + gaussian_noise*r1
    #        red = noisy_image[:,:,0]
    #        mask = (red > 255.0)
    #        noisy_image[:,:,0][mask] = [255.0]
    #        green = noisy_image[:,:,1]
    #        mask = (green > 255.0)
    #        noisy_image[:,:,1][mask] = [255.0]
    #        blue = noisy_image[:,:,2]
    #        mask = (blue > 255.0)
    #        noisy_image[:,:,2][mask] = [255.0]
    #        red = noisy_image[:,:,0]
    #        mask = (red < 0.0)
    #        noisy_image[:,:,0][mask] = [0.0]
    #        green = noisy_image[:,:,1]
    #        mask = (green < 0.0)
    #        noisy_image[:,:,1][mask] = [0.0]
    #        blue = noisy_image[:,:,2]
    #        mask = (blue < 0.0)
    #        noisy_image[:,:,2][mask] = [0.0]
    #        image1 = noisy_image.astype('uint8')
    #        image1 = np.array(image1)
    #    print("GaussianNoise Applied on Image")
    #    gaussiannoise=1
    #    return(image1)
    
    def gaussian_noise(image):
        global gaussiannoise
        height,width,channel = image.shape
        image1 = image
        mean = 0
        var = random.uniform(0, 10)
        sigma = var ** 0.5 
        gaussian_noise = np.random.normal(mean, sigma, (height, width, channel))
        noisy_image = np.zeros(image.shape, np.float32)
        if ((10 <= height < 70) and (10 <= width <70)):
            r1 = random.randint(5, 10)
            noisy_image = image.astype(np.float32) + gaussian_noise*r1
            red = noisy_image[:,:,0]
            mask = (red > 255.0)
            noisy_image[:,:,0][mask] = [255.0]
            green = noisy_image[:,:,1]
            mask = (green > 255.0)
            noisy_image[:,:,1][mask] = [255.0]
            blue = noisy_image[:,:,2]
            mask = (blue > 255.0)
            noisy_image[:,:,2][mask] = [255.0]
            red = noisy_image[:,:,0]
            mask = (red < 0.0)
            noisy_image[:,:,0][mask] = [0.0]
            green = noisy_image[:,:,1]
            mask = (green < 0.0)
            noisy_image[:,:,1][mask] = [0.0]
            blue = noisy_image[:,:,2]
            mask = (blue < 0.0)
            noisy_image[:,:,2][mask] = [0.0]
            image1 = noisy_image.astype('uint8')
            image1 = np.array(image1)
        print("GaussianNoise Applied on Image")
        gaussiannoise=1
        return(image1)

    image_processing_functions = [erotion_image, dilation_image, gaussian_blur, mediun_blur, salt_pepper_noise, gaussian_noise]

    random_function = random.choice(image_processing_functions)
    final_image = random_function(image)

    #this is the variable for storing the result of the erosion function
    ## eroded_image=erotion_image(image) ##
    #print("eroded_image:",eroded_image)

    #observation-if we want to check if erosion has been applied on the original image, we can check the difference in the outputs of the pixel values in the two  numpy arrays which will most likely be decreased.

    #this is for storing the image in a jpg-file format
    cv2.imwrite(finalBlendImageName,final_image)
    #check where this newly rendered eroded file is stored
    final_image = cv2.imread(finalBlendImageName)
    #print("final_image:", final_image) ##

    #os.system(finalBlendCommand.encode('utf-8'))

    #for process_func in image_processing_functions:
    #if random.choice([True, False]):
        #image = process_func(image)

    #cv2.imwrite(finalBlendImageName, image)

#### combine fglayer and bglayer in normal manner  - just do normal overlay or say dissovlve method ###

    ##finalBlendCommand='composite -gravity center ' + finalFgLayerName + ' ' +  finalBgLayerName
    ##finalBlendCommand+=' jpeg:-|'
    ##finalBlendCommand += 'convert - ' + finalBlendImageName
#print finalBlendCommand.encode('utf-8')
    ##os.system(finalBlendCommand.encode('utf-8'))
    
### WRITING THE GT ALONG WITH RENDERING DETAILS TO a csv ###

#print command.encode('utf-8')
#print command_compose

    myfile.write(sys.argv[5]+'/'+str(thousand)+'/'+str(i)+'.jpeg, ')
    myfile.write(words[i] + ', ')
    myfile.write(str(i) + ', ')
    myfile.write(fontName + ', ')
    myfile.write(fontSize + ', ')
    myfile.write(fontStretch + ', ')
    myfile.write(arcValue + ', ')
    myfile.write(str(perspectiveBoolean) + ', ')
    myfile.write(str(fgBlendBoolean) + ', ')
    myfile.write(str(bgNaturalImage) + ', ')
    myfile.write(density + ', ')
    myfile.write(str(erotion) + ', ')
    myfile.write(str(dilation) + ', ')
    myfile.write(str(gaussianblur) + ', ')
    myfile.write(str(medianblur) + ', ')
    myfile.write(str(saltpeppernoise) + ', ')
    myfile.write(str(gaussiannoise) + ',\n')

myfile.close()

#Printing all the csv fields related file values


print("sys.argv[5]+'/'+str(thousand)+'/'+str(i)+'.jpeg, ' :",sys.argv[5]+'/'+str(thousand)+'/'+str(i)+'.jpeg, ' )
print("word:",words[i])
print("str(i) + ', ' :",str(i) + ', ' )
print("fontName + ', ' :",fontName + ', ' )
print("fontSize + ', ' :",fontSize + ', ' )
print("fontStretch + ', ' :",fontStretch + ', ' )
print("arcValue + ', ' :",arcValue + ', ' )
print("str(perspectiveBoolean) + ', ' :",str(perspectiveBoolean) + ', ' )
print("str(fgBlendBoolean) + ', ' :",str(fgBlendBoolean) + ', ' )
print("str(bgNaturalImage) + ', ' :",str(bgNaturalImage) + ', ' )
print("density:",density + ', ' )

import glob

# Identify image variables
imageVariables = ['fgImageCropName', 'textImageName', 'textBgBlendImageName',
                  'finalFgLayerName', 'bgLayerName', 'finalBlendImageName', 'finalBgLayerName']

# Iterate over image variables and print their values
for variable in imageVariables:
    if variable in globals():
        images = globals()[variable]
        print(f"{variable}: {images}")
    else:
        print(f"{variable} is not defined.")

print("distortArcBoolean:",distortArcBoolean)
print("boldBoolean:",boldBoolean)
print("italicBoolean:",italicBoolean)
print("trimBoolean:",trimBoolean)
print("perspectiveBoolean:",perspectiveBoolean)
print("shadowWidth:",shadowWidth)
print("shadowSigma:",shadowSigma)
print("shadowOpacity:",shadowOpacity)
print("shadowWidthSign:",shadowWidthSign)
print("trimBoolean:",trimBoolean)
print("erosion:",erotion)
print("dilation:",dilation)
print("gaussianblur:",gaussianblur)
print("medianblur:",medianblur)
print("saltpeppernoise:",saltpeppernoise)
print("gaussiannoise:",gaussiannoise)
