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
from Computer_Vision import Camera_Stream as objscan
from Computer_Vision import Target_Locator as objTracker
from Obstical_Avoidance import lidar_avoid as navigator


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
        try:
            os.system("sudo rfcomm connect hci0 00:16:53:3F:13:E9")
            print("Mindstorms EV3:  Online...")
        except:
            print("Error! Can't connect to the mindstorms!")
            print("Exiting...")
            sys.exit()

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