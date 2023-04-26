###############################
##      MXET 300 - 501       ##
##      Final Project:       ##
##                           ##
##      JunkBot-Jeff         ##
###############################

####   Main Python file    ###

# Import External extensions
import time
import threading # only use for threading functions
import os
import sys


print("Importing modules...")
#import everything from Computer_Vision_Stuff
import Computer_Vision_Stuff.Object_Scan as objscan
import Computer_Vision_Stuff.Object_Tracking as objTracker
import Computer_Vision_Stuff.L2_speed_control
import Computer_Vision_Stuff.L1_motor
#import Computer_Vision_Stuff


import Navigation_Stuff.lidar_driving as navigator


# Create Thread for camera detection
def loop_objscan( ID ):
    objscan.go()  # command the full program to run
        
# Create Thread for navigation
def loop_navigator( ID ):
    navigator.go() # command the full program to run

def loop_Tracker( ID ):
    objTracker.go() # command the full program to run

# ALL THREADS ARE CALLED TO RUN IN THE MAIN FUNCTION
def main():

        print("Waking Jeff....")
        threads = []  # create an object for threads

        #setup and connect to EV3
        os.system("sudo rfcomm connect hci0 00:16:53:3F:13:E9")
        print("Mindstorms EV3:  Online...")

        t1 = threading.Thread( target=loop_objscan, args=(1,) ) # make 1st thread object
        threads.append(t1) # add this function to the thread object
        t1.start() # start executing
        print("Camera:  Online... ")

        t2 = threading.Thread( target=loop_navigator, args=(2,) ) # make 2nd thread object
        threads.append(t2) # add this function to the thread object
        t2.start() # start executing
        print("Navigation System:  Online...")

        t3 = threading.Thread( target=loop_Tracker, args=(3, ) ) # make 3rd thread object
        threads.append(t3) # add this function to the thread object
        t3.start() # start executing
        print("Object Tracking System:  Online...")

        # the join commands manipulate the way the program concludes multithreading.
        t1.join()
        t2.join()
        t3.join()


        # finish setup
        print("JunkBot: Jeff Ready to go!")

# EXECUTE THE MAIN FUNCTION
main()