# Scan the room in a lawnmower path forever

#import LX code
import L2_speed_control as motor
import numpy as npy

motor.driveClosedLoop(npy.array[0,0])
enabled = 1

if (enabled == 1):
    if (Area == 7):     #Surrounded, reverse then turn
        motor.sendLeft(BKD)
        motor.sendRight(BKD)
        time.sleep(0.5)
        motor.sendLeft(FWD)
        motor.sendRight(BKD)
    elif (Area == 1):   #Pivot
        motor.sendLeft(FWD)
        motor.sendRight(0.0)
    elif ((Area == 3) or (Area == 3.2)):   #Rotate Right
        motor.sendLeft(FWD)
        motor.sendRight(BKD)
    elif ((Area == 5) or (Area == 5.4)):        #Rotate Left
        motor.sendLeft(BKD)
        motor.sendRight(FWD)
    elif (Area == 2):   #Keep straight if wall to Left
        motor.sendLeft(FWD)
        motor.sendRight(FWD)
    elif (Area == 4):   #Keep straight if wall to Right
        motor.sendLeft(FWD)
        motor.sendRight(FWD)
    elif ((Area == 2.2) or (Area == 7.2)):   #Close to Left
        motor.sendLeft(FWD)
        motor.sendRight(0)
    elif ((Area == 4.4) or (Area == 7.4)):   #Close to Right
        motor.sendLeft(0)
        motor.sendRight(FWD)
    else:
        motor.sendLeft(FWD)
        motor.sendRight(FWD)