###############################
##      MXET 300 - 501       ##
##      Final Project:       ##
##                           ##
##      JunkBot-Jeff         ##
###############################

####   Main Python file    ###

# Import External extensions
import time as sleep
import threading # only use for threading functions
import os
import sys


print("Importing modules...")
import Object_Tracking_v2 as objTracker
import Proximity as navigator
#import Scan the room code as pinger
        
# Create Thread for navigation
def loop_navigator( ID ):
    navigator.go() # command the full program to run

# Create Thread for object tracking
def loop_Tracker( ID ):
    objTracker.go() # command the full program to run

# ALL THREADS ARE CALLED TO RUN IN THE MAIN FUNCTION
def main():

        print("Waking Jeff....")
        threads = []  # create an object for threads

        #setup and connect to EV3
        #os.system("sudo rfcomm connect hci0 00:16:53:3F:13:E9")
        print("Mindstorms EV3:  Online...")

        t1 = threading.Thread( target=loop_Tracker, args=(1,) ) # make 1st thread object
        threads.append(t1) # add this function to the thread object
        t1.start() # start executing
        print("Camera:  Online... ")
        sleep(0.5)
        print("Tracking system: Online... ")
        sleep(0.5)


        t2 = threading.Thread( target=loop_navigator, args=(2,) ) # make 2nd thread object
        threads.append(t2) # add this function to the thread object
        t2.start() # start executing
        print("Navigation System:  Online...")

        # the join commands manipulate the way the program concludes multithreading.
        t1.join()
        t2.join()


        # finish setup
        print("JunkBot: Jeff Ready to go!")

# EXECUTE THE MAIN FUNCTION
main()

#Lidar avoidance runs all the time and has priority


#Object tracking runs when there is no obstical


#Room scaner runs when there is no obsticals and no target.