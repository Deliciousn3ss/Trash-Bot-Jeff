# This File performs the following:
# 1) grab a subset of the readings from the lidar for lightweight purposes
# 2) assign the proper angle value to the reading, with respect to robot x-axis
# 3) create a 2d array of [distances, angles] from the data

# Note: installation of pysicktim library is required for to run this program.
# perform "sudo pip3 install pyusb," then "sudo pip3 install pysicktim"

# Import external libraries
import numpy as np                                  # for array handling
import pysicktim as lidar                           # required for communication with TiM561 lidar sensor
import time                                         # for timekeeping
import math
import threading
import L2_vector as vector
import L1_motor as motor

pings = int(84)                         #Amount of Points for lidar to scan

enable = 0 #Enables old condition tree for movement (0 = Debug, 1 = Old Routine, 2 = Default Routine)

np.set_printoptions(suppress=True)                  # Suppress Scientific Notation
start_angle = -121.0                                # lidar points will range from -135 to 135 degrees, added a 14 degree offset to fix orientation

def Proximity_Scan(num_points = pings):                       # You may request up to 811 points, max.

    lidar.scan()                                    # take reading

    # LIDAR data properties
    dist_amnt = lidar.scan.dist_data_amnt                               # Number of distance data points reported from the lidar
    angle_res = lidar.scan.dist_angle_res                               # Angular resolution reported from lidar

    # create the column of distances
    scan_points = np.asarray(lidar.scan.distances)                      # store the reported readings and cast as numpy.array
    inc_ang = (dist_amnt/(num_points+1))*angle_res                      # Calculate angle increment for scan_points resized to num_points
    scan_points = np.asarray(np.array_split(scan_points, num_points))   # Split array into sections
    scan_points = [item[0] for item in scan_points]                     # output first element in each section into a list
    scan_points = np.asarray(scan_points)                               # cast the list into an array
    scan_points = np.reshape(scan_points, (scan_points.shape[0], 1))    # Turn scan_points row into column

    # create the column of angles
    angles = np.zeros(num_points)
    x = len(angles)
    for i in range(x):
        angles[i] = (i*lidar.scan.dist_angle_res*lidar.scan.dist_data_amnt/num_points)+(start_angle)

    angles = np.reshape(angles, (angles.shape[0], 1))                   # Turn angles row into column

    # create the polar coordinates of scan
    scan_points = np.hstack((scan_points, angles))                      # Turn two (54,) arrays into a single (54,2) matrix
    scan_points = np.round(scan_points, 3)                              # Round each element in array to 3 decimal places


    radar = []
    i = 0
    u = 0
    for i in range(pings):  #Check proximity of coordinate values that are within 0.6 meters of scuttle
        if ((((scan_points[i,0]) <= 0.9) & ((scan_points[i,0]) >= 0.1))):     #If distance is within 0.6 m, flag value and determine coords (((lidarData[i,1]) <= 85) & ((lidarData[i,1]) >= -85))
            
            angle = scan_points[i,1] #[Row, Col]
            dist = scan_points[i,0]  #Distance won't be needed, but can be used to distinguish

            radar = radar + [[dist,angle]] #Adds point to list
            
#Checks obstacles angle to determine relative to robot
    Front = 0
    Left = 0
    Right = 0
    Back = 0
#Motor Speed/Direction
    FWD = 0.8
    BKD = -0.8
    
    #Convert radar point list into array
    Radarray = np.array(radar)
    
    for i in range(len(Radarray)):
        #Extract values from array      *************************************************************
        dist = (Radarray[i,0])          #May be unneccary because distance is already less than 0.7m
        angle = (Radarray[i,1])
        
        #[Angles] See if robot is between two points
        if (((angle <= 25) and (angle >= -5)) & (Front != 1)): #Check Front Side [angle to -angle] about 30 deg
            Front = 1
            continue
        
        elif (((angle > 25) and (angle <= 94)) & (Left != 2.2) & (dist <= 0.7)): #Check Left Side [angle to -angle] and severity 30 to 80 deg
            if (dist < 0.6 and ((angle > 25) and (angle <= 45))):
                Left = 2.2
            else:
                Left = 2
            continue
        
        elif (((angle < -5) and (angle >= -71)) & (Right != 4.4) & (dist <= 0.7)): #Check Right Side [angle to -angle] and severity 
            if ((dist < 0.6) and ((angle < -5) and (angle >= -25))):
                Right = 4.4 
            else:
                Right = 4
            continue
        
    #Sum directional values to form the unique command using binary
    Area = Front + Left + Right
       
    if (enable == 1):   #Old movement control
            
        if ((Front == 1) & (Left == 2) & (Right == 4)):     #Surrounded, reverse then turn
            motor.sendLeft(BKD)
            motor.sendRight(BKD)
            time.sleep(0.5)
            motor.sendLeft(FWD)
            motor.sendRight(BKD)
        elif ((Front == 1) & (Left == 0) & (Right == 0)):   #Stop
            motor.sendLeft(FWD)
            motor.sendRight(0.0)
        elif ((Front == 1) & ((Left == 2) or (Left == 2.2)) & (Right == 0)):   #Rotate Right
            motor.sendLeft(FWD)
            motor.sendRight(BKD)
        elif ((Front == 1) & (Left == 0) & ((Right == 4) or (Right == 4.4))):   #Rotate Left
            motor.sendLeft(BKD)
            motor.sendRight(FWD)
        elif ((Front == 0) & (Left == 2) & (Right == 0)):   #Keep straight if wall to Left
            motor.sendLeft(FWD)
            motor.sendRight(FWD)
        elif ((Front == 0) & (Left == 0) & (Right == 4)):   #Keep straight if wall to Right
            motor.sendLeft(FWD)
            motor.sendRight(FWD)
        elif (((Front == 0) & (Left == 2.2) & (Right == 0)) or ((Front == 1) & (Left == 2.2) & (Right == 4))):   #Close to Left
            motor.sendLeft(FWD)
            motor.sendRight(0)
        elif (((Front == 0) & (Left == 0) & (Right == 4.4)) or ((Front == 1) & (Left == 2) & (Right == 4.4))):   #Close to Right
            motor.sendLeft(0)
            motor.sendRight(FWD)
        else:
            motor.sendLeft(FWD)
            motor.sendRight(FWD)
            
    if (enable == 2):   #New proximity
            
        if ((Area == 7) or (Area == 8.2)):     #Surrounded, reverse then turn
            print("Surrounded")
        elif ((Front == 1) & (Left == 0) & (Right == 0)):   #Stop
            print("Object in Front")
        elif ((Front == 1) & ((Left == 2) or (Left == 2.2)) & (Right == 0)):   #Rotate Right
            print("Object to Front/Left Corner")
        elif ((Front == 1) & (Left == 0) & ((Right == 4) or (Right == 4.4))):   #Rotate Left
            print("Object to Front/Right Corner")
        elif ((Front == 0) & (Left == 2) & (Right == 0)):   #Keep straight if wall to Left
            print("Object to Left")
        elif ((Front == 0) & (Left == 0) & (Right == 4)):   #Keep straight if wall to Right
            print("Object to Right")
        elif ((Front == 0) & (Left == 2.2) & (Right == 0)):   #Close to Left
            print("Object Close Left")
        elif ((Front == 0) & (Left == 0) & (Right == 4.4)):   #Close to Right
            print("Object Close Right")
        else:
            print("No Object")

    #debug displays
    #print(Front)
    #print(Left)
    #print(Right)
        
    return(Area)    #Return Current Surroundings
    

if __name__ == "__main__":
    while (1):
        Area = Proximity_Scan(pings)    #Performs Entire Lidar Scan then state objects positon relative to robot
        print("Refresh")
        print(Area)
        time.sleep(0.2)
        
'{x: 0.5, y: -0.25, r: 5},\
{x: 0.5, y: 0.25, r: 5},\
{x: -0.1, y: 0.25, r: 5},\
{x: -0.1, y: -0.25, r: 5},\
{x: 0.2, y: -0.25, r: 5},\
{x: 0.2, y: 0.25, r: 5},\
{x: 0.5, y: 0.0, r: 5},\
{x: -0.1, y: 0.0, r: 5},\
{x: 0.05, y: 0.25, r: 5},\
{x: 0.05, y: -0.25, r: 5},\
{x: 0.35, y: 0.25, r: 5},\
{x: 0.35, y: -0.25, r: 5},'
