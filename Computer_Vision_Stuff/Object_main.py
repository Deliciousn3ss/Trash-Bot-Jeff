from Object_Scan import objectScanner
from Object_Tracking import objectTracking
import threading

while True:

    x,y = objectScanner(1)
    objectTracking(x,y)


    


    

