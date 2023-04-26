#! /usr/bin/env python3
#====================================#
#   LEGO Mindstorms EV3 Interfacer   #
#====================================#

## IMPORTANT_NOTE !!
# run the commands below to ensure bluetooth drivers and libraries are installed
'''
sudo apt-get update
sudo apt-get install bluetooth bluez libbluetooth-dev
sudo python3 -m pip install pybluez
'''

# if bluetooth is not working on the pi:
# systemctl start hciuart

# use this command to detect the 

import serial
import time
import EV3BT

Debug = 0

# Front claw interfacing

#set EV3 to bluetooth bus comm0
try:
    EV3 = serial.Serial('/dev/rfcomm0')

except OSError:
    print("EV3 Brick not found! Exiting...")
    exit()

def sendcommand(command)
    s = EV3BT.encodeMessage(EV3BT.MessageType.Numeric, "abc", int(key))
    if(Debug):
        print(EV3BT.printMessage(s))
    EV3.write(s)
    time.sleep(1)



if __name__ == "__main__":
    key = 0
    print("Manual control enabled...")
    print("enter numbers to control EV3 motors (1-4):")

    while(1):
        key = input()
        print(key)

        if(key == 9):
            print("exiting...")
            EV3.close()
            exit()
        else:
            s = EV3BT.encodeMessage(EV3BT.MessageType.Numeric, "abc", int(key))
            print(EV3BT.printMessage(s))
            EV3.write(s)
            time.sleep(1)




# #test recive message
# print("Waiting for message")

# try:
#     s = EV3BT.encodeMessage(EV3BT.MessageType.Numeric, "abc", "2")
#     print(EV3BT.printMessage(s))
#     EV3.write(s)
#     time.sleep(1)

# except KeyboardInterrupt:
#     print("aborted testing...")
#     print("exiting...")
#     pass

# EV3.close()