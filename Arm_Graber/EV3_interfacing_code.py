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

import serial
import time
import EV3BT

EV3 = serial.Serial('/dev/rfcomm0')
s = EV3BT.encodeMessage(EV3BT.MessageType.Text, 'abc', 'Eat responsibly')
print(EV3BT.printMessage(s))
EV3.write(s)
time.sleep(1)
EV3.close()

'''
# Front claw interfacing

#set EV3 to bluetooth bus comm0
try:
    EV3 = serial.Serial('/dev/rfcomm0')

except OSError:
    print("EV3 Brick not found! Exiting...")
    exit()



#test recive message
print("Waiting for message")

try:
    s = EV3BT.encodeMessage(EV3BT.MessageType.Numeric, "Motor state", "1")
    print(EV3BT.printMessage(s))
    EV3.write(s)
    time.sleep(1)

except KeyboardInterrupt:
    print("aborted testing...")
    print("exiting...")
    pass

EV3.close()
'''