#!/usr/bin/env python
from flask import Flask, render_template, Response, jsonify, send_file
import threading

# Raspberry Pi camera module (requires picamera package)
from camera_pi import Camera
from runface   import Runface
from motiondet import MotionDet

import json
import time
import numpy as np
from PIL import Image
import cv2
import os
import piexif
import io

#from PIL.ExifTags import TAGS
# Evelyn Boettcher
# DiDacTex, LLC 2016

app 		= Flask(__name__)
camera 		= Camera()
runFace 	= Runface()
motionDet 	= MotionDet()
framecount 	= 0

@app.route('/')
def index(): 
    """Video streaming home page."""
    return render_template('./files/index.html')


def gen(camera, facedet, movedet):
    """Video streaming generator functipython."""
    
    while True:
       frame, npframe = camera.get_frame()
	   saveStill(npframe)
		
        # Run Face???
        #det,ffaceRects, pfaceRects=facedet.get_detection(npframe)

        # Run Motions detections
        #movedet.get_movement(det,ffaceRects,pfaceRects,npframe)
      
       
       	yield (b'--frame\r\n'
               		b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
	
def stillCall(camera,facedet,movedet):		
        frame, npframe = camera.get_frame()
		saveStill(npframe)
			
        # Run Face???
        #det,ffaceRects, pfaceRects=facedet.get_detection(npframe)

        # Run Motions detections
        # movedet.get_movement(det,ffaceRects,pfaceRects,npframe)
      
       
	     
@app.route('/still_feed')
def still_feed():
    global camera
    global runFace
    global motionDet
    stillCall(camera, runFace,motionDet)
     
    #stackoverfloow.com/questions/11017466
    filename = "./files/stillimg.jpg"
    return send_file(filename,mimetype='image/jpeg')

@app.route('/video_feed')
def video_feed():    
    global camera
    global runFace
    global motionDet
    ## Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera, runFace,motionDet),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def saveStill(npframe):
	# Stave STill Image
	global lastStill
	global framecount
        	
	if 'lastStill' in globals():
		lastStill = lastStill
	else:
		lastStill = time.time()
		j=Image.fromarray(np.uint8(cv2.cvtColor(npframe,cv2.COLOR_BGR2RGB)))
		j.save("./files/stillimg.jpg", format='JPEG')	

	if time.time()-lastStill>0.6:
		lastStill = time.time()
		saveout = True
	else:
		saveout = False
	
	if saveout:
		# save out image
		#im = npframe.copy()
		#cv2.rectangle(im,(0,0),(85,20),(100,40,100),-1)
		#im_text =  str(framecount) + " Got Baby" 
		#cv2.putText(im,im_text,(10,15),cv2.FONT_HERSHEY_DUPLEX,.4,(0,0,0))
                
		j=Image.fromarray(np.uint8(cv2.cvtColor(npframe,cv2.COLOR_BGR2RGB)))
		j.save("./static/stillimg.jpg", format='JPEG')
		#framecount = framecount +1
		#if framecount== 10: 
		#	framecount=0
		
		#o = io.BytesIO()
		#thumb_im=j.copy();
		#thumb_im.thumbnail((50,50),Image.ANTIALIAS)
		#thumb_im.save(o,"jpeg")
		#thumbnail = o.getvalue()
		#DateTime = time.time()
		
		#zeroth_ifd	= {}
		#exif 		= {}
		#gps  		= {}
		#exif_dict = {"0th":zeroth_ifd, "Exif":exif, "GPS":gps,"thumbnail":thumbnail}
		#exif_dict["thumbnail"] = thumb_im
		#exif_dict["0th"][piexif.ImageIFD.ImageDescription]="Test for Got Baby"
		#exif_dict["0th"][piexif.ImageIFD.Copyright]="Test for Got Baby"

		#zeroth_ifd[piexif.ImageIFD.ImageDescription]="Test for Got Baby"
		#zeroth_ifd[piexif.ImageIFD.Copyright]="Test for Got Baby"
		#zeroth_ifd[piexif.ImageIFD.DateTime]=str(DateTime)
		#exif_dict = {"0th":zeroth_ifd, "Exif":exif, "GPS":gps,"thumbnail":thumbnail}
		#exif_bytes = piexif.dump(exif_dict)		


        	

@app.route('/json_det')
def json_det():
     global camera
     global runFace
     global MotionDet
     stillCall(camera, runFace,motionDet)
     f 	= open("./files/json_det.txt", 'r')
     status  = f.read()
     f.close()
     #print "Json call status: " + print(cls.det_list)status
     #status = '{"data":[{"status":" good", "time": "2020"}]}'
     return status

 
if __name__ == '__main__':
    os.system("sudo fuser -k 8082/tcp")
    os.system("sudo pigpiod")
    app.run(host='192.168.42.1', port=8082, debug=True, threaded=True)
    
    
