import L1_lidar as lidar
import L1_motor as motor
import L2_speed_control as sc
import L2_inverse_kinematics as ik
import L2_kinematics as kin
import L2_vector as vector
import netifaces as ni
import cv2              # For image capture and processing
import numpy as np 
import threading
from time import sleep
from math import radians, pi
from array import *   

def objectScanner(colortarget):    #Blue = 0, Orange = 1, Green = 2

    HSV =   [[[55,45,125],[255,255,255]],           
            [[0,90,195],[255,255,255]],
            [[45,50,110],[255,255,255]]]
    
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

    try:
        camera = cv2.VideoCapture(0)    
    except: pass

    # Try opening camera stream if default method failed
    if not camera.isOpened():
        camera = cv2.VideoCapture(camera_input)    

    camera.set(3, size_w)                       # Set width of images that will be retrived from camera
    camera.set(4, size_h)                       # Set height of images that will be retrived from camera

    aligned = 0
    while TRUE:

        ret, image = camera.read()  # Get image from camera

        # Make sure image was grabbed
        if not ret:
            print("Failed to retrieve image!")

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
                angle = round(((center[0]/width)-0.5)*fov, 3)           # angle of vector towards target center from camera, where 0 deg is centered

                wheel_measured = kin.getPdCurrent()                     # Wheel speed measurements

                # If robot is facing target
                if abs(angle) < angle_margin:                                 
                    e_width = target_width - w                          # Find error in target width and measured width

                    # If error width is within acceptable margin
                    if abs(e_width) < width_margin:
                        sc.driveOpenLoop(np.array([0.,0.]))             # Stop when centered and aligned
                        print("Aligned! ",w)
                        aligned = 1
                        #Add an interrupt here once aligned

                        #Move forward and dynamically track the object
        else:
            #Scuttle Object avoidance function

            #Opt 2: Thread the processes of Scanning and Object avoidance.
            return

def getIp():
    for interface in ni.interfaces()[1:]:   #For interfaces eth0 and wlan0
    
        try:
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            return ip
            
        except KeyError:                    #We get a KeyError if the interface does not have the info
            continue                        #Try the next interface since this one has no IPv4
        
    return 0

if __name__ == '__main__':
    objectScanner()                       

#blue ball
#v1_min = 55      # Minimum H value
#v2_min = 45     # Minimum S value
#v3_min = 125      # Minimum V value

#v1_max = 255     # Maximum H value
#v2_max = 255    # Maximum S value
#v3_max = 255    # Maximum V value


#orange ball
#v1_min = 0      # Minimum H value
#v2_min = 90     # Minimum S value
#v3_min = 195      # Minimum V value

#v1_max = 255     # Maximum H value
#v2_max = 255    # Maximum S value
#v3_max = 255    # Maximum V value

#green ball
#v1_min = 45      # Minimum H value
#v2_min = 50     # Minimum S value
#v3_min = 110      # Minimum V value

#v1_max = 255     # Maximum H value
#v2_max = 255    # Maximum S value
#v3_max = 255    # Maximum V value