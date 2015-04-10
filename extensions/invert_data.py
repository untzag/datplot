#invert_data
#by Blaise Thompson, April 2014
#
#a python script to run within datplot

#-------------------------------------------------------------------------------

class run:
    
    def __init__(self,
                 instance):
                     
        #begin
        print ' '
        print 'invert_data script running'

        #invert data
        instance.zi = -1*instance.zi
        
        #re-scale data zmin, zmax
        instance.zmax = instance.zi.max()
        instance.zmin = instance.zi.min()
        
        #re-normalize
        instance.normalize(ntype = 'a')
        
        #finish
        print '  done'