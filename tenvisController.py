import time , sys , numpy , cv2
import numpy as np
import imutils
import smtplib


import securityDetails


class TenvisVideo():

	def __init__( self ):

		
		w_IP = securityDetails.w_R_IP
		w_Port = securityDetails.w_PORT
		w_UN = securityDetails.w_USER
		w_Pass = securityDetails.w_PASS

		self.feed_url = "http://" + w_IP + ":" + w_Port + "/vjpeg.v?user=" + w_UN + "&pwd=" + w_Pass
		print self.feed_url

		self.startMotionTime = None
		self.totalMotionTime = 0
		self.totalMotionAcceptable = 25
		self.alertLevel = 0
		self.alertLevelAcceptable = 3
		
		self.w_Capture = cv2.VideoCapture(self.feed_url)

		self.motionTracking2()

	def sendEmail( self , alertLevel , msg ):

        	FROM = securityDetails.fromEmail 
        	TO = securityDetails.toEmail

	        message = """From: %s\nTo: %s\nSubject: %s\n\n%s """ % (FROM, ", ".join(TO) , alertLevel , msg )

        	try:
                	server = smtplib.SMTP( "smtp.gmail.com" , 587 )
                	server.ehlo()
                	server.starttls()
                	server.login( FROM , securityDetails.emailPass  )
                	server.sendmail( FROM , TO , msg )
                	server.close()
                	print('sent email')
        	except:
                	print('failed to send email')

	def cleanup(self):
		self.w_Capture.release()
		cv2.destroyAllWindows()



	def motionTracking2( self ):

		avg = None
		firstFrame = None

		min_area = 500
		delta_thresh = 5

		motionCounter = 0
		min_motion_frames = 1

		while True:

			( grabbed , frame ) = self.w_Capture.read()
			text = "No Motion"

			if not grabbed:
				break

			frame = imutils.resize( frame , width = 500 )
			gray = cv2.cvtColor( frame , cv2.COLOR_BGR2GRAY )
			gray = cv2.GaussianBlur( gray , ( 21 , 21 ) , 0 )

			if firstFrame is None:
				firstFrame = gray
				continue

			if avg is None:
				avg = gray.copy().astype("float")
				continue

			cv2.accumulateWeighted( gray , avg , 0.5 )
			frameDelta = cv2.absdiff( gray , cv2.convertScaleAbs(avg) )

			thresh = cv2.threshold( frameDelta , delta_thresh , 255 , cv2.THRESH_BINARY )[1]
			thresh = cv2.dilate( thresh , None , iterations=2 )
			(image , cnts , _ ) = cv2.findContours( thresh.copy() , cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE )

			for c in cnts:

				if cv2.contourArea( c ) < min_area:
					continue

				(x, y, w, h) = cv2.boundingRect(c)
				cv2.rectangle( frame , ( x , y ) , ( x + w , y + h ) , ( 0, 255 , 0 ) , 2 )
				text = "Motion"
				
				if self.startMotionTime is None:
					self.startMotionTime = time.time()


			cv2.putText( frame , "Room Status: {}".format(text) , ( 10 , 20 ) , cv2.FONT_HERSHEY_SIMPLEX , 0.5 , (0, 0, 255) , 2 )

			if text == "Motion":

				motionCounter += 1

				if motionCounter >= min_motion_frames:

					done = time.time()
					totalMotionTime = done - self.startMotionTime
					totalMotionTime = int(totalMotionTime) % 60
					self.totalMotionTime = self.totalMotionTime + totalMotionTime

					#cv2.imshow( "Security Feed" , frame )
					#cv2.imshow( "Thresh" , thresh )
					#cv2.imshow( "Frame Delta" , frameDelta )

					motionCounter = 0
					

			else:
				motionCounter = 0


			if self.totalMotionTime > self.totalMotionAcceptable:
				self.alertLevel = self.alertLevel + 1
				self.totalMotionTime = 0
				self.startMotionTime = None
				
			if self.alertLevel > self.alertLevelAcceptable:
				sMesg = "haley is moving ALERT_LEVEL = " + str(self.alertLevel)
				self.sendEmail( "ALERT"  , sMesg )	
				self.alertLevel = 0

			k = cv2.waitKey(30) & 0xff
			if k == 27:
				break
			

		self.cleanup()








