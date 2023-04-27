# Camera image processing code

import cv2          #for image capturing and processing
import numpy as np
import L2_speed_control as sc
import L2_inverse_kinematics as ik
import L2_kinematics as kin
import netifaces as ni
from time import sleep
from math import radians, pi

# Default Global Camera 


# Gets IP to grab MJPG stream
def getIp():
    for interface in ni.interfaces()[1:]:   #For interfaces eth0 and wlan0
    
        try:
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            return ip
            
        except KeyError:                    #We get a KeyError if the interface does not have the info
            continue                        #Try the next interface since this one has no IPv4
        
    return 0

# Setup default parameters for camera streaming
def CameraSetup():
    stream_ip = getIp()
    if not stream_ip: 
        print("Failed to get IP for camera stream")
        exit()

    camera_input = 'http://' + stream_ip + ':8090/?action=stream'   # Address for stream

    size_w  = 240   # Resized image width. This is the image width in pixels.
    size_h = 160	# Resized image height. This is the image height in pixels.

    fov = 1         # Camera field of view in rad (estimate)

    #    Color Range, described in HSV
    v1_min = 0      # Minimum H value
    v2_min = 100     # Minimum S value
    v3_min = 195      # Minimum V value

    v1_max = 135     # Maximum H value
    v2_max = 255    # Maximum S value
    v3_max = 255    # Maximum V value

    target_width = 100      # Target pixel width of tracked object
    angle_margin = 0.2      # Radians object can be from image center to be considered "centered"
    width_margin = 10       # Minimum width error to drive forward/back

    # Try opening camera with default method
    try:
        camera = cv2.VideoCapture(0)    
    except: pass

    # Try opening camera stream if default method failed
    if not camera.isOpened():
        camera = cv2.VideoCapture(camera_input)    

    camera.set(3, size_w)                       # Set width of images that will be retrived from camera
    camera.set(4, size_h)                       # Set height of images that will be retrived from camera

