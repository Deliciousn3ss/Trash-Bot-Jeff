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
import EV3BT



# Front claw interfacing

#set EV3 to bluetooth bus comm0
try:
    EV3 = serial.Serial('/dev/rfcomm0')

except OSError:
    print("EV3 Brick not found! Exiting...")



#test recive message
print("Waiting for message")

try:
    s = EV3BT.encodeMessage(EV3BT.MessageType.Numeric, "abc", "1")
    print(EV3BT.printMessage(s))
    EV3.write(s)
    time.sleep(1)

except KeyboardInterrupt:
    print("aborted testing...")
    print("exiting...")
    pass

EV3.close()