import Object_Tracking_v2 as objTrack
import Object_Scan as objScan

def main():
    objects = [0,1,2,3]
    y = 0
    current_capacity = 0
    
    while True:
        
        num_obj = objTrack.objectTracking(objects[y],290, current_capacity)
        print("Object count: ",num_obj)
        
        current_capacity = num_obj
        
        if(num_obj >= 2 and y < 4):
            y += 1
            
        
        
            
if __name__ == '__main__':
    main()