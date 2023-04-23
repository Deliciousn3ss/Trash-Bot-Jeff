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

# Import Scuttle Code and custom scripts
import L3_camdetector as camdetect
import L3_obsticalavoid as navigator

# Create Thread for camera detection
def loop_camdetect( ID ):
    camdetect.go()  # command the full program to run
        
# Create Thread for navigation
def loop_navigator( ID ):
    navigator.go() # command the full program to run

# ALL THREADS ARE CALLED TO RUN IN THE MAIN FUNCTION
def main():

        print("Waking Jeff....")
        threads = []  # create an object for threads

        t = threading.Thread( target=loop_camdetect, args=(1,) ) # make 1st thread object
        threads.append(t) # add this function to the thread object
        t.start() # start executing
        print("Camera:  Online... ")

        t2 = threading.Thread( target=loop_navigator, args=(2,) ) # make 2nd thread object
        threads.append(t2) # add this function to the thread object
        t2.start() # start executing
        print("Navigation System:  Online...")

        # the join commands manipulate the way the program concludes multithreading.
        t.join()
        t2.join()

        # finish setup
        print("JunkBot: Jeff Ready to go!")

# EXECUTE THE MAIN FUNCTION
main()