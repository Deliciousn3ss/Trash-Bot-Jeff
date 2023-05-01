# Scan the room in a lawnmower path forever
# move robot forwards, turn right, move forwards, turn right
# move robot forwards, turn left, move forwards, turn left

#import LX code
import L2_speed_control as motor
import L2_compass_heading as compass
import L1_lidar as lidar
import numpy as npy
import threading

#setup a class for threading use
class Room_Scan(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print("Thread: " + self.name + "Started...")
        try:
            while(not wall):
                wall = lidar.polarScan(84)
                driveforwards()
            turnRight()
            driveforwards()
            turnRight()
            while(not wall):
                wall = lidar.polarScan(84)
                driveforwards()
            turnLeft()
            driveforwards()
            turnLeft()

        except threading.main_thread:
            #object detected or obstical in the way
            return 0

#wall distance 1.1m

def driveforwards():
    motor.driveClosedLoop()

def turnRight():
    motor.driveClosedLoop()

def turnLeft():
    motor.driveClosedLoop()

def stopRobit():
    motor.driveClosedLoop(0,0,0)


if __name__ == '__main__':
    Room_Scan.running()