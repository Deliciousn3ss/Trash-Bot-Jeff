import cv2              # For image capture and processing
import numpy as np      
import L2_speed_control as sc
import L2_inverse_kinematics as ik
import L2_kinematics as kin
import netifaces as ni
from time import sleep
from math import radians, pi
import EV3_interfacing_code as grabber
import L1_lidar_update as avoidance
import L2_compass_heading as compass
import L1_motor as m


pings = int(84)

#To run this, do sudo python3 

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

#Blue = 0, Orange = 1, Green = 2
HSV =   [[[90,135,50],[130,230,235]],           
            [[5,90,170],[50,255,255]],
            [[45,50,105],[90,255,250]],
            [[150,20,130],[205,255,255]]]

def objectTracking(colortarget, distance): #Distance 310 for ball , 100 for home

    size_w  = 240   # Resized image width. This is the image width in pixels.
    size_h = 160	# Resized image height. This is the image height in pixels.

    fov = 1         # Camera field of view in rad (estimate)

    target_width = distance     # Target pixel width of tracked object
    angle_margin = 0.2      # Radians object can be from image center to be considered "centered"
    width_margin = 10       # Minimum width error to drive forward/back

    Turncounter = 0

# Try opening camera with default method
    try:
        camera = cv2.VideoCapture(0)    
    except: pass

    # Try opening camera stream if default method failed
    if not camera.isOpened():
        camera = cv2.VideoCapture(camera_input)    

    camera.set(3, size_w)                       # Set width of images that will be retrived from camera
    camera.set(4, size_h)                       # Set height of images that will be retrived from camera
    state = 0

    try:
        while True:

            sleep(.05)                                          
        
            while(state == 0): #Aligning
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
                    
                    print("State 1: Aligning...")
                    sc.driveClosedLoop(wheel_speed, wheel_measured, 0)  # Drive closed loop
                    print("Angle: ", angle, " | Target L/R: ", *wheel_speed, " | Measured L\R: ", *wheel_measured)

                    if(abs(angle) < angle_margin):
                        print("Aligned!")
                        sc.driveOpenLoop(np.array([0.,0.]))
                        state = 1
                else:
                    print("No targets...")


            while(state == 1): #Forward
                sleep(0.025)
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
                    
                    print("State 2: Moving forward...")
                    wheel_speed = ik.getPdTargets(np.array([0.4*fwd_effort, -0.5*angle]))   # Find wheel speeds for approach and heading correction
                    sc.driveClosedLoop(wheel_speed, wheel_measured, 0)  # Drive closed loop
                    print("Angle: ", angle, " | Target L/R: ", *wheel_speed, " | Measured L\R: ", *wheel_measured)

                    if(abs(angle) > angle_margin):
                        print("No longer aligned...")
                        sc.driveOpenLoop(np.array([0.,0.]))         
                        state = 0

                    print(e_width)
                    if((e_width < 10) & (e_width > -1) & (colortarget < 3) ):
                        print("stopping motor..")
                        sc.driveOpenLoop(np.array([0,0])) 
                        sleep(0.5)
                        print("object in claw")
                        #Grab
                        grabber.sendcommand(2)  #Grab ball
                        print("object obtained")
                        sleep(3)
                        grabber.sendcommand(1)
                        print("object dropped")
                        sleep(1)
                        #Drop ball
                        break

                    if((e_width < 10) & (colortarget > 2)):
                        initheading = compass.get_heading()
                        state = 2
                    
                    
                else:
                    print("No targets...")
                    sc.driveOpenLoop(np.array([0,0]))

            while(state == 2):
                print("Turning...")
                target_heading = initheading + 180
                e_heading = 1
                headingstate = 0
                while(e_heading > 0):
                    currentheading = compass.get_heading()
                    e_heading = ((currentheading / target_heading))  #convert to radians
                    wheel_measured = kin.getPdCurrent() 

                    wheel_speed = ik.getPdTargets(np.array([0, -1.1*e_heading]))    # Find wheel speeds for only turning
                    if(abs(target_heading - currentheading) < 5):
                        print("State 2: Error heading:", e_heading, "Target heading:", target_heading, "Current heading:", currentheading)
                        sc.driveClosedLoop(wheel_speed, wheel_measured, 0)  # Drive closed loop
                        print("Angle: ", currentheading, " | Target L/R: ", *wheel_speed, " | Measured L\R: ", *wheel_measured)

                        if((currentheading/target_heading) > 0.95):
                            headingstate = 1
                            continue

                    if(headingstate == 1):
                        m.sendLeft(-0.8)
                        m.sendRight(-0.8)
                        sleep(1)
                        m.sendLeft(0)
                        m.sendRight(0)
                        grabber.sendcommand(3) #Raise gate
                        sleep(1)
                        m.sendLeft(0.8)
                        m.sendRight(0.8)
                        sleep(1)
                        m.sendLeft(0)
                        m.sendRight(0)
                        grabber.sendcommand(4) #Drop gate

                break


                
                


                    

    except KeyboardInterrupt:
        pass

    finally:
        print("Exiting object tracking...")

    return

if __name__ == '__main__':
    objectTracking(colortarget=3, distance=290)
    #Blue = 0, Orange = 1, Green = 2  

#Pink min[150,20,130] max[205,255,255]