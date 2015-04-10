#transform y to y-x
#by Blaise Thompson, June 2014
#
#a python script to run within datplot

#-------------------------------------------------------------------------------

import numpy as np

class run:
    
    def __init__(self,
                 instance):
                     
        #begin
        print ' '
        print 'transforming y to y-x'
        
        #zi[x][y]
        
        print instance.data.shape
        
        for i in range(instance.data.shape[1]): #over all aquisitions
            #get values of w1, w2 (in wavenumbers)
            '''
            w1 = 1e7/instance.data[1, i]
            w2 = 1e7/instance.data[3, i]
            #do subtraction
            out = 1e7/(w2-w1)
            '''
            #re-write array
            instance.data[3, i] = instance.data[3, i] - instance.data[1, i]

        #gengrid again
        instance._gengrid()
        
        print instance.xi
        print instance.yi           
        
        #finish
        print '  done'