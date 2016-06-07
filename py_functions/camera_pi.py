import time
import io
import threading
import picamera
from picamera.array import PiRGBArray
import cv2
import numpy as np
from PIL import Image
import json
from led_lr_pigpio import LED_LR


class Camera(object):
    thread  = None  # background thread that reads frames from camera
    frame   = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    npframe = None 


    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
	
        self.initialize()
        return self.frame, self.npframe

      


    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            # camera setup
            conf  = json.load(open("./templates/conf.json"))
	    camera.resolution   = tuple(conf["resolution_raw"])
	    camera.framerate    = conf["stream_fps"]	    
            camera.hflip 	= False
            camera.vflip 	= False
            stream 		= PiRGBArray(camera)

            # let camera warm up
            #camera.start_preview()
            time.sleep(conf["camera_warmup_time"])

            
 	    for foo in camera.capture_continuous(stream,format="bgr",use_video_port=True):
		cls.npframe = foo.array                
                
		# stackoverflow.com/question/31077366/				
		cimage = io.BytesIO() 		              
		img = Image.fromarray(np.uint8(cv2.cvtColor(cls.npframe,cv2.COLOR_BGR2RGB)))
		#img = img.resize((320,280), Image.ANTIALIAS)
		img  = img.resize(tuple(conf["resolution_strm"]),Image.ANTIALIAS)
		img.save(cimage,format='JPEG')
		
		# store frame
		cimage.seek(0)		
		cls.frame = cimage.read()                
		
                # reset stream for next frame
		stream.seek(0)
                stream.truncate()
		
		cimage.seek(0)
		cimage.truncate()
		# if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread    
		if time.time() - cls.last_access > 100000:
		    LED_LR().Cleanup()
                    break

        cls.thread = None