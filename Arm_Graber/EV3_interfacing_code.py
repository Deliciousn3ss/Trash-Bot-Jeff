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

import bluetooth
import serial
import time


# Front claw interfacing

#set EV3 to bluetooth bus comm0
try:
    EV3 = serial.Serial('/dev/rfcomm0')

except ValueError:
    print("EV3 Brick not found! Exiting...")



#test recive message
print("Waiting for message")

try:
    while 1:
        n = EV3.in_waiting()
        if(n != 0):
            s = EV3.read(n)
            for n in s:
                print("x%02X" % ord(n),)
            print
        else:
            #No data to process
        time.sleep(0.5)

except KeyboardInterrupt:
    print("finished testing...")
    print("exiting...")
    pass

EV3.close()