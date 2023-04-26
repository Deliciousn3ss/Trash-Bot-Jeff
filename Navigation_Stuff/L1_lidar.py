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

np.set_printoptions(suppress=True)                  # Suppress Scientific Notation
start_angle = -135.0                                # lidar points will range from -135 to 135 degrees

def csv_write(list):
    list = [str(i) for i in list]
    #save location "/tmp/excel_data.csv"
    with open('/home/pi/mxet300_lab/basics/log/lidar_data.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(list)
    csvFile.close()


def polarScan(num_points=54):                       # You may request up to 811 points, max.

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
    coords = np.zeros([54,2])
    
    #print(type(lidar))
    for i in range(54):
        
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
    
def Proximity(lidarData):
    #coords = np.zeros([])
    radar = []
    #Check proximity of coordinate values that are within 0.6 meters of scuttle
    i = 0
    u = 0
    for i in range(54):
        if (((lidarData[i,0]) <= 0.6) & ((lidarData[i,0]) != 0.0)):     #If distance is within 0.6 m, flag value and determine coords
            
            angle = lidarData[i,1] #[Row, Col]
            dist = lidarData[i,0]

            radar = radar + [[dist,angle]] #Adds point to list
            
    return(radar)
    
def avoidance(radar):   #Checks obstacles angle to determine relative to robot
    
    Front = 0
    Left = 0
    Right = 0
    Back = 0
    
    #print(obstacles)
    Radarray = np.array(radar)
    
    for i in range(len(Radarray)):
        #print("Scanning")

        dist = (Radarray[i,0])
        angle = (Radarray[i,1])
        

        #[(x,y)] See if robot is between two points
        if (((dist < 0.6) & ((angle <= 30) & (angle >= -30)))): #Check Front Side [dist, angle to -angle]
            Front = 1

        elif (((dist < 0.6) & ((angle > 30) & (angle <= 80)))): #Check Left Side [-dist to dist, angle]
            Left = 1

        elif (((dist < 0.6) & ((angle < -30) & (angle >= -80)))): #Check Right Side [-dist to dist, -angle]
            Right = 1


            
    if ((Front == 1) & (Left == 1) & (Right == 1)):
        motor.sendLeft(0.0)
        motor.sendRight(0.0)
    elif ((Front == 1) & (Left == 0) & (Right == 0)):
        motor.sendLeft(0.4)
        motor.sendRight(0.8)
    elif ((Front == 1) & (Left == 1) & (Right == 0)):
        motor.sendLeft(0.8)
        motor.sendRight(-0.8)
    elif ((Front == 1) & (Left == 0) & (Right == 1)):
        motor.sendLeft(-0.8)
        motor.sendRight(0.8)
    elif ((Front == 0) & (Left == 1) & (Right == 0)):
        motor.sendLeft(0.8)
        motor.sendRight(0.8)
    elif ((Front == 0) & (Left == 0) & (Right == 1)):
        motor.sendLeft(0.8)
        motor.sendRight(0.8)
    else:
        motor.sendLeft(0.8)
        motor.sendRight(0.8)
            
            
    print(Front)
    print(Left)
    print(Right)
        
    
    return()
    

if __name__ == "__main__":
    while (1):
        lidarData = polarScan(54)
        #coords = Coordinates(lidarData)    #Converts all points into Coords
        radar = Proximity(lidarData)    #Captures only close points
        avoidance(radar)                #Finds objects positon relative to robot
        print("Refresh")
        #print(radar)
        #csv_write(coords) #Save coordinates in CSV
        time.sleep(0.5)
        
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
