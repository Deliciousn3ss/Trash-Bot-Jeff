import L1_encoder as enc
import L3_color_tracking as clrtrack
from array import *

color = "blue"
ball = "red"

blueHSV = [[55,45,125],[255,255,255]]
orangeHSV = [[0,90,195],[255,255,255]]
greenHSV = [[45,50,110],[255,255,255]]

if(color == "blue"):
    clrtrack.main(blueHSV[0][0], blueHSV[0][1], blueHSV[0][2], blueHSV[1][0], blueHSV[1][1], blueHSV[1][2])
elif(color == "orange"):
    clrtrack.main(orangeHSV[0][0], orangeHSV[0][1], orangeHSV[0][2], orangeHSV[1][0], orangeHSV[1][1], orangeHSV[1][2])
elif(color == "green"):
    clrtrack.main(greenHSV[0][0], greenHSV[0][1], greenHSV[0][2], greenHSV[1][0], greenHSV[1][1], greenHSV[1][2])

#blue ball
#v1_min = 55      # Minimum H value
#v2_min = 45     # Minimum S value
#v3_min = 125      # Minimum V value

#v1_max = 255     # Maximum H value
#v2_max = 255    # Maximum S value
#v3_max = 255    # Maximum V value


#orange ball
#v1_min = 0      # Minimum H value
#v2_min = 90     # Minimum S value
#v3_min = 195      # Minimum V value

#v1_max = 255     # Maximum H value
#v2_max = 255    # Maximum S value
#v3_max = 255    # Maximum V value

#green ball
#v1_min = 45      # Minimum H value
#v2_min = 50     # Minimum S value
#v3_min = 110      # Minimum V value

#v1_max = 255     # Maximum H value
#v2_max = 255    # Maximum S value
#v3_max = 255    # Maximum V value

