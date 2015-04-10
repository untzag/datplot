#normalize_by_negative_delay_points
#by Blaise Thompson, April 2014
#
#a python script to run within datplot

#-------------------------------------------------------------------------------

import numpy as np

class run:
    
    def __init__(self,
                 instance):
                   
        #begin
        print ' '
        print 'normalize_by_negative_delay_points script running'
        
        #create array to hold averages
        negative_delay_averages = np.zeros(len(instance.xi))
                  
        #collect averages
        cutoff = -200 #fs                   
        for i in range(len(instance.xi)):
            num_points = 0
            current_slice_value = 0
            for j in range(len(instance.yi)):
                if instance.yi[j] < cutoff:
                    num_points = num_points + 1
                    current_slice_value = current_slice_value + instance.zi[j][i]
                else:
                    pass
            negative_delay_averages[i] = current_slice_value / num_points 
                    
        #normalize by averages
        for i in range(len(instance.xi)):
            for j in range(len(instance.yi)):
                instance.zi[j][i] = instance.zi[j][i] - negative_delay_averages[i]
         
        #re-scale data zmin, zmax   
        instance.zmax = instance.zi.max()
        instance.zmin = instance.zi.min()
        instance.znull = 0
    
        #finish
        print '  done'