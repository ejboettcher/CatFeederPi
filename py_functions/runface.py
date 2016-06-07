
import time
import threading
import picamera
from picamera.array import PiRGBArray
import cv2
import numpy as np
from imagesearch.facedetector import FaceDetector
import json
import os

#cascade_ff = "../../../opencv/data/lbpcascades/lbpcascade_frontalface.xml"
#cascade_pf = "../../../opencv/data/haarcascades/haarcascade_profileface.xml"   

class Runface(object):
    thread    = None  # background thread that detects face
    detection = "False"  # current frame is stored here by background thread
    conf  = json.load(open("./templates/conf.json"))
    
    ffaceRects = None
    pfaceRects = None

    # initialize the Detection File: Preload with nd null detections and times
    # After nd detection.  Save outfile. 
    ind  		= 0 
    nd  		= conf["num_det_to_ave"]  #10
    det_list 		= [None] * nd 
    det_timestamp	= [None] * nd

    # Initialize the Json Detection file
    f = open('./det_output/json_det.txt','w')
    f.write('{"data":[{"status":" None", "time": "9999", "stillim":"9999"}]}')

    f.close()
     
    # Detection Setup
    font = cv2.FONT_HERSHEY_SIMPLEX
    oldRotation=0
    Rotations =[0,20,40,60,-20,-40,-60]	
    
    # construct the face detector
    cascade_pf  = conf["face_side_det"]
    cascade_ff  = conf["face_front_det"]
 
    # TODO
    last_access = 0  # time of last client access to the camera
    
    # Camera Setup
    imsize  = tuple(conf["resolution_raw"])    #[480,320]
    npframe = np.zeros((imsize[0],imsize[1],3),np.uint8)

    def initialize(self):       
        if Runface.thread is None:
            # start background frame thread
            Runface.thread = threading.Thread(target=self._thread)
            Runface.thread.start()

    def get_detection(self,npframe):
        Runface.npframe = npframe;
        #run detection once a x sec 
        if time.time()-Runface.last_access > 1/self.conf["det_fps"]: 
        	Runface.last_access = time.time()
        	self.initialize()        	
	return self.detection, self.ffaceRects, self.pfaceRects

    @classmethod
    def _thread(cls):
	
	ind 	= 0  # initial count in detection Max is nd
	ff   	= FaceDetector(cls.cascade_ff)
	pf 	= FaceDetector(cls.cascade_pf)

     gray  	= cv2.cvtColor(cls.npframe, cv2.COLOR_BGR2GRAY)
        gray1 	= np.copy(gray)
	center  = [cls.imsize[0]/2, cls.imsize[1]/2]
	
	scale    =  0.6

	ffaceRects = None
	pfaceRects = None

        ## ### ## Try with OLD Rotation FIRST ##############
	if cls.oldRotation==0:
		ffaceRects, pfaceRects = make_detection(gray1,ff, pf,cls.imsize[0],cls.conf)
	else:
		rot_angle = cls.oldRotation		
		rot_mat   = cv2.getRotationMatrix2D(tuple(center),rot_angle,scale)
		gray1     = np.copy(cv2.warpAffine(gray,rot_mat,(cls.imsize[0],cls.imsize[1])))		
		ffaceRects, pfaceRects = make_detection(gray1,ff, pf,cls.imsize[0],cls.conf) 
		
	#cv2.putText(cls.npframe,"Using Rotation: "+ str(120+cls.oldRotation),(10,210),cls.font,0.5,(0,255,255))
	
	## ROTATE IMAGE IF NO FACES FOUND ---------------------------------
	if not len(ffaceRects) and not len(pfaceRects):
		loopmax = len(cls.Rotations)		
		ln  	= 0
		while (((not len(ffaceRects)) and (not len(pfaceRects))) and ln<loopmax):
			rot_angle = cls.Rotations[ln]
		#	cv2.putText(cls.npframe,"Trying new Rotation: "+str(rot_angle),(10,75+5*ln),cls.font,0.25,(255,255,255))				
			rot_mat = cv2.getRotationMatrix2D(tuple(center),rot_angle,scale)

			gray1 	= np.copy(cv2.warpAffine(gray,rot_mat,(cls.imsize[0],cls.imsize[1])))
			gray2   = np.copy(gray1)
			ffaceRects, pfaceRects = make_detection(gray1,ff, pf, cls.imsize[0],cls.conf) 
			ln=ln+1
						
		#if len(ffaceRects) or len(pfaceRects):	
		#	cv2.putText(cls.npframe,"Baby in Car",(210,30),cls.font,1,(255,255,255))
		#	cls.oldRotation = rot_angle
	

	if len(ffaceRects) or len(pfaceRects):
        	cls.detection = 1.0
		if cls.conf["show_det"]:
		    showMydetections(ffaceRects, pfaceRects, cls.npframe)
		
      
	else:
		cls.detection = 0.0
	
	cls.ffaceRects	= ffaceRects	
	cls.pfaceRects	= pfaceRects
 	

	# Fill in the detection list 
        
        
	if cls.ind < cls.nd:
		
		# Add to the detection list		
		cls.det_list[cls.ind] = cls.detection

		cls.ind = cls.ind +1
	else: 
		print(cls.det_list)
		cls.ind = 0		
		# Make Final Detection call
		Status = str(final_det_call(cls.det_list, cls.conf))
		p = os.popen('stat --format "%Y" static/stillimg.jpg', "r")
		imtimestamp = int(p.readline())
	
		# save out detections
		f = open('./det_output/json_det.txt','w')
		#f.write('{"data":[{"status":"'+ Status + '", "time": "'+ time.ctime()  +
		f.write('{"data":[{"status":"'+ Status + '", "time": "'+ str(time.time())  +
				'", "stillim": "'+ str(imtimestamp) +'"}]}')
	        f.close()


        cls.thread = None

def final_det_call(det_list, conf):
	#
	#threshold = 5
	threshold = conf["delta_thresh"]
	finalDet  = False
	
	if sum(det_list)>threshold:
		finalDet = True	
		
	return  finalDet



def make_ONEdetection(grayim, pf, conf):
 	# detect faces in the image         
        
	pfaceRects = pf.detect(grayim, scaleFactor = conf["pface_scaleFactor"], 
		minNeighbors = conf["pface_minNeighbors"], minSize = tuple(conf["pface_minSize"]))
	#pfaceRects = pf.detect(grayim, scaleFactor = 1.05, 
	#	minNeighbors = 4, minSize = (34, 20))
		
	return  pfaceRects
	
def make_detection(grayim, ff, pf, imagewidth, conf):
 	# detect faces in the image   from frontal to side      
	dgray = np.copy(grayim)
        ffaceRects = ff.detect(dgray, scaleFactor = conf["fface_scaleFactor"], 
		minNeighbors = conf["fface_minNeighbors"], minSize = tuple(conf["fface_minSize"]))
	pfaceRects=()

	# Do side detection if no front face
	if not len(ffaceRects):		
		fgray = np.copy(grayim)
		pfaceRects=make_ONEdetection(fgray,pf,conf)
		
		# flip image 
		if not len(pfaceRects):			
			ffgray = np.copy(cv2.flip(grayim,1))			
			pfaceRects=make_ONEdetection(ffgray,pf, conf)        
			## Makes the rectanges in the frame of the original	        	
			pfaceRects =[(imagewidth-fX-fW ,fY,fW,fH) for (fX, fY, fW, fH) in pfaceRects]
				
	return  ffaceRects, pfaceRects

def showMydetections(ffaceRects, pfaceRects, gray):
	# loop over the face bounding boxes and draw them
        for (fX, fY, fW, fH) in ffaceRects:
        	cv2.rectangle(gray, (fX, fY), (fX + fW, fY + fH), (0, 255,0),2)

	for (fX, fY, fW, fH) in pfaceRects:
        	cv2.rectangle(gray, (fX, fY), (fX + fW, fY + fH), (0, 255,0),2)

	cv2.imshow("Face Det",gray)
	cv2.waitKey(50)

	