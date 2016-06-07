#!/usr/bin/python
import time
import threading
import picamera
from picamera.array import PiRGBArray
import cv2
import numpy as np
import json
from led_lr_pigpio import LED_LR

class MotionDet(object):
    thread    	= None  # background thread that detects face
    detection 	= "False"  # current frame is stored here by background thread
    conf  	= json.load(open("./templates/conf.json"))
    avg   	= None
    #LED         = LED_LR()
    #LED.Cleanup()
  
	  
    # TODO
    last_access = 0  # time of last client access to the camera
    
    # Camera Setup
    imsize  = tuple(conf["resolution_raw"])    #[480,320]
    npframe = np.zeros((imsize[0],imsize[1],3),np.uint8)

    def initialize(self):       
        if MotionDet.thread is None:
	
            # start background frame thread
            MotionDet.thread = threading.Thread(target=self._thread)
            MotionDet.thread.start()

    def get_movement(self,det, ffaceRects, pfaceRects,npframe):
        MotionDet.npframe 	= npframe
	MotionDet.ffaceRects	= ffaceRects
	MotionDet.pfaceRects	= pfaceRects
	MotionDet.det  	= det
        #run detection once a x sec 
        if time.time()-MotionDet.last_access > 1/self.conf["det_fps"]: 
        	MotionDet.last_access = time.time()
        	self.initialize()        	
	return self.detection

    @classmethod
    def _thread(cls):	
	ind 	= 0  # initial count in detection Max is nd

        gray  	= cv2.cvtColor(cls.npframe, cv2.COLOR_BGR2GRAY)
	gray  	= cv2.GaussianBlur(gray,(21,21),0)

	center  = [cls.imsize[0]/2, cls.imsize[1]/2]	
	scale   = 0.6

        # if the Average frame is Non, initialize it
	if cls.avg is None:
		print " [INFO] starting background model..."
		cls.avg = gray.copy().astype("float")
		
	
	# accumlate the weighted average between the current frame and the
	# previous frames, then compute the difference between the current frame and running averag
	cv2.accumulateWeighted(gray,cls.avg,0.50)
	frameDelta = cv2.absdiff(gray,cv2.convertScaleAbs(cls.avg))
	
	#threshold the delta image, dilate the threshold image to fill in holes
	# then find contours on the threshold image
	thresh = cv2.threshold(frameDelta, cls.conf["delta_thresh"],
		255,cv2.THRESH_BINARY)[1]
	thresh = cv2.erode(thresh, None, iterations=2)
	thresh = cv2.dilate(thresh, None, iterations=2)

	
	#(_,cnts,_) = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,
	#	cv2.CHAIN_APPROX_SIMPLE)
	
	# Loop over the Contours
	#text = "NA"
	#for c in cnts:
	#	# if the contour is too small, ignore it
	#	if cv2.contourArea(c) > cls.conf["min_area"]:		
	#		# compute the bounding box for the contour, draw it on the frame, and update the
	#		(x, y, w, h) = cv2.boundingRect(c)
	#		cv2.rectangle(gray,(x,y),(x+w,y+h),(0,255,0),1)
	#		text = "MOTION"
	
	# Find if motion on Left or RIght of face
	LR_Motion=Left_Right(cls.imsize, cls.ffaceRects, cls.pfaceRects, thresh)

	if LR_Motion==0:
		LED_LR().Turn_LeftOn()
	elif LR_Motion==1:
		LED_LR().Turn_RightOn()
	elif LR_Motion==2 :
		LED_LR().Turn_BothOn()
	elif LR_Motion==3 :
		LED_LR().Turn_Off()
	
		
	# Draw the Text on Frame
	# cv2.putText(cls.npframe, "Motion Status: {}".format(text),(10,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
        #showMydetections(cls.ffaceRects,cls.pfaceRects,cls.npframe)         
	#cv2.imshow("Motion Det", gray)
	#cv2.waitKey(50)

        #cv2.imshow("Motion thesh",thresh)
	#cv2.waitKey(50)

        
	cls.thread = None



def Left_Right(imsize, ffaceRects, pfaceRects, thresh):
	# Find the face
	#find max face Bounding box
	mfX = imsize[0]	
	tol = 0.01
	mxfX = 0
        if ffaceRects is None:
		if pfaceRects is None:
			return 3
	if ffaceRects is not None:
       	   for (fX, fY, fW, fH) in ffaceRects:
       	  	mfX  = max(5, min(fX-tol*imsize[0],mfX))
       	  	mxfX = min(imsize[0]-5,max(fX+tol*imsize[0]+fW,mxfX))
	if pfaceRects is not None:
	   for (fX, fY, fW, fH) in pfaceRects:
       		mfX = max(5, min(fX-tol*imsize[0],mfX))
       	  	mxfX = min(imsize[0]-5,max(fX+tol*imsize[0]+fW,mxfX)	)
	mfX	= int(mfX)
	mxfX	= int(mxfX)
	Lft = sum(map(sum,thresh[0:mfX,0:imsize[1]]))
	Rgt = sum(map(sum,thresh[mxfX:imsize[0],0:imsize[1]]))
	Lft = Lft/float(mfX*imsize[1])
	Rgt = Rgt/float((imsize[0]-mxfX)*imsize[1])
	#print "mfX:  %d , mxfX %d, Lft: %d, Rgt: %d" %(mfX, mxfX, Lft, Rgt)
		

	if Lft > Rgt*0.7:
		return 0
	elif Rgt > Lft*0.7:
		return 1
	else:
		return 2

	

def showMydetections(ffaceRects, pfaceRects, gray):
	if ffaceRects!=None:
		# loop over the face bounding boxes and draw them
        	for (fX, fY, fW, fH) in ffaceRects:
        		cv2.rectangle(gray, (fX, fY), (fX + fW, fY + fH), (0, 255,0),5)
	if pfaceRects!=None:
		for (fX, fY, fW, fH) in pfaceRects:
        		cv2.rectangle(gray, (fX, fY), (fX + fW, fY + fH), (0, 255,0),5)

	cv2.imshow("Motion Det",gray)
	cv2.waitKey(50)

	