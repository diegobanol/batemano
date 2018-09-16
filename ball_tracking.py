# USAGE
# python ball_tracking.py

# import the necessary packages
from collections import deque			# Returns a new deque object initialized left-to-right 
from imutils.video import VideoStream	# Creates a video loop over frames
import numpy as np						# Library for the easy manage of arrays
import cv2								# library for image processing
import imutils							# library over cv2 for easy image manipulation
import time								# use for wait over time
import pygame							# We use this library for manipulate sounds

'''
Description: Put a circle with transparency over the original frame.
Params: x, y: The x, y coordinates of the circle center.
		r,g, b: The (r,g,b) value to paint the circle.
		lambdaValue: the loop frame counter.
		frame: The actual frame of the video loop.
Output: The frame eith the lambda circle painted
'''
def lambdaCircles(x, y, r, g, b, lambdaValue, frame):
	# starts copying the frame
	overlay = frame.copy()
	output = frame.copy()

	# draw a colored circle surrounding the x, y coordinates and 
	# the rgb value
	cv2.circle(overlay ,(x,y), 60, (r,g,b), -1)

	# apply the overlay
	cv2.addWeighted(overlay, lambdaValue, output, 1 - lambdaValue,
		0, output)

	return output


'''
Description: When a circle is active, this function turns on the flicker and the sound.
Params: Circle: Has the flags and values of the circle.
		r,g, b: The (r,g,b) value to paint the circle.
		loops: the loop frame counter.
		sound: The name of the sound in the folder.
Output: The actual value of the circle and the frame
'''
def turningOnCircles(circle, r, g, b, frame, loops, sound):
	if(circle['music']):
		# Each 25 frames the lambda value of the circle transparency
		# changes and altern between 0.2 and 0.8 lambda value
		if(loops%25==0):								
			circle['altern']=not(circle['altern'])
		if(circle['altern']):
			frame = lambdaCircles(circle['x'], circle['y'], r, g, b, 0.2, frame)
		else:
			frame = lambdaCircles(circle['x'], circle['y'], r, g, b, 0.8, frame)
		# If the music starts not replays again
		if(not(circle['isPlaying'])):
			sound.play(-1)				# starts the sound
			circle['isPlaying'] = True	# Tells the music starts to play
	else:
		# If the circle isnt turn the lambda value of the transparency is 0.5
		frame = lambdaCircles(circle['x'], circle['y'], r, g, b, 0.5, frame)
		# And if the music is playing stops the misuc
		if(circle['isPlaying']):
			sound.stop()
			circle['isPlaying'] = False
	return {'circle':circle, 'frame':frame}

'''
Description: Detects if the color detected are inside the circle.
Params: dx, dy: Diference between the x or y values (center of detected circle) and the 
			center of the lambda circle.
		R: the loop frame counter.
Output: boolean that indicates if the color detected is inside the circle
'''
def isInsideCircle(dx, dy, R):
	dx = abs(dx)			# Obtain the absolut value
	dy = abs(dy)
	if dx > R or dy >R:		# Compare respect the radius
		return False
	elif(dx + dy <= R): 	# Compare respect the vector
		return True
	elif(dx^2 + dy^2 <= R^2): # Compare respect the circle equation
		return True
	else:
		return False


'''
Description: State machine that represents the current state of each circle.
Params: circle: A set of flags for controls the state of the circle
		center: the x, y values of the center of the detected green circle.
Output: The current flags depending on the current state
'''
def activeTheCircle(circle, center):
	circle['isInside'] = isInsideCircle((center[0] - circle['x']), (center[1] - circle['y']), 60)
	if(circle['state']==1 and not(circle['isInside'])):
		circle['state']=1
		circle['music'] = False
	elif(circle['state']==1 and circle['isInside']):
		circle['state']=2
		circle['music']=True
	elif(circle['state']==2 and circle['isInside']):
		circle['state']=2
		circle['music']=True
	elif(circle['state']==2 and not(circle['isInside'])):
		circle['state']=3
		circle['music']=True
	elif(circle['state']==3 and not(circle['isInside'])):
		circle['state']=3
		circle['music']=True
	elif(circle['state']==3 and circle['isInside']):
		circle['state']=4
		circle['music']=False
	elif(circle['state']==4 and circle['isInside']):
		circle['state']=4
		circle['music']=False
	elif(circle['state']==4 and not(circle['isInside'])):
		circle['state']=1
		circle['music']=False
	else:
		circle['music']=False
	return circle


'''
Description: Do the logic over all the frames.
Params: loops: loop counter of passed frames
Output: No output
'''
def loopOverCamera(loops):

	# define the lower and upper boundaries of the "green"
	# ball in the HSV color space, then initialize the
	# list of tracked points
	greenLower = (29, 86, 6)
	greenUpper = (64, 255, 255)
	points = 64
	pts = deque(maxlen=points)

	# Defines the frequency of samples, The size argument represents how many bits are used for each audio sample.
	# chanels 2 defines the audio as stereo, buffer, The buffer argument controls the number of internal 
	# samples used in the sound mixer
	pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
	# Define sounds, with the specific name in the folder
	sound1 = pygame.mixer.Sound('Bass 1.wav')
	sound2 = pygame.mixer.Sound('DRUMS 3.wav')
	sound3 = pygame.mixer.Sound('SYNTH 1.wav')
	sound4 = pygame.mixer.Sound('SYNTH 2.wav')
	sound5 = pygame.mixer.Sound('Bass 1.wav')

	# Each circle: x, y: center, and the rest of values are flags for the game logic.
	circle1 = {'x': 320, 'y': 80, 'music': False, 'isInside': False, 'state': 1, 'altern': False, 'isPlaying': False}
	circle2 = {'x': 80, 'y': 80, 'music': False, 'isInside': False, 'state': 1, 'altern': False, 'isPlaying': False}
	circle3 = {'x': 550, 'y': 80, 'music': False, 'isInside': False, 'state': 1, 'altern': False, 'isPlaying': False}
	circle4 = {'x': 200, 'y': 400, 'music': False, 'isInside': False, 'state': 1, 'altern': False, 'isPlaying': False}
	circle5 = {'x': 440, 'y': 400, 'music': False, 'isInside': False, 'state': 1, 'altern': False, 'isPlaying': False}

	# Starts the video with reference
	# to the webcam
	vs = VideoStream(src=0).start()

	# allow the camera to warm up
	time.sleep(2.0)

	# keep looping
	while True:
		loops = loops+1	  # Increase d¿the loop counter
		frame = vs.read() # grab the current frame

		# resize the frame, blur it, and convert it to the HSV
		# color space
		frame = imutils.resize(frame, height=480, width=640) # resize image to 640x480
		
		# the original image is mirroed, the 1 value is for mirror respect the ABSCISSA		
		frame = cv2.flip( frame, 1 )	

		# Aply the gaussian blur to image the (11, 11) specify the standard deviation in X and Y direction
		# 0 dont do pixel strapolation
		blurred = cv2.GaussianBlur(frame, (11, 11), 0)

		# Transforms to HSV Color Space, to minimize dependence with color intensity
		hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

		# construct a mask for the color "green", then perform
		# a series of dilations and erosions to remove any small
		# blobs left in the mask
		mask = cv2.inRange(hsv, greenLower, greenUpper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)

		# find contours in the mask and initialize the current
		# (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]
		center = None

		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

			# only proceed if the radius meets a minimum size
			if radius > 50:
				# print "The radius is" + str(radius)
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
				cv2.circle(frame, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
				cv2.circle(frame, center, 5, (0, 0, 255), -1)
				# update the points queue
				pts.appendleft(center)

				# Current state of activated circles
				circle1 = activeTheCircle(circle1, center)
				circle2 = activeTheCircle(circle2, center)
				circle3 = activeTheCircle(circle3, center)
				circle4 = activeTheCircle(circle4, center)
				circle5 = activeTheCircle(circle5, center)

				# loop over the set of tracked points
				for i in range(1, len(pts)):
					# if either of the tracked points are None, ignore
					# them
					if pts[i - 1] is None or pts[i] is None:
						continue

					# otherwise, compute the thickness of the line and
					# draw the connecting lines
					thickness = int(np.sqrt(points / float(i + 1)) * 2.5)
					cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

		# Drawing circles, and turn on depending if the circle are active
		result = turningOnCircles(circle1, 0, 0, 255, frame, loops, sound1)
		circle1 = result['circle']
		frame = result['frame']
		result = turningOnCircles(circle2, 255, 0, 0, frame, loops, sound2)
		circle2 = result['circle']
		frame = result['frame']
		result = turningOnCircles(circle3, 255, 255, 0, frame, loops, sound3)
		circle3 = result['circle']
		frame = result['frame']
		result = turningOnCircles(circle4, 0, 255, 255, frame, loops, sound4)
		circle4 = result['circle']
		frame = result['frame']
		result = turningOnCircles(circle5, 255, 0, 255, frame, loops, sound5)
		circle5 = result['circle']
		frame = result['frame']
		
		# show the frame to our screen
		# print loops
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

		# if the 'q' key is pressed, stop the loop
		if key == ord("q"):
			break
			
	# otherwise, release the camera
	else:
		vs.release()

	# close all windows
	cv2.destroyAllWindows()	

if __name__== "__main__":
	loops = 0				# Loop counter over the video
	loopOverCamera(loops)