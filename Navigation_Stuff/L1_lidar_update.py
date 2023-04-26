# This File performs the following:
# 1) grab a subset of the readings from the lidar for lightweight purposes
# 2) assign the proper angle value to the reading, with respect to robot x-axis
# 3) create a 2d array of [distances, angles] from the data

# Note: installation of pysicktim library is required for to run this program.
# perform "sudo pip3 install pyusb," then "sudo pip3 install pysicktim"

# Import external libraries
import csv
import numpy as np                                  # for array handling
import pysicktim as lidar                           # required for communication with TiM561 lidar sensor
import time                                         # for timekeeping
import math
import L2_vector as vector
import L1_log as log
import L1_motor as motor

pings = int(84)                                      #Amount of Points for lidar to scan

np.set_printoptions(suppress=True)                  # Suppress Scientific Notation
start_angle = -121.0                                # lidar points will range from -135 to 135 degrees, added a 14 degree offset to fix orientation

def csv_write(list):
    list = [str(i) for i in list]
    #save location "/tmp/excel_data.csv"
    with open('/home/pi/mxet300_lab/basics/log/lidar_data.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(list)
    csvFile.close()


def polarScan(num_points = pings):                       # You may request up to 811 points, max.

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

    return(scan_points)
    

def Coordinates(scan_points):   #Converts angles and distance
    coords = np.zeros([pings,2])
    
    for i in range(pings):
        
        #get angle
        #print(i)
        angle = lidarData[i,1] #[Row, Col]
        #get distance
        dist = lidarData[i,0]

        #Determines X and Y coordinates from distances and angles
        x = round(dist * math.cos((angle) * (math.pi/180)),3)
        y = round(dist * math.sin((angle) * (math.pi/180)),3)
         
        coords[i,0] = x
        coords[i,1] = y
    
    return(coords)
    
    
def Surroundings(lidarData):
    AreaCheck = 0
    RightArea = 0
    LeftArea = 0
    
    for i in range(len(lidarData)):
        Sdist = (lidarData[i,0])
        SAngle = (lidarData[i,1])
        
        if ((SAngle >= -80) & (SAngle <= -25)):
            RightArea += Sdist
            
        elif ((SAngle >= 25) & (SAngle <= 80)):
            LeftArea += Sdist
            
    if (RightArea > LeftArea):
        AreaCheck = -1
    elif (LeftArea > RightArea):
        AreaCheck = 1

    return(AreaCheck)
    
    
def Proximity(lidarData):
    #coords = np.zeros([])
    radar = [[1,0]]
    i = 0
    u = 0
    for i in range(pings):  #Check proximity of coordinate values that are within 0.6 meters of scuttle
        if ((((lidarData[i,0]) <= 0.9) & ((lidarData[i,0]) != 0.0))):     #If distance is within 0.6 m, flag value and determine coords (((lidarData[i,1]) <= 85) & ((lidarData[i,1]) >= -85))
            
            angle = lidarData[i,1] #[Row, Col]
            dist = lidarData[i,0]  #Distance won't be needed, but can be used to distinguish

            radar = radar + [[dist,angle]] #Adds point to list
            
    return(radar)
    
    
def avoidance(radar):   #Checks obstacles angle to determine relative to robot

    enable = 2 #Enables old condition tree for movement (0 = Debug, 1 = Old Routine, 2 = Default Routine)
    Front = 0
    Left = 0
    Right = 0
    Back = 0
    
    #Convert radar point list into array
    Radarray = np.array(radar)
    
    for i in range(len(Radarray)):
        #Extract values from array      *************************************************************
        dist = (Radarray[i,0])          #May be unneccary because distance is already less than 0.7m
        angle = (Radarray[i,1])
        
        #[Angles] See if robot is between two points
        if ((((dist <= 0.9) & (angle <= 33) & (angle >= -13))) & (Front != 1)): #Check Front Side [angle to -angle] about 30 deg
            Front = 1
            continue
        
        elif (((angle > 33) & (angle <= 94)) & (Left != 8)): #Check Left Side [angle to -angle] and severity 30 to 80 deg
            if (dist <= 0.45):
                Left = 8
            else:   #(dist <= 0.8):
                Left = 2
            continue
        
        elif (((angle < -13) & (angle >= -71)) & (Right != 16)): #Check Right Side [angle to -angle] and severity 
            if (dist <= 0.45):
                Right = 16
            else:   #(dist <= 0.8):
                Right = 4
            continue
        else:
            continue
        
    #Sum directional values to form the unique command using binary
    Area = Front + Left + Right

    if (enable == 2):
        if (Area == 0):
            motor.sendLeft(0.8)
            motor.sendRight(0.8)
        elif (Area == 1):     #Object in front                           #Determine which area to face based on amount of open space
            if (Surroundings(lidarData) == -1):  #More open area to Right
                motor.sendLeft(0.8)
                motor.sendRight(-0.8)
            elif (Surroundings(lidarData) == 1): #More open area to Left
                motor.sendLeft(-0.8)
                motor.sendRight(0.8)
            else:
                motor.sendLeft(0.0)
                motor.sendRight(0.0)
        elif (Area == 2):           #Object to the Left
            motor.sendLeft(0.8)
            motor.sendRight(0.8)
        elif (Area == 4):           #Object to the Right
            motor.sendLeft(0.8)
            motor.sendRight(0.8)
        elif (Area == 3):           #Object in front and to Left
            motor.sendLeft(0.8)
            motor.sendRight(-0.8)
        elif (Area == 5):           #Object in front and to Right
            motor.sendLeft(-0.8)
            motor.sendRight(0.8)
        elif ((Area == 7) or (Area == 25)):   #Surrounded by objects
                            #Determine which area to face based on amount of open space
            if (Surroundings(lidarData) == -1): #More open area to Right
                motor.sendLeft(0.8)
                motor.sendRight(-0.8)
            elif (Surroundings(lidarData) == 1): #More open area to Left
                motor.sendLeft(-0.8)
                motor.sendRight(0.8)
        elif (Area == 8):           #Object is Close to Left
            motor.sendLeft(0.8)
            motor.sendRight(0.0)
        elif (Area == 16):           #Object is Close to Right
            motor.sendLeft(0.0)
            motor.sendRight(0.8)
        elif (Area == 24):           #Passage is too Narrow
            motor.sendLeft(0.0)
            motor.sendRight(0.0)
        else:                       #No condition met, keep forward
            motor.sendLeft(0.0)
            motor.sendRight(0.0)
        
       
    elif (enable == 1):   #Old movement control
            
        if ((Front == 1) & (Left == 1) & (Right == 1)):     #Surrounded, reverse then turn
            motor.sendLeft(-0.8)
            motor.sendRight(-0.8)
            time.sleep(0.5)
            motor.sendLeft(0.8)
            motor.sendRight(-0.8)
        elif ((Front == 1) & (Left == 0) & (Right == 0)):   #Stop
            motor.sendLeft(0.4)
            motor.sendRight(0.8)
        elif ((Front == 1) & (Left == 1) & (Right == 0)):   #Rotate Right
            motor.sendLeft(0.8)
            motor.sendRight(-0.8)
        elif ((Front == 1) & (Left == 0) & (Right == 1)):   #Rotate Left
            motor.sendLeft(-0.8)
            motor.sendRight(0.8)
        elif ((Front == 0) & (Left == 1) & (Right == 0)):   #Keep straight if wall to Left
            motor.sendLeft(0.8)
            motor.sendRight(0.8)
        elif ((Front == 0) & (Left == 0) & (Right == 1)):   #Keep straight if wall to Right
            motor.sendLeft(0.8)
            motor.sendRight(0.8)
        else:
            motor.sendLeft(0.8)
            motor.sendRight(0.8)

    #debug displays
    print(Front)
    print(Left)
    print(Right)
        
    return()
    

if __name__ == "__main__":
    while (1):
        lidarData = polarScan(pings)
        #coords = Coordinates(lidarData)    #Converts all points into Coords
        radar = Proximity(lidarData)    #Captures only close points
        avoidance(radar)                #Finds objects positon relative to robot
        print("Refresh")
        #print(radar)
        #csv_write(coords) #Save coordinates in CSV
        time.sleep(0.25)
        
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
