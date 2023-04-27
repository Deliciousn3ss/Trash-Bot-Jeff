import cv2              # For image capture and processing
import numpy as np      
import L2_speed_control as sc
import L2_inverse_kinematics as ik
import L2_kinematics as kin
import netifaces as ni
from time import sleep
from math import radians, pi

# Gets IP to grab MJPG stream
def getIp():
    for interface in ni.interfaces()[1:]:   #For interfaces eth0 and wlan0
    
        try:
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            return ip
            
        except KeyError:                    #We get a KeyError if the interface does not have the info
            continue                        #Try the next interface since this one has no IPv4
        
    return 0
    
#    Camera
stream_ip = getIp()
if not stream_ip: 
    print("Failed to get IP for camera stream")
    exit()

camera_input = 'http://' + stream_ip + ':8090/?action=stream'   # Address for stream

size_w  = 240   # Resized image width. This is the image width in pixels.
size_h = 160	# Resized image height. This is the image height in pixels.

fov = 1         # Camera field of view in rad (estimate)

target_width = 100      # Target pixel width of tracked object
angle_margin = 0.2      # Radians object can be from image center to be considered "centered"
width_margin = 10       # Minimum width error to drive forward/back

HSV =   [[[90,135,50],[130,230,235]],           
            [[5,90,170],[50,255,255]],
            [[45,50,105],[90,255,250]]]

def objectTracking(colortarget):

# Try opening camera with default method
    try:
        camera = cv2.VideoCapture(0)    
    except: pass

    # Try opening camera stream if default method failed
    if not camera.isOpened():
        camera = cv2.VideoCapture(camera_input)    

    camera.set(3, size_w)                       # Set width of images that will be retrived from camera
    camera.set(4, size_h)                       # Set height of images that will be retrived from camera
    aligned = 0

    try:
        while True:
            sleep(.05)                                          
        
            while(aligned == 0):
                ret, image = camera.read()

                if not ret:
                    print("Failed to retrieve image...")
                    break

                image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)              # Convert image to HSV

                height, width, channels = image.shape                       # Get shape of image

                thresh = cv2.inRange(image, (HSV[colortarget][0][0], HSV[colortarget][0][1], HSV[colortarget][0][2]),
            (HSV[colortarget][1][0], HSV[colortarget][1][1], HSV[colortarget][1][2]))   # Find all pixels in color range
                kernel = np.ones((5,5),np.uint8)                            # Set kernel size
                mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)     # Open morph: removes noise w/ erode followed by dilate
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)      # Close morph: fills openings w/ dilate followed by erode
                cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)[-2]                        # Find closed shapes in image
                
                if len(cnts) and len(cnts) < 3:                             # If more than 0 and less than 3 closed shapes exist

                    c = max(cnts, key=cv2.contourArea)                      # return the largest target area
                    x,y,w,h = cv2.boundingRect(c)                           # Get bounding rectangle (x,y,w,h) of the largest contour
                    center = (int(x+0.5*w), int(y+0.5*h))                   # defines center of rectangle around the largest target area
                    angle = round(((center[0]/width)-0.5)*fov, 3)           # % away from the center -- angle of vector towards target center from camera, where 0 deg is centered
                    
                    wheel_measured = kin.getPdCurrent() 

                    wheel_speed = ik.getPdTargets(np.array([0, -1.1*angle]))    # Find wheel speeds for only turning
                    
                    print("Aligning...")
                    sc.driveClosedLoop(wheel_speed, wheel_measured, 0)  # Drive closed loop
                    print("Angle: ", angle, " | Target L/R: ", *wheel_speed, " | Measured L\R: ", *wheel_measured)

                    if(abs(angle) < angle_margin):
                        print("Aligned!")
                        sc.driveOpenLoop(np.array([0.,0.]))         
                        aligned = 1
                    
                else:
                    print("No targets...")


            while(aligned == 1):

                ret, image = camera.read()

                if not ret:
                    print("Failed to retrieve image...")
                    break

                image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)              # Convert image to HSV

                height, width, channels = image.shape                       # Get shape of image

                thresh = cv2.inRange(image, (HSV[colortarget][0][0], HSV[colortarget][0][1], HSV[colortarget][0][2]),
            (HSV[colortarget][1][0], HSV[colortarget][1][1], HSV[colortarget][1][2]))   # Find all pixels in color range
                kernel = np.ones((5,5),np.uint8)                            # Set kernel size
                mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)     # Open morph: removes noise w/ erode followed by dilate
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)      # Close morph: fills openings w/ dilate followed by erode
                cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)[-2]                        # Find closed shapes in image
                
                if len(cnts) and len(cnts) < 3:                             # If more than 0 and less than 3 closed shapes exist

                    c = max(cnts, key=cv2.contourArea)                      # return the largest target area
                    x,y,w,h = cv2.boundingRect(c)                           # Get bounding rectangle (x,y,w,h) of the largest contour
                    center = (int(x+0.5*w), int(y+0.5*h))                   # defines center of rectangle around the largest target area
                    angle = round(((center[0]/width)-0.5)*fov, 3)           # % away from the center -- angle of vector towards target center from camera, where 0 deg is centered
                    
                    e_width = target_width - w                          # Find error in target width and measured width
                    fwd_effort = e_width/target_width
                    
                    wheel_measured = kin.getPdCurrent() 
                    
                    print("Moving forward...")
                    wheel_speed = ik.getPdTargets(np.array([0.8*fwd_effort, -0.5*angle]))   # Find wheel speeds for approach and heading correction
                    sc.driveClosedLoop(wheel_speed, wheel_measured, 0)  # Drive closed loop
                    print("Angle: ", angle, " | Target L/R: ", *wheel_speed, " | Measured L\R: ", *wheel_measured)

                    if(abs(angle) > angle_margin):
                        print("No longer aligned...")
                        sc.driveOpenLoop(np.array([0.,0.]))         
                        aligned = 0

                    if(abs(e_width) < 10):
                        print("Object obtained!")
                        sc.driveOpenLoop(np.array([0.,0.]))         
                        break
                    
                else:
                    print("No targets...")
            

    except KeyboardInterrupt:
        pass

    finally:
        print("Exiting object tracking...")

    return