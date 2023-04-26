import L2_speed_control as sc
import L2_inverse_kinematics as ik
import L2_kinematics as kin
import cv2              # For image capture and processing
import numpy as np 


def objectTracking(cnts, width):

    size_w  = 240   # Resized image width. This is the image width in pixels.
    size_h = 160	# Resized image height. This is the image height in pixels.

    fov = 1         # Camera field of view in rad (estimate)

    target_width = 150      # Target pixel width of tracked object
    angle_margin = 0.025      # Radians object can be from image center to be considered "centered"
    width_margin = 10       # Minimum width error to drive forward/
    

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
            print("Aligning...")
            sc.driveOpenLoop(np.array([0.,0.]))             # Stop when centered and aligned
            

        fwd_effort = e_width/target_width                   
        
        wheel_speed = ik.getPdTargets(np.array([2.0*fwd_effort, -1.0*angle]))   # Find wheel speeds for approach and heading correction
        sc.driveClosedLoop(wheel_speed, wheel_measured, 0)  # Drive closed loop
        print("Angle: ", angle, " | Target L/R: ", *wheel_speed, " | Measured L\R: ", *wheel_measured)
        

    wheel_speed = ik.getPdTargets(np.array([0, -1.1*angle]))    # Find wheel speeds for only turning

    sc.driveClosedLoop(wheel_speed, wheel_measured, 0)          # Drive robot
    print("Angle: ", angle, " | Target L/R: ", *wheel_speed, " | Measured L\R: ", *wheel_measured)

  

        