"""
@author: Dan Kohler

"""

import os#, sys
#import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mplcolors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.interpolate import griddata, interp1d
import matplotlib.gridspec as grd

"""class grid(np.array):
    def __init__(self, array):
        
            Produces the regularly spaced grid of data from self.data[self.xcol], self.data[self.ycol], and self.data[self.zcol]
            grid factor:  how many grid points in between every data point in one dimension
        
        np.array.__init__(self, array)
"""

"""class grid():
    #    extends the numpy array module to add properties
    def __new__():
"""        

matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
    
class dat:    
    #dictionary connects column names to locations for COLORS scan
    #first is column from color file--columns according to new column ordering
    #second is movement tolerance (x +/- tolerance)
    #third is the unit assigned to this variable
    # dictionary for dat convention implemented on 2014.03.25
    #v2_date = time.strptime('14 Mar 25', '%y %b %d')
    #v2_time = time.mktime(v2_date)
    v2_time = 1395723600.0
    cols_v2 = {
        'num':  (0, 0.0, None, 'acquisition number'),
        'w1':   (1, 5.0, 'nm', r'$\mathrm{\bar\nu_1=\bar\nu_m (cm^{-1})}$'),
        'l1':   (1, 1.0, 'wn', r'$\lambda_1 / nm$'),
        'w2':   (3, 5.0, 'nm', r'$\mathrm{\bar\nu_2=\bar\nu_{2^{\prime}} (cm^{-1})}$'),
        'l2':   (3, 1.0, 'wn', r'$\lambda_2 / nm$'),
        'w3':   (5, 5.0, 'wn', r'$\mathrm{\bar\nu_3 (cm^{-1})}$'),
        'l3':   (5, 1.0, 'nm', r'$\mathrm{\lambda_3 (cm^{-1})}$'),
        'wm':   (7, 1.0, 'nm', r'$\bar\nu_m / cm^{-1}$'),
        'lm':   (7, 1.0, 'wn', r'$\lambda_m / nm$'),
        'dref': (10, 25.0, 'fs', r'$d_ref$'),
        'd1':   (12, 3.0, 'fs', r'$\mathrm{\tau_{2^{\prime} 1} (fs)}$'),
        #'t2p1': (12, 3.0, 'fs', r'$\mathrm{\tau_{2^{\prime} 1}(fs)}$'),
        'd2':   (14, 3.0, 'fs', r'$\mathrm{\tau_{21} (fs)}$'),
        #'t21':  (14, 3.0, 'fs', r'$\mathrm{\tau_{21} (fs)}$'),
        'ai0':  (16, 0.0, 'V', 'Signal 0'),
        'ai1':  (17, 0.0, 'V', 'Signal 1'),
        'ai2':  (18, 0.0, 'V', 'Signal 2'),
        'ai3':  (19, 0.0, 'V', 'Signal 3'),
        'ai4':  (20, 0.0, 'V', 'Signal 4')
    }
    #v1_date = time.strptime('12 Oct 01', '%y %b %d')
    #v1_time = time.mktime(v1_date)
    v1_time = 1349067600.0
    cols_v1 = {
        'num':  (0, 0.0, None, 'acquisition number'),
        'w1':   (1, 5.0, 'nm', r'$\mathrm{\bar\nu_1=\bar\nu_m (cm^{-1})}$'),
        'l1':   (1, 1.0, 'wn', r'$\lambda_1 / nm$'),
        'w2':   (3, 5.0, 'nm', r'$\mathrm{\bar\nu_2=\bar\nu_{2^{\prime}} (cm^{-1})}$'),
        'l2':   (3, 1.0, 'wn', r'$\lambda_2 / nm$'),
        'wm':   (5, 1.0, 'nm', r'$\bar\nu_m / cm^{-1}$'),
        'lm':   (5, 1.0, 'wn', r'$\lambda_m / nm$'),
        'd1':   (6, 3.0, 'fs', r'$\mathrm{\tau_{2^{\prime} 1} (fs)}$'),
        't2p1': (6, 3.0, 'fs', r'$\mathrm{\tau_{2^{\prime} 1}(fs)}$'),
        'd2':   (7, 3.0, 'fs', r'$\mathrm{\tau_{21} (fs)}$'),
        't21':  (7, 3.0, 'fs', r'$\mathrm{\tau_{21} (fs)}$'),
        'ai0':  (8, 0.0, 'V', 'Signal 0'),
        'ai1':  (9, 0.0, 'V', 'Signal 1'),
        'ai2':  (10, 0.0, 'V', 'Signal 2'),
        'ai3':  (11, 0.0, 'V', 'Signal 3')
    }
    #the old column rules before Winter 2012 (when Skye changed the column assignments)
    cols_v0 = {
        'num':  (0, 0.0, None, 'acquisition number'),
        'w1':   (1, 2.0, 'nm', r'$\mathrm{\bar\nu_1=\bar\nu_m (cm^{-1})}$'),
        'l1':   (1, 1.0, 'wn',r'$\lambda_1 / nm$'),
        'w2':   (3, 2.0, 'nm',r'$\mathrm{\bar\nu_2=\bar\nu_{2^{\prime}} (cm^{-1})}$'),
        'l2':   (3, 1.0, 'wn',r'$\lambda_2 / nm$'),
        'wm':   (5, 0.25, 'nm',r'$\bar\nu_m / cm^{-1}$'),
        'lm':   (5, 0.25, 'wn',r'$\lambda_m / nm$'),
        'd1':   (6, 3.0, 'fs',r'$\mathrm{\tau_{2^{\prime} 1} (fs)}$'),
        't2p1': (6, 3.0, 'fs',r'$\mathrm{\tau_{2^{\prime} 1}(fs)}$'),
        'd2':   (8, 3.0, 'fs',r'$\mathrm{\tau_{21} (fs)}$'),
        't21':  (8, 3.0, 'fs',r'$\mathrm{\tau_{21} (fs)}$'),
        'ai0':  (10, 0.0, 'V','Signal 0'),
        'ai1':  (11, 0.0, 'V','Signal 1'),
        'ai2':  (12, 0.0, 'V','Signal 2'),
        'ai3':  (13, 0.0, 'V','Signal 3')
    }
    savepath = 'C:\\Users\\Dan\\Google Drive\\myscripts\\simulations\\'
    # colormap
    signed_cm = ['#0000FF', #blue
                '#00BBFF', #blue-aqua
                '#00FFFF', #aqua
                '#FFFFFF', #white
                '#FFFF00', #yellow
                '#FFBB00', #orange
                '#FF0000'] #red   
    wrightcm = ['#FFFFFF','#0000FF','#00FFFF','#00FF00','#FFFF00','#FF0000','#881111']
    # define colormaps
    mycm=mplcolors.LinearSegmentedColormap.from_list('wright',wrightcm)
    debug=False
    # font style attributes
    font_size = 14
    font_family = 'sans-serif'
    # plot windowing--use to concatenate image
    limits = False
    xlim = [-150,150]
    ylim = [-150,150]
    # attribute used to set z axis scale
    zmin,zmax = 0,1
    # attribute used to indicate the signal zero voltage
    # initial value is znull=zmin
    znull = 0.
    has_data=False
    grid_factor=2
    # attributes of contour lines
    contour_n = 9
    contour_kwargs={'colors':'k',
                    'linewidths':2}
    # attributes of sideplots
    side_plot_proj_kwargs={'linewidth':2}
    side_plot_proj_linetype = 'b'
    side_plot_else_kwargs={'linewidth':2}
    side_plot_else_linetype = 'r'
    #   beamsplitter spectral dependence, measured Sept. 2011 by Stephen Block and Dan Kohler
    #   1st column is wavelength, second is reflection / transmission for that wavelength
    #   stored at Trive/Pyro%20Calibration/fs%20Power%20Curves%20Nov%202011.xlsx
    #   1150nm and 1600nm are artificial points
    #   Note:  this beamsplitter is no longer in use!  Replaced by nickel thin film ND
    #normalization_method = 'SFG'
    normalization_method = 'OPA Power'
    BS = [
        [1150.0, 1200.0, 1250.0, 1300.0, 1350.0, 1400.0, 1450.0, 1500.0, 1550.0, 1600.0],
        [1.641,  1.641,  1.488,  1.275,  1.048,  0.808,  0.654,  0.443,  0.394,  0.394 ]
    ]
   
    def __init__(self, filepath=None, scantype='2d',zvar='ai0', 
                 xvar=None, yvar=None, 
                 user_created=True, 
                 cols=None,
                 grid_factor=grid_factor,
                 color_offset=None, 
                 font_size=None, font_family=None,
                 colortune=False, znull=None):
        #import data file
        if filepath:
            pass
        else:
            filepath = raw_input('Please give the absolute file location:')
        #filepath must yield a file
        if os.path.isfile(filepath):
            self.has_data=True
            print 'found the file!'
        else:
            self.has_data = False
            print 'filepath',filepath,'does not yield a file'
            return        
        self.filepath, self.filename, self.file_suffix = filename_parse(filepath)
        #now import file as a local var
        rawDat = np.genfromtxt(filepath,dtype=np.float) 
        #define arrray used for transposing dat file so cols are first index
        self.data = rawDat.T
        self.grid_factor=grid_factor
        self.smoothing = False
        self.z_scale = 'linear'
        #assign columns
        if cols == 'v2':
            self.datCols = dat.cols_v2
        elif cols == 'v1':
            self.datCols = dat.cols_v1
        elif cols == 'v0':
            self.datCols = dat.cols_v0
        else:
            #guess based on when the file was made
            file_date = os.path.getctime(filepath)
            #print file_date
            if file_date > dat.v2_time:
                cols = 'v2'
                self.datCols = dat.cols_v2
            elif file_date > dat.v1_time:
                cols = 'v1'
                self.datCols = dat.cols_v1
            else:
                # file is older than all other dat versions
                cols = 'v0'
                self.datCols = dat.cols_v0
            print cols
        self.cols=cols
        #shift assorted default values
        if font_size:
            self.font_size = font_size
        if font_family:
            self.font_family = font_family
        print 'file has imported'
        self.constants = []
        if scantype == '2d':
            #define variables and make sure they are valid
            if xvar in self.datCols.keys():
                self.xvar = xvar
            else:
                print 'xvar {0} is not valid.  cannot import file'.format(xvar)
                return
            if yvar in self.datCols.keys():
                self.yvar = yvar
            else:
                print 'yvar {0} is not valid.  cannot import file'.format(yvar)
                return
            self.zvar = zvar

            self.xcol = self.datCols[self.xvar][0]
            self.ycol = self.datCols[self.yvar][0]
            self.zcol = self.datCols[self.zvar][0]

            self.zvars = {
                    'ai0' : None,
                    'ai1' : None,
                    'ai2' : None,
                    'ai3' : None
            }

            #add another ai if the newest dat format
            if self.cols in ['v2']:
                self.zvars['ai4'] = None
            #define constants (anything that is not x,y or z)
            for key in self.datCols.keys():
                if key != self.xvar or key != self.yvar or key not in self.zvars.keys():
                    col = self.datCols[key][0]
                    self.constants.append([key,self.data[col][0]])

            # is xvar or yvar in wavenumbers?  default is nm for dat, so convert data col
            if self.xvar in ['w1', 'w2', 'w3', 'wm']:
                self.data[self.xcol] = 10**7 / self.data[self.xcol]
            if self.yvar in ['w1', 'w2', 'w3', 'wm']:
                self.data[self.ycol] = 10**7 / self.data[self.ycol]

            # subtract off the central frequency from the mono axis
            # this gives units of displacement from the set point
            if colortune:
                # figure out how to convert the mono axis
                if self.xvar in ['lm', 'wm'] and self.yvar in ['l1', 'l2', 'w1', 'w2']:
                    if (self.xvar in ['lm'] and self.yvar in ['l1','l2']) or (
                        self.xvar in ['wm'] and self.yvar in ['w1','w2']):
                        self.data[self.xcol] = self.data[self.xcol] - self.data[self.ycol]
                    else:
                        self.data[self.xcol] = self.data[self.xcol] - 10**7 / self.data[self.ycol]
                elif self.yvar in ['lm', 'wm'] and self.xvar in ['l1', 'l2', 'w1', 'w2']:
                    if (self.yvar in ['lm'] and self.xvar in ['l1','l2']) or (
                        self.yvar in ['wm'] and self.xvar in ['w1','w2']):
                        self.data[self.ycol] = self.data[self.ycol] - self.data[self.xcol]
                    else:
                        self.data[self.ycol] = self.data[self.ycol] - 10**7 / self.data[self.xcol]
            # apply window to data?
            self.limits=False
            if user_created:
                # create xy grid (vars self.xi, self.yi) and interpolate z values to grid
                # new:  grid for all ai channels
                if znull is not None:
                    self.znull = znull
                    self.gengrid()
                else:
                    #if no znull, we probably want zmin to be our zero voltage
                    self.znull = self.data[self.zcol].min()
                    self._gengrid()
                    self.znull = self.zi.min()                    
                # store min and max independent of data so different scaling can be applied
                self.zmax = self.zi.max()
                self.zmin = self.zi.min()
            else:
                pass

        elif scantype == '1d':
            self.xvar = raw_input('x var (w1, w2, wm, d1, d2)?  ')

        elif scantype == 'norm': # file will not be explicitly plotted--need only self.data
            pass
        else:
            print 'no treatment known for scan type', scantype


    def colorbar(self):
        """
            adds colorbar to the contour plot figure
            only after all contour plot embellishments have been performed
        """
        if self.s1:
            ax_cb = plt.subplot(self.gs[1])
        else:
            print 'must create plot before adding colorbar'
            return
        if self.alt_zi == 'int':
            ticks = np.linspace(-1,1,21)
            # find the intersection of the range of data displayed and ticks
            ticks = [ticki for ticki in ticks if ticki >= 
                min(self.zi_norm.min(), self.znull) and 
                ticki <= max(self.znull, self.zi_norm.max())]
            self.p1.colorbar(self.cax, ticks=ticks, cax=ax_cb)
        elif self.alt_zi == 'amp':
            ticks = np.linspace(0,1,11)
            self.p1.colorbar(self.cax, ticks=ticks, cax=ax_cb)
        elif self.alt_zi == 'log':
            # mask zi's negative and zero elements
            masked = np.ma.masked_less_equal(self.zi-self.znull, 0.)
            # the colorbar range
            # not sure whether to define the range using masked array or
            # full array
            logmin = np.log10(masked.min() / (self.zmax - masked.min()))
            ticks = np.linspace(logmin,0,num=11)
            # determine how much precision is necessary in the ticks:
            decimals = int(np.floor(-np.log10(np.abs(
                ticks[-1]-ticks[0])))) + 2
            ticklabels = np.around(ticks,decimals)
            self.p1.colorbar(self.cax, ticks=ticks).ax.set_yticklabels(ticklabels)
        elif self.alt_zi in [None, 'raw']: # raw colorbar
            ticks = np.linspace(min([self.znull, self.zmin]),max(self.znull, self.zmax),num=11)
            decimals = int(np.floor(-np.log10(np.abs(
                ticks[-1]-ticks[0])))) + 2
            ticklabels = np.around(ticks,decimals)
            self.p1.colorbar(self.cax, ticks=ticks, cax=ax_cb).ax.set_yticklabels(ticklabels)
            #self.p1.colorbar(self.cax, ticks=ticks, cax=ax_cb)
        else: #could not determine colorbar type
            print 'color scale used not recognized:  cannot produce colorbar'

    def plot2d(self, alt_zi='int', 
               scantype=None, contour=False, aspect=None, pixelated=False, 
               dynamic_range=False, signed=None):
        """
            offset is deprecated and should not be used: 
                invoke zmin attribute to shift data values
            dynamic_range will force the colorbar to use all of it's colors
        """
        # delete old plot data stored in the plt class
        plt.close()
        # update parameters
        matplotlib.rcParams.update({
            'font.size':self.font_size
        })
        # if the plot is a 2d delay or 2d freq, add extra gridlines to guide the eye
        # also, set the aspect ratio so axes have equal measure
        delays = ['d1','d2','t2p1','t21']
        freq = ['w1','w2', 'wm']
        wavelength = ['l1','l2', 'lm']
        p1 = plt.figure()
        gs = grd.GridSpec(1,2, width_ratios=[20,1], wspace=0.1)
        if ((self.xvar in delays and self.yvar in delays) 
            or (self.xvar in freq and self.yvar in freq) 
            or (self.xvar in wavelength and self.yvar in wavelength)):
            if aspect:
                s1 = p1.add_subplot(gs[0], aspect=aspect)
            else:
                s1 = p1.add_subplot(gs[0], aspect='equal')
            diag_min = max(min(self.xi),min(self.yi))
            diag_max = min(max(self.xi),max(self.yi))
            plt.plot([diag_min, diag_max],[diag_min, diag_max],'k:')
        else:
            s1 = p1.add_subplot(gs[0])
        # attach to the plot objects so further manipulations can be done
        self.p1=p1
        self.gs=gs
        self.s1=s1

        if alt_zi in ['int', None, 'raw']:
            znull = None
            if alt_zi == 'int':
                # for regular normalized (unscaled, normalized to znull-zmax range)
                # first offset and normalize data
                pm_max = max(np.abs([self.zmax, self.zmin]))
                zi_norm = (self.zi - self.znull) / (pm_max - self.znull)
                znull = 0.
            else: # alt_zi in [None, 'raw']
                zi_norm = self.zi
                znull = self.znull
            zmax = max(znull, zi_norm.max())
            zmin = min(znull, zi_norm.min())
            print zmin, zmax
            # now I have to whether or not the data is signed, if zmin and zmax
            # are on the same side of znull, then the data only has one sign!
            if znull >= max(zmin, zmax):
                # data is negative sign
                if dynamic_range:
                    ubound = zmax
                else:
                    ubound = znull
                lbound = zmin
            elif znull <= min(zmin, zmax):
                # data is positive sign
                if dynamic_range:
                    lbound = zmin
                else:
                    lbound = znull
                ubound = zmax
            else:
                # data has positive and negative sign, so center the colorbar
                if dynamic_range:
                    ubound = min(-zmin, zmax)
                else:
                    ubound = max(-zmin, zmax)
                lbound = -ubound
            levels = np.linspace(lbound, ubound, num=200)
        elif alt_zi == 'amp':
            # for sqrt scale (amplitude)
            zi_norm = np.ma.masked_less_equal(
                (self.zi - self.znull) / (self.zmax - self.znull), 0.)
            zi_norm = np.sqrt((self.zi - self.znull) / (self.zmax - self.znull))
            levels = np.linspace(0,1,num=200)
        elif alt_zi == 'log':
            # for log scale
            zi_norm = np.ma.masked_less_equal(
                (self.zi - self.znull) / (self.zmax - self.znull), 0.)
            zi_norm = np.log10(zi_norm)
            levels = 200
        else:
            print 'alt_zi type {0} not recognized; plotting on raw scale'.format(alt_zi)
            zi_norm = self.zi
            levels = 200 
        self.alt_zi=alt_zi
        self.zi_norm = zi_norm
        # plot the data
        if pixelated:
            # need to input step size to get centering to work
            x_step = np.abs(self.xi[1] - self.xi[0])
            y_step = np.abs(self.yi[1] - self.yi[0])
            if aspect:
                pixel_aspect=aspect
            else:
                # this weighting makes the plot itself square
                pixel_aspect = (self.xi.max() - self.xi.min()) / (self.yi.max() - self.yi.min())
                # this weighting gives square pixels...?
                #pixel_aspect = 1. / pixel_aspect
            cax = plt.imshow(zi_norm, origin='lower', cmap=self.mycm, 
                             interpolation='nearest', 
                             extent=[self.xi.min() - x_step/2., 
                                     self.xi.max() + x_step/2., 
                                     self.yi.min() - y_step/2., 
                                     self.yi.max() + y_step/2.])#,
                             #aspect=pixel_aspect)
            plt.gca().set_aspect(pixel_aspect, adjustable='box-forced')
        else:
            cax = plt.contourf(self.xi, self.yi, zi_norm, levels, 
                               cmap=self.mycm)
        self.cax=cax
        if contour:
            plt.contour(self.xi, self.yi, zi_norm, self.contour_n, 
                        **self.contour_kwargs)
        #matplotlib.axes.rcParams.viewitems
        #ni = 5
        #xticks = np.linspace(self.xi.min(), self.xi.max(), ni).round()
        #yticks = np.linspace(self.yi.min(), self.yi.max(), ni).round()
        #plt.xticks(xticks)
        #plt.yticks(yticks)
        plt.xticks(rotation=45)
        plt.xlabel(self.datCols[self.xvar][3], fontsize=self.font_size)
        plt.ylabel(self.datCols[self.yvar][3], fontsize=self.font_size)
        plt.grid(b=True)
        if self.limits:
            v = np.array([self.xlim[0], self.xlim[1],
                          self.ylim[0], self.ylim[1]])
        else:
            v = np.array([self.xi.min(), self.xi.max(),
                          self.yi.min(), self.yi.max()])
        s1.axis(np.around(v))
        if aspect:
            s1.set_aspect(aspect)
        # window the plot; use either 2d plot dimensions or set window
        p1.subplots_adjust(bottom=0.18)
        #s1.set_adjustable('box-forced')
        s1.autoscale(False)
        print 'plotting finished!'

    def side_plots(self, subplot, 
                    # do we project (bin) either axis?
                    x_proj=False, y_proj=False, 
                    # provide a list of coordinates for sideplot
                    x_list=None, y_list=None,
                    # provide a NIRscan object to plot
                    x_obj=None, y_obj=None):
        """
            position complementary axis plot on x and/or y axes of subplot
        """
        #if there is no 1d_object, try to import one
        divider = make_axes_locatable(subplot)
        if x_proj or x_list or x_obj:
            axCorrx = divider.append_axes('top', 0.75, pad=0.3, sharex=subplot)
            axCorrx.autoscale(False)
            axCorrx.set_adjustable('box-forced')
            # make labels invisible
            plt.setp(axCorrx.get_xticklabels(), visible=False)
            axCorrx.get_yaxis().set_visible(False)
            axCorrx.grid(b=True)
        if y_proj or y_list or y_obj:
            axCorry = divider.append_axes('right', 0.75, pad=0.3, sharey=subplot)
            axCorry.autoscale(False)
            axCorry.set_adjustable('box-forced')
            # make labels invisible
            plt.setp(axCorry.get_yticklabels(), visible=False)
            axCorry.get_xaxis().set_visible(False)
            axCorry.grid(b=True)
        if x_proj:
            #integrate the axis
            x_ax_int = self.zi.sum(axis=0) - self.znull * len(self.yi)
            #normalize (min is a pixel)
            xmax = max(np.abs(x_ax_int))
            x_ax_int = x_ax_int / xmax
            axCorrx.plot(self.xi,x_ax_int,self.side_plot_proj_linetype,
                         **self.side_plot_proj_kwargs)
            if min(x_ax_int) < 0:
                axCorrx.set_ylim([-1.1,1.1])
            else:
                axCorrx.set_ylim([0,1.1])
            axCorrx.set_xlim([self.xi.min(), self.xi.max()])
        if y_proj:
            #integrate the axis
            y_ax_int = self.zi.sum(axis=1) - self.znull * len(self.xi)
            #normalize (min is a pixel)
            ymax = max(np.abs(y_ax_int))
            y_ax_int = y_ax_int / ymax
            axCorry.plot(y_ax_int,self.yi,self.side_plot_proj_linetype,
                         **self.side_plot_proj_kwargs)
            if min(y_ax_int) < 0:
                axCorry.set_xlim([-1.1,1.1])
            else:
                axCorry.set_xlim([0,1.1])
            axCorry.set_ylim([self.yi.min(), self.yi.max()])
        if isinstance(x_list, np.ndarray): 
            print x_list.shape
            axCorrx.plot(x_list[0],x_list[1], self.side_plot_else_linetype,
                         **self.side_plot_else_kwargs)
            axCorrx.set_ylim([0.,1.1])
        elif x_obj:
            try:
                x_list = x_obj.data[0][2].copy()
            except IndexError:
                print 'Import failed--data type was not recognized'
            # spectrometer has units of nm, so make sure these agree
            if self.xvar in ['w1','w2','wm']:
                x_list[0] = 10**7 / x_list[0]
            #normalize the data set
            x_list_max = x_list[1].max()
            x_list[1] = x_list[1] / x_list_max
            axCorrx.plot(x_list[0],x_list[1], self.side_plot_else_linetype,
                         **self.side_plot_else_kwargs)
            axCorrx.set_ylim([0.,1.1])
            axCorrx.set_xlim([self.xi.min(), self.xi.max()])
        if isinstance(y_list, np.ndarray):
            axCorry.plot(y_list[1],y_list[0], self.side_plot_else_linetype,
                         **self.side_plot_else_kwargs)
        elif y_obj:
            try:
                y_list = y_obj.data[0][2].copy()
            except IndexError:
                print 'Import failed--data type was not recognized'
            if self.yvar in ['w1','w2','wm']:
                y_list[0] = 10**7 / y_list[0]
            #normalize the data set
            y_list_max = y_list[1].max()
            y_list[1] = y_list[1] / y_list_max
            axCorry.plot(y_list[1],y_list[0], self.side_plot_else_linetype,
                         **self.side_plot_else_kwargs)
            #axCorry.set_xlim([0.,1.1])
            axCorry.set_ylim([self.yi.min(), self.yi.max()])

    def savefig(self, fname=None, **kwargs):
        """
            generates the image file by autonaming the file
            default image type is 'png'
        """
        if self.p1:        
            pass
        else:
            print 'no plot is associated with the data. cannot save'
            return
        if not fname:
            fname = self.filename
            filepath = self.filepath
            file_suffix = 'png'
        else:
            filepath, fname, file_suffix = filename_parse(fname)
            if not file_suffix:
                file_suffix = 'png' 
        if 'transparent' not in kwargs:
            kwargs['transparent'] = True
        if filepath:
            fname = filepath + '\\' + fname
        fname = find_name(fname, file_suffix)
        fname = fname + '.' + file_suffix
        self.p1.savefig(fname, **kwargs)
        print 'image saved as {0}'.format(fname)
    
    def trace(self, val=None, kind=None, save=False):
        """
            returns a 1D trace of the data where val is constant
            both arguments and values of the trace are returned in the format 
                np.array([arg, value])
            val is a constraint that defines the 1D trace
            kind has several options:
                'x':  horizontal trace at fixed y val
                'y':  vertical trace at fixed x val
                'ps':  peak shift parameterized against coherence time (tau)
                    at fixed population time val=T
                    needs to be 2d delay scan
                '3pepsZQC':  peak shift parameterized against coherence time 
                    (tau) at fixed zqc evolution time (pathways 1-3) val
                'diag':  diagonal slice of an equal axis space (eg. 2d freq)
                    with offset val
        """
        if kind == 'x':
            pass
        elif kind == 'y':
            pass
        elif kind in ['ps', '3peps']:
            trace = self._3PEPS_trace(val, w2w2p_pump=True)
            savestr = '{0}3peps \\{1}.T{2}.txt'.format(self.savepath,self.filename,val)
        elif kind in ['ps-zqc', 'zqc', '3peps-zqc']:
            trace = self._3PEPS_trace(val, w2w2p_pump=False)
            savestr = '{0}3peps-zqc \\{1}.T{2}.txt'.format(self.savepath,self.filename,val)
        elif kind == 'diag':
            if val:
                offset = val
            else: offset = 0.0
            trace = self._diag(offset=offset)
        if save:
            np.savetxt(savestr,trace.T)
        return trace

    def svd(self):
        """
            singular value decomposition of gridded data z
        """
        U,s,V = np.linalg.svd(self.zi)
        self.U, self.s, self.V = U,s,V
        #give feedback on top (normalized) singular values
        return U, s, V

    def _diag(self, offset=0.0, use_griddata=False):
        """
            returns an array of z-axis points in the interpolated array that satisfy x=y
        """
        #check that x and y both are the same domain (i.e. 2dfreq or 2d delay)
        out=[]
        delays = ['d1','d2','t2p1','t21']
        freq = ['w1','w2']
        wavelength = ['l1','l2']
        if (self.xvar in delays and self.yvar in delays) or (self.xvar in freq and self.yvar in freq) or (self.xvar in wavelength and self.yvar in wavelength):
            if use_griddata:
                #alternate version:  use griddata
                min_diag = max(min(self.xi),min(self.yi))
                max_diag = min(max(self.xi),max(self.yi))
                #make grid values
                
            else:
                #initialize the closest we get with a random cloeseness number
                closest=np.abs(self.xi[0]-self.yi[0])
                #find the x and y coordinates that agree to within tolerance
                for i in range(len(self.xi)):
                    for j in range(len(self.yi)):
                        difference = np.abs(self.xi[i] - self.yi[j])
                        if difference <= self.datCols[self.xvar][1]:
                            out.append([
                                (self.xi[i]+self.yi[j])/2,
                                self.zi[j][i]])
                        else:
                            closest=min([closest,difference])
            #check if we have any values that fit
            if len(out) == 0:
                print 'no x and y values were closer than {0}.  Try increasing grid_factor'.format(closest)
            else:
                out.sort()
                out = np.array(zip(*out))
                return np.array(out)
        else:
            print 'cannot give diagonal if x and y units are not the same'
            print 'x axis:', self.xvar
            print 'y axis:', self.yvar
            return
        
    def difference2d(self):
        """
            Take the registered plot and import one to take the difference.
            Difference will be plotted as ref - imported (so biggest differences are red)
        """
        print 'Specify the requested file to compare with ref'
        imported = dat(xvar=self.xvar, yvar=self.yvar, user_created=False)
        #create zi grid using ref grid values
        imported._gengrid(xlis=self.xi, ylis=self.yi, grid_factor=1)
        #imported and ref should have same zi grid size now--subtract and plot!
        #normalize both grids first
        zrefmax = self.zi.max()
        zrefmin = self.zi.min()
        zimpmax = imported.zi.max()
        zimpmin = imported.zi.min()
        
        self.zi = (self.zi - zrefmin) / (zrefmax - zrefmin)
        imported.zi = (imported.zi - zimpmin) / (zimpmax - zimpmin)

        diffzi =  imported.zi - self.zi
        self.plot2d(alt_zi=diffzi, scantype='Difference')

    def normalize(self,ntype=None,
                  x_file=None,y_file=None,
                  xnSigVar=None,ynSigVar=None,
                  xpower=None, ypower=None,
                  old_fit=False): 
        """
            A scaling technique to alter either all the pixels uniformly (i.e. 
            a unit conversion), or certain pixels based on their x and y values.  
        """
        if ntype is None:
            print 'no ntype selected; normalizing to max'
            zi_max = self.zi.max()
            self.zi = (self.zi - self.znull) / (zi_max - self.znull)
            self.zmax = 1.
            self.znull = 0.
            return
        elif ntype == 'wavelength' or ntype=='b': 
            freqs = ['w1', 'w2', 'wm', 'l1', 'l2', 'lm']
            if self.debug:
                plt.figure()
            # output scales as a function of wavelength (optics, opa power, etc.)
            if self.xvar in freqs or self.yvar in freqs:
                # first find x normalization values, then y normalization values
                if self.xvar in freqs:
                    print 'Need normalization file for ',self.xvar,' from ',min(self.xi),' to ',max(self.xi)
                    # import the desired colors file
                    if x_file:
                        x_file_path, x_file_name, x_file_suffix = filename_parse(x_file)
                        if x_file_suffix == 'dat':
                            xNorm = dat(filepath=x_file, scantype='norm', cols=self.cols)
                            if not xnSigVar:
                                xnSigVar = raw_input('which column has normalization signal (ai1, ai2, ai3)?')
                            xnCol = xNorm.datCols[self.xvar][0] 
                            xnSigCol = xNorm.datCols[xnSigVar][0]
                        elif x_file_suffix == 'fit':
                            xNorm = fit(filepath=x_file, old_cols=old_fit)
                            xnCol = xNorm.cols['set_pt'][0] 
                            xnSigCol = xNorm.cols['amp'][0]
                        try:
                            # convert if in wavenumber units
                            # note:  data[xnCol] values must be in ascending order
                            if self.xvar == 'w1' or self.xvar == 'w2' or self.xvar == 'wm':
                                xNorm.data[xnCol] = 10**7 / xNorm.data[xnCol]
                            # to interpolate, make sure points are ordered by ascending x value
                            xnData = zip(xNorm.data[xnCol],xNorm.data[xnSigCol])
                            xnData.sort()
                            xnData = zip(*xnData)
                            xnData = np.array(xnData)
                            if self.debug:
                                plt.plot(xnData[0],xnData[1],label='xvar')
                            # w2 gets squared for normalization in standard treatment
                            fx = interp1d(xnData[0],xnData[1], kind='cubic', bounds_error=True)
                        except:
                            print '{0} normalization failed'.format(self.xvar)
                            fx = False #interp1d([min(self.xi),max(self.xi)],[1,1])
                    # rather than look for a file, don't normalize by x
                    # if x_file is not given
                    else:
                        print 'no file found for xnorm using filepath {0}'.format(x_file)
                        fx = False
                else:
                    fx = None
                    #xni = np.ones(len(self.xi))

                if self.yvar in freqs:                
                    print 'Need normalization file for ',self.yvar,' from ',min(self.yi),' to ',max(self.yi)
                    #import the desired colors file using a special case of the module!
                    if y_file:
                        y_file_path, y_file_name, y_file_suffix = filename_parse(y_file)
                        if y_file_suffix == 'dat':
                            print 'in here!'
                            yNorm = dat(filepath=y_file, scantype='norm', cols=self.cols)
                            if not ynSigVar:
                                ynSigVar = raw_input('which column has normalization signal (ai1, ai2, ai3)?')
                            ynCol = yNorm.datCols[self.yvar][0] 
                            ynSigCol = yNorm.datCols[ynSigVar][0]
                        elif y_file_suffix == 'fit':
                            yNorm = fit(filepath=y_file, old_cols=old_fit)
                            ynCol = yNorm.cols['set_pt'][0] 
                            ynSigCol = yNorm.cols['amp'][0]
                        try:
                            if self.yvar == 'w1' or self.yvar == 'w2' or self.yvar == 'wm':
                                yNorm.data[ynCol] = 10**7 / yNorm.data[ynCol]
                            ynData = zip(yNorm.data[ynCol],yNorm.data[ynSigCol])
                            ynData.sort()
                            ynData = zip(*ynData)
                            ynData = np.array(ynData)
                            if self.debug:
                                plt.plot(ynData[0],ynData[1],label='yvar')
                            fy = interp1d(ynData[0],ynData[1], kind='cubic', bounds_error=True)
                        except:
                            print '{0} normalization failed'.format(self.yvar)
                            fy = False#interp1d([min(self.yi),max(self.yi)],[1,1])
                            return
                    else:
                        print 'no file found for ynorm using filepath {0}'.format(y_file)
                        fx = False
                    #yni = griddata(ynData[0],ynData[1], self.yi, method='cubic')
                    #fyi = fy(self.yi)
                    #plt.plot(self.yi,fyi)
                else:
                    fy = None

                #normalize by w2 by both beam energies (use beamsplitter stats for splitting correctly)
                #NOTE:  R*T = 1 / (1 + R/T) if Abs=0
                #NOTE:  BS normalization deprecated for now
                # if x and y powers are not given, make a guess
                if xpower is None:
                    if self.xvar == 'w2' or self.xvar == 'l2':
                        xpower = 2
                        #BS = np.array(dat.BS)
                        #BS[0] = 10**7 / BS[0]
                        #BS[1] = BS[1] / (1.0 + BS[1])
                        #BS = zip(BS[0],BS[1])
                        #BS.sort()
                        #BS = zip(*BS)
                        #fBSx = interp1d((BS[0]), BS[1], kind='linear')
                    else: 
                        xpower = 1
                        #fBSx = None
                if ypower is None:
                    if self.yvar == 'w2' or self.yvar == 'l2':
                        ypower = 2
                        #BS = np.array(dat.BS)
                        #BS[0] = 10**7/BS[0]
                        #BS[1] = BS[1] / (1.0 + BS[1])
                        #BS = zip(BS[0],BS[1])
                        #BS.sort()
                        #BS = zip(*BS)
                        #fBSy = interp1d(BS[0], BS[1], kind='linear')
                    else:
                        ypower = 1
                        #fBSy = None
                if not self.znull:
                    znull = self.data[self.zcol].min()
                else:
                    znull = self.znull
                # begin normalization of data points
                # after scaling, offset by znull so zero remains the same
                for i in range(len(self.data[self.zcol])):
                    #match data's x value to our power curve's values through interpolation
                    zi = self.data[self.zcol][i]
                    if fx:
                        #if fBSx:
                        #    self.data[self.zcol][i] = self.data[self.zcol][i] / (fx(self.data[self.xcol][i])**xpower*fBSx(self.data[self.xcol][i]))
                        #else:
                        #    self.data[self.zcol][i] = self.data[self.zcol][i] / (fx(self.data[self.xcol][i])**xpower)
                        try:
                            zi = (zi - znull) / (fx(self.data[self.xcol][i])**xpower) + znull
                        except ValueError:
                            #see if value is near bounds (to within tolerance)
                            if np.abs(self.data[self.xcol][i]-xnData[0].max()) < self.datCols[self.xvar][1]:
                               zi = (zi - znull) / (fx(xnData[0].max())**xpower) + znull
                            elif np.abs(self.data[self.xcol][i]-xnData[0].min()) < self.datCols[self.xvar][1]:
                                zi = (zi - znull) / (fx(xnData[0].min())**xpower) + znull
                            else:
                                print 'There is a problem with element x={0}, row {1}'.format(self.data[self.xcol][i],i)  
                                print 'norm data has range of: {0}-{1}'.format(xnData[0].min(), xnData[0].max())
                                return
                        except ZeroDivisionError:
                            print 'divided by zero at element x={0}, row {1}'.format(self.data[self.xcol][i],i)  
                            zi = znull
                    if fy:
                        #if fBSy:
                        #    self.data[self.zcol][i] = self.data[self.zcol][i] / (fy(self.data[self.ycol][i])**ypower*fBSy(self.data[self.ycol][i]))
                        #else:
                        #    self.data[self.zcol][i] = self.data[self.zcol][i] / (fy(self.data[self.ycol][i])**ypower)
                        #zi = self.data[self.zcol][i]
                        try:
                            zi = (zi - znull) / (fy(self.data[self.ycol][i])**ypower) + znull
                        except ValueError:
                            #see if value is near bounds (to within tolerance)
                            if np.abs(self.data[self.ycol][i]-ynData[0].max()) < self.datCols[self.yvar][1]:
                                zi = (zi - znull) / (fy(ynData[0].max())**ypower) + znull
                            elif np.abs(self.data[self.ycol][i]-ynData[0].min()) < self.datCols[self.yvar][1]:
                                zi = (zi - znull) / (fy(ynData[0].min())**ypower) + znull
                            else:
                                print 'There is a problem with element y={0}, row {1}'.format(self.data[self.ycol][i],i)  
                                print 'norm data has range of: {0}-{1}'.format(ynData[0].min(), ynData[0].max())
                                return
                        except ZeroDivisionError:
                                print 'divided by zero at element y={0}, row {1}'.format(self.data[self.ycol][i],i)  
                                zi = znull
                    self.data[self.zcol][i] = zi
                # offset so that znull = 0
                self.data[self.zcol] = self.data[self.zcol] - znull
                self.znull = 0.
                # now interpolate the new data and create a new zi grid
                self._gengrid()
                # do NOT update zmin and zmax unless zmin and zmax were the 
                #  bounds before normalization 
                self.zmax = self.zi.max()
                self.zmin = self.zi.min()

            else:
                print 'wavelength normalization not needed:  x and y vars are wavelength invariant'
        # now for trace-localized normalization
        # ntype specifies the traces to normalize
        # used to be called equalize
        elif ntype in ['horizontal', 'h', 'x', self.xvar]: 
            nmin = self.znull
            #normalize all x traces to a common value 
            maxes = self.zi.max(axis=1)
            numerator = (self.zi - nmin)
            denominator = (maxes - nmin)
            for i in range(self.zi.shape[0]):
                self.zi[i] = numerator[i]/denominator[i]
            self.zmax = self.zi.max()
            self.zmin = self.zi.min()
            self.znull = 0.
            print 'normalization complete!'
        elif ntype in ['vertical', 'v', 'y', self.yvar]: 
            nmin = self.znull
            maxes = self.zi.max(axis=0)
            numerator = (self.zi - nmin)
            denominator = (maxes - nmin)
            for i in range(self.zi.shape[1]):
                self.zi[:,i] = numerator[:,i] / denominator[i]
            self.zmax = self.zi.max()
            self.zmin = self.zi.min()
            self.znull = 0.
            print 'normalization complete!'
        else:
                print 'did not normalize because only programmed to handle linear, log, or power normalization'
    
    def center(self, axis=None, center=None):
        if center == 'max':
            print 'listing center as the point of maximum value'
            if axis == 0 or axis in ['x', self.xvar]:
                index = self.zi.argmax(axis=0)
                set_var = self.xi
                max_var = self.yi
                out = np.zeros(self.xi.shape)
            elif axis == 1 or axis in ['y', self.yvar]:
                index = self.zi.argmax(axis=1)
                set_var = self.yi
                max_var = self.xi
                out = np.zeros(self.yi.shape)
            else:
                print 'Input error:  axis not identified'
                return
            for i in range(len(set_var)):
                out[i] = max_var[index[i]]
        else:
            # find center by average value
            out = self.exp_value(axis=axis, moment=1)
        return out
                
    def exp_value(self, axis=None, moment=1, norm=True, noise_filter=None):
        """
            returns the weighted average for fixed points along axis
            specify the axis you want to have exp values for (x or y)
            good for poor-man's 3peps, among other things
            moment argument can be any integer; meaningful ones are:
                0 (area, set norm False)
                1 (average, mu) or 
                2 (variance, or std**2)
            noise filter, a number between 0 and 1, specifies a cutoff for 
                values to consider in calculation.  zi values less than the 
                cutoff (on a normalized scale) will be ignored
            
        """
        if axis == 0 or axis in ['x', self.xvar]:
            # an output for every x var
            zi = self.zi.copy()
            int_var = self.yi
            out = np.zeros(self.xi.shape)
        elif axis == 1 or axis in ['y', self.yvar]:
            # an output for every y var
            zi = self.zi.T.copy()
            int_var = self.xi
            out = np.zeros(self.yi.shape)
        else:
            print 'Input error:  axis not identified'
            return
        if not isinstance(moment, int):
            print 'moment must be an integer.  recieved {0}'.format(moment)
            return
        for i in range(out.shape[0]):
            # ignoring znull for this calculation, and offseting my slice by min
            zi_min = zi[:,i].min()
            #zi_max = zi[:,i].max()
            temp_zi = zi[:,i] - zi_min
            if noise_filter is not None:
                cutoff = noise_filter * (temp_zi.max() - zi_min)
                temp_zi[temp_zi < cutoff] = 0
            #calculate the normalized moment
            if norm == True:
                out[i] = np.dot(temp_zi,int_var**moment) / temp_zi.sum()#*np.abs(int_var[1]-int_var[0]) 
            else:
                out[i] = np.dot(temp_zi,int_var**moment)
        return out

    def fit_gauss(self, axis=None):
        """
            least squares optimization of traces
            intial params p0 guessed by moments expansion
        """
        if axis == 0 or axis in ['x', self.xvar]:
            # an output for every x var
            zi = self.zi.copy()
            var = self.yi
            #out = np.zeros((len(self.xi), 3))
        elif axis == 1 or axis in ['y', self.yvar]:
            # an output for every y var
            zi = self.zi.T.copy()
            var = self.xi
            #out = np.zeros((len(self.yi), 3))

        # organize the list of initial params by calculating moments
        m0 = self.exp_value(axis=axis, moment=0, norm=False)
        m1 = self.exp_value(axis=axis, moment=1, noise_filter=0.1)
        m2 = self.exp_value(axis=axis, moment=2, noise_filter=0.1)        

        mu_0 = m1
        s0 = np.sqrt(np.abs(m2 - mu_0**2))
        A0 = m0 / (s0 * np.sqrt(2*np.pi))
        offset = np.zeros(m0.shape)
        
        print mu_0

        p0 = np.array([A0, mu_0, s0, offset])
        out = p0.copy()
        from scipy.optimize import leastsq
        for i in range(out.shape[1]):
            #print leastsq(gauss_residuals, p0[:,i], args=(zi[:,i], var))
            try:
                out[:,i] = leastsq(gauss_residuals, p0[:,i], args=(zi[:,i]-self.znull, var))[0]
            except:
                print 'least squares failed on {0}:  initial guesses will be used instead'.format(i)
                out[:,i] = p0[:,i]
            #print out[:,i] - p0[:,i]
        out[2] = np.abs(out[2])
        return out
        
    def smooth(self, 
               x=0,y=0, 
               window='kaiser'): #smoothes via adjacent averaging            
        """
            convolves the signal with a 2D window function
            currently only equipped for kaiser window
            'x' and 'y', both integers, are the nth nearest neighbor that get 
                included in the window
            Decide whether to perform xaxis smoothing or yaxis by setting the 
                boolean true
        """
        # n is the seed of the odd numbers:  n is how many nearest neighbors 
        # in each direction
        # make sure n is integer and n < grid dimension
        # account for interpolation using grid factor
        nx = x*self.grid_factor
        ny = y*self.grid_factor
        # create the window function
        if window == 'kaiser':
            # beta, a real number, is a form parameter of the kaiser window
            # beta = 5 makes this look approximately gaussian in weighting 
            # beta = 5 similar to Hamming window, according to numpy
            # over window (about 0 at end of window)
            beta=5.0
            wx = np.kaiser(2*nx+1, beta)
            wy = np.kaiser(2*ny+1, beta)
        # for a 2D array, y is the first index listed
        w = np.zeros((len(wy),len(wx)))
        for i in range(len(wy)):
            for j in range(len(wx)):
                w[i,j] = wy[i]*wx[j]
        # create a padded array of zi
        # numpy 1.7.x required for this to work
        temp_zi = np.pad(self.zi, ((ny,ny), 
                                   (nx,nx)), 
                                    mode='edge')
        from scipy.signal import convolve
        out = convolve(temp_zi, w/w.sum(), mode='valid')
        if self.debug:
            plt.figure()
            sp1 = plt.subplot(131)
            plt.contourf(self.zi, 100)
            plt.subplot(132, sharex=sp1, sharey=sp1)
            plt.contourf(w,100)
            plt.subplot(133)
            plt.contourf(out,100)
        self.zi=out
        # reset zmax
        self.zmax = self.zi.max()
        self.zmin = self.zi.min()

    def T(self):
        """
        transpose the matrix and get the x and y axes to follow suit
        """
        self.zi = self.zi.T

        tempxi = self.xi.copy()
        tempyi = self.yi.copy()
        tempxvar = self.xvar.copy()
        tempyvar = self.yvar.copy()

        self.xi = tempyi
        self.yi = tempxi
        
        self.xvar = tempyvar
        self.yvar = tempxvar
        
        print 'x axis is now {0}, and y is {1}'.format(self.xvar, self.yvar)
        
    def intaxis(self, intVar, filename=None):
         if intVar == self.xvar: #sum over all x values at fixed y
             dataDump = np.zeros((len(self.yi),2))
             for y in range(len(self.yi)):
                 dataDump[y][0] = self.yi[y]
                 dataDump[y][1] = self.zi[y].sum() -  self.znull * len(self.xi)

             np.savetxt(filename, dataDump)

         elif intVar == self.yvar: #sum over all y values at fixed x
             dataDump = np.zeros((len(self.xi),2))
             for x in range(len(self.xi)):
                 dataDump[x][0] = self.xi[x]
                 for y in range(len(self.yi)):
                     dataDump[x][1] += self.zi[y][x] - self.znull

             np.savetxt(filename, dataDump)
            
         else:
             print 'specified axis is not recognized'

    def _3PEPS_trace(self, T, w2w2p_pump = True):
        """
            Must accept 2d delay scan type
            Assumes typical input dimensions of tau_21 and tau_2p1
            Returns the coherence trace for a specified population time, T
        """
        tau_out = []
        if self.xvar == 'd1' or self.xvar == 't2p1':
            #define tolerances for delay value equivalence
            d1tol = self.datCols[self.xvar][1]
            d1_col = self.xcol
            d2tol = self.datCols[self.yvar][1]
            d2_col = self.ycol
        else:
            d1tol = self.datCols[self.yvar][1]
            d1_col = self.ycol
            d2tol = self.datCols[self.xvar][1]
            d2_col = self.xcol

        if w2w2p_pump:
            #flip sign (ds = -T)
            ds=-T
            #find values such that d2 = ds
            for i in range(len(self.data[0])):
                #find the horizontal part of the data we want
                if (np.abs(self.data[d2_col][i] - ds) <= d2tol) and (self.data[d1_col][i] - ds) <= d1tol:
                    #2p comes first (non-rephasing)
                    #print 'd1,d2 = %s, %s' % (self.data[d1_col][i],self.data[d2_col][i])
                    tau_out.append([
                        self.data[d1_col][i]-ds,
                        self.data[self.zcol][i]])
                
                elif np.abs(self.data[d1_col][i] - ds) <= d1tol and self.data[d2_col][i] - ds <= d2tol:
                    #2 comes first  (rephasing)
                    #print 'd1,d2 = %s, %s' % (self.data[d1_col][i],self.data[d2_col][i])
                    tau_out.append([
                        -(self.data[d2_col][i]-ds),
                        self.data[self.zcol][i]])
        else:
            #pump is w1w2
            #find values such that d2 = ds
            for i in range(len(self.data[0])):
                #find the slice across d2 we want (T=d1 and d2 <= 0)
                if (np.abs(self.data[d1_col][i] - T) <= d1tol) and self.data[d2_col][i] <= d2tol:
                    #2 comes first (rephasing)
                    tau_out.append([
                        -self.data[d2_col][i],
                        self.data[self.zcol][i]])
                #find the antidiagonal slice we want (d1-d2 = T and d2 >= 0)
                elif np.abs(self.data[d1_col][i] - self.data[d2_col][i] - T) <= d1tol and self.data[d2_col][i] >= d2tol:
                    #1 comes first  (non-rephasing)
                    tau_out.append([
                        -self.data[d2_col][i],
                        self.data[self.zcol][i]])
        #order the list
        tau_out.sort()
        tau_out = np.array(zip(*tau_out))
        return np.array(tau_out)

    def export(self, fname=None, cols='v2'):
        """
            generate a dat file using the current zi grid
            cols determines teh output format
            currently ignores constants of the scan
        """

        out_x = self.xi
        out_y = self.yi

        # convert back to default dat units
        if self.xvar in ['w1', 'w2', 'w3', 'wm']:
            out_x = 10**7 / out_x
        if self.yvar in ['w1', 'w2', 'w3', 'wm']:
            out_y = 10**7 / out_x
        out_z = self.zi.ravel()
        out = np.array((out_z.shape[0], 27))
        
        cols = dat.cols_v2
        
        out[cols[self.zvar]] = out_z
        out[cols[self.xvar]] = np.tile(out_x,out.shape[0])
        out[cols[self.yvar]] = np.tile[out_y,out.shape[1]]
        
        np.savetxt(fname, out, fmt='', delimiter='\t')

    def _gengrid(self, xlis=None, ylis=None):
        """
            generate regularly spaced y and x bins to use for gridding 2d data
            grid_factor:  multiplier factor for blowing up grid
            grid all input channels (ai0-ai3) to the set xi and yi attributes
        """
        grid_factor = self.grid_factor
        #if xygrid is already properly set, skip filters and generate the grid
        if xlis is not None:
            self.xi = xlis
        else:
            #if no global axes steps and bounds are defined, find them based on data
            #generate lists from data
            xlis = sorted(self.data[self.xcol])
            xtol = self.datCols[self.xvar][1]
            # values are binned according to their averages now, so min and max 
            #  are better represented
            xs = []
            # check to see if unique values are sufficiently unique
            # deplete to list of values by finding points that are within 
            #  tolerance
            while len(xlis) > 0:
                # find all the xi's that are like this one and group them
                # after grouping, remove from the list
                set_val = xlis[0]
                xi_lis = [xi for xi in xlis if np.abs(set_val - xi) < xtol]
                # the complement of xi_lis is what remains of xlis, then
                xlis = [xi for xi in xlis if not np.abs(xi_lis[0] - xi) < xtol]
                xi_lis_average = sum(xi_lis) / len(xi_lis)
                xs.append(xi_lis_average)
            # create uniformly spaced x and y lists for gridding
            # infinitesimal offset used to properly interpolate on bounds; can
            #  be a problem, especially for stepping axis
            self.xi = np.linspace(min(xs)+1E-06,max(xs)-1E-06,
                                  (len(xs) + (len(xs)-1)*(grid_factor-1)))
        if ylis is not None:
            self.yi = ylis
        else:
            ylis = sorted(self.data[self.ycol])
            ytol = self.datCols[self.yvar][1]
            ys = []
            while len(ylis) > 0:
                set_val = ylis[0]
                yi_lis = [yi for yi in ylis if np.abs(set_val - yi) < ytol]
                ylis = [yi for yi in ylis if not np.abs(yi_lis[0] - yi) < ytol]
                yi_lis_average = sum(yi_lis) / len(yi_lis)
                ys.append(yi_lis_average)
            self.yi = np.linspace(min(ys)+1E-06,max(ys)-1E-06,
                                  (len(ys) + (len(ys)-1)*(grid_factor-1)))

        x_col = self.data[self.xcol] 
        y_col = self.data[self.ycol]
        # grid each of our signal channels
        for key in self.zvars:
            zcol = self.datCols[key][0]
            #make fill value znull right now (instead of average value)
            fill_value = self.znull #self.data[zcol].sum()  / len(self.data[zcol])
            grid_i = griddata((x_col,y_col), self.data[zcol], 
                               (self.xi[None,:],self.yi[:,None]),
                                method='cubic',fill_value=fill_value)
            self.zvars[key] = grid_i
        self.zi = self.zvars[self.zvar]

    def pp_offset(self,znull_range):
        pass
    
        
class NIRscan:
    #this module has yet to be defined, but will handle typical abs scans
    #functions should be able to plot absorbance spectra as well as normalized 2nd derivative (after smoothing)
    font_size = 16

    def __init__(self):
        self.data = list()
        self.unit = 'nm'
        self.xmin = None
        self.xmax = None

    def add(self, filepath=None,dataName=None):
        #import data file--right now designed to be a file from Rob's spectrometer
        #filepath must yield a file
        #create a list of dictionaries?
        #each file data is inserted as a numpy array into the list data ~ [[name, numpyarray],[name, numpy array]]
        if filepath:
            pass
        else:
            filepath = raw_input('Please enter the filepath:')
        if type(filepath) == str:
            pass
        else:
            print 'Error:  filepath needs to be a string'
            return
        
        if os.path.isfile(filepath):
            print 'found the file!'
        else:
            print 'Error: filepath does not yield a file'
            return

        #is the file suffix one that we expect?  warn if it is not!
        filesuffix = os.path.basename(filepath).split('.')[-1]
        if filesuffix != 'txt':
            should_continue = raw_input('Filetype is not recognized and may not be supported.  Continue (y/n)?')
            if should_continue == 'y':
                pass
            else:
                print 'Aborting'
                return

        
        #create a string that will refer to this list
        if dataName:
            pass
        else:
            dataName = raw_input('Please name this data set:  ')
        #now import file as a local var--18 lines are just txt and thus discarded
        rawDat = np.genfromtxt(filepath, skip_header=18)
        dataSet = [dataName, 'nm', np.zeros((2,len(rawDat)))]
        #store the data in the data array--to be indexed as [variable][data]
        for i in range(len(rawDat)):
            for j in range(2):
                dataSet[2][j][i] = float(rawDat[i][j])
        self.data.append(dataSet)
        if max(self.data[-1][2][0]) > self.xmax:
            self.xmax = max(self.data[-1][2][0])
        if min(self.data[-1][2][0]) < self.xmin:
            self.xmin = min(self.data[-1][2][0])
        print 'file has imported!'
    
    def plot(self, scantype='default', xtype='wn'):
        self.ax1 = plt.subplot(211)
        matplotlib.rcParams.update({
            'font.size':self.font_size
        })
        for i in range(len(self.data)):
            plotData = self.data[i][2]
            name = self.data[i][0]
            if xtype == 'wn':
                if self.data[i][1] != 'wn':
                    plotData = self._switchUnits(plotData[0],plotData[1])
            elif xtype == 'nm':
                if self.data[i][1] != 'nm':
                    plotData = self._switchUnits(plotData[0],plotData[1])
            self.ax1.plot(plotData[0], plotData[1], label=name)
        plt.ylabel('abs (a.u.)')
        self.ax1.legend(loc=4)
        self.ax1.grid(b=True)
        #now plot 2nd derivative
        for i in range(len(self.data)):
            self.ax2 = plt.subplot(212, sharex=self.ax1)
            preData = self.data[i][2]
            preData = self._smooth(preData)
            name = self.data[i][0]
            #compute second derivative
            plotData = np.array([10**7 / preData[0][:-2], np.diff(preData[1], n=2)])
            #plotData[1] = plotData[1] / (np.diff(preData[0])[:-1]**2)
            #normalize for comparisons of different scans
            Max = max(max(plotData[1]),-min(plotData[1]))
            #plotData[1] = plotData[1] / Max
            #plot the data!
            self.ax2.plot(plotData[0], plotData[1], label=name)
        self.ax2.grid(b=True)
        plt.xlabel(r'$\bar\nu / cm^{-1}$')

    def _switchUnits(self, xset, yset):
        #converts from wavenumbers to nm and vice-versa
        #sorts data by ascending x values
        xset = 10**7 / xset
        xypairs = zip(xset, yset)
        xypairs.sort()
        return zip(*xypairs)
        
    def _smooth(self, dat1, n=20, window_type='default'):
        #data is an array of type [xlis,ylis]        
        #smooth to prevent 2nd derivative from being noisy
        for i in range(n, len(dat1[1])-n):
            #change the x value to the average
            window = dat1[1][i-n:i+n].copy()
            dat1[1][i] = window.mean()
        return dat1[:][:,n:-n]
    def export(self):
        #write a file with smoothed 2nd derivative data included
        print 'in progress!'

class fit:
    # old_cols used before COLORS support for extra mixers (~November 2013 and
    # earlier)
    old_cols = {
        'num':  [0],
        'set_pt':   [1],
        'd1':   [2],
        'c1':   [3],
        'd2':   [4],
        'c2':   [5],
        'm1':   [6],
        'mu':   [7],
        'amp':   [8],
        'sigma': [9],
        'gof':   [10]
    }
    cols = {
        'num':  [0],
        'set_pt':   [1],
        'd1':   [2],
        'c1':   [3],
        'd2':   [4],
        'c2':   [5],
        'm1':   [6],
        'm2':   [7],
        'm3':   [8],
        'mu':   [9],
        'amp':   [10],
        'sigma': [11],
        'gof':   [12],
        'mismatch': [13]
    }

    def __init__(self, filepath=None, old_cols=False):
        """
            import a fit file
        """
        if filepath:
            pass
        else:
            filepath = raw_input('Please give the absolute file location:')
        #filepath must yield a file
        if os.path.isfile(filepath):
            self.has_data=True
            print 'found the file!'
        else:
            self.has_data = False
            print 'filepath',filepath,'does not yield a file'
            return
        self.filepath, self.filename, self.file_suffix = filename_parse(filepath)
        rawDat = np.genfromtxt(filepath,dtype=np.float) 
        # define arrray used for transposing dat file so cols are first index
        self.data = rawDat.T
        if old_cols:
            self.cols = self.old_cols
        print 'file has imported'
        
def makefit(**kwargs):
    """
    make a fit file filling in only the arguments specified
    kwargs must be lists or arrays of uniform size and 1D shape
    """
    n = len(kwargs.values()[0])
    out = np.zeros((n, 12))
    #first column is just row number (unless overwritten)
    out[:, 0] = range(n)
    for name, value in kwargs.items():
        #all kwargs have to be the same length to make an intelligable array
        if len(value) == n:
            if name in fit.cols.keys():
                out[:, fit.cols[name][0]] = value
            else:
                print 'name {0} is not an appropriate column name'.format(name)
                return
        else:
            print 'Error: not all columns are the same length:  len({0})={1}, len({2}) = {3}'.format(
                kwargs.keys()[0], n, name, len(value))
            return
    return out

def find_name(fname, suffix):
    """
    save the file using fname, and tacking on a number if fname already exists
    iterates until a unique name is found
    returns False if the loop malfunctions
    """
    good_name=False
    # find a name that isn't used by enumerating
    i = 1
    while not good_name:
        try:
            with open(fname+'.'+suffix):
               # file does exist
               # see if a number has already been guessed
               if fname.endswith(' ({0})'.format(i-1)):
                   # cut the old off before putting the new in
                   fname = fname[:-len(' ({0})'.format(i-1))]
               fname += ' ({0})'.format(i)
               i = i + 1
               # prevent infinite loop if the code isn't perfect
               if i > 100:
                   print 'didn\'t find a good name; index used up to 100!'
                   fname = False
                   good_name=True
        except IOError:
            # file doesn't exist and is safe to write to this path
            good_name = True
    return fname

def make_tune(obj, set_var, fname=None, amp='int', center='exp_val', fit=True,
              offset=None):
    """
        function for turning dat scans into tune files using exp value

        takes a dat class object and transforms it into a fit file

        need to specify which axis we need the expectation value from 
        (set_var; either 'x' or 'y'; the other axis will be called int_var)

        amp can measure either amplitude or integrated itensity

        offset:  the a point contained within the set_var range that you wish 
        to be the zero point--if such a point is included, the exp_values will
        be shifted relative to it.  This is convenient in tunetests if you want 
        to have a specific color you want to set zero delay to.
    """
    if set_var not in ['x', 'y', obj.xvar, obj.yvar]:
        print 'Error:  set_var type not supported: {0}'.format(set_var)
    # make sure obj type is appropriate and extract properties
    #zimin = obj.zi.min()
    tempzi = obj.zi - obj.znull
    if set_var in ['y', obj.yvar]:
        int_var = obj.xvar
        set_var = obj.yvar
        set_lis = obj.yi
        #int_lis = obj.xi
        axis = 1
    elif set_var in ['x', obj.xvar]:
        int_var = obj.yvar
        set_var = obj.xvar
        set_lis = obj.xi
        #int_lis = obj.yi
        axis = 0

    # decide what tune type this is
    # if exp value var is delay, call this zerotune, if mono, call it colortune
    if int_var in ['lm', 'wm']:
        fit_type = 'colortune'
    elif int_var in ['d1', 'd2']:
        fit_type = 'zerotune'
    else:
        # not sure what type of fit it is
        fit_type = 'othertune'
    if fit:
        # use least squares fitting to fill in tune values
        plsq = obj.fit_gauss(axis=set_var)
        obj_amp, obj_exp, obj_width, obj_y0 = plsq
    else:
        # use expectation values and explicit measurements to extract values
        # calculate the expectation value to get the peak center
        obj_exp = obj.center(axis=set_var, center=center)
        # calculate the width of the feature using the second moment
        obj_width = obj.exp_value(axis=set_var, moment=2)
        obj_width = np.sqrt(np.abs(obj_width - obj_exp**2))
        # also include amplitude
        if amp == 'int':
            # convert area to max amplitude assuming gaussian form factor
            obj_amp = obj.exp_value(axis=set_var, moment=0, norm=False)
            obj_amp = obj_amp / (np.sqrt(2*np.pi)* obj_width)
        elif amp == 'max':
            obj_amp = tempzi.max(axis=axis) - obj.znull
    # convert obj_width from stdev to fwhm
    obj_width *= 2*np.sqrt(2*np.log(2))
    # offset the values if specified
    if offset is not None:
        f_exp = interp1d(set_lis,obj_exp, kind='linear')
        off = f_exp(offset)
        obj_exp = obj_exp - off
    # convert color to nm for fit file
    if set_var in ['w1', 'w2', 'wm']:
        set_lis = 10**7 / set_lis
    # put wavelength in ascending order
    pts = zip(set_lis, obj_exp, obj_amp)
    pts.sort()
    pts = zip(*pts)
    set_lis, obj_exp, obj_amp = pts
    out = makefit(set_pt=set_lis, mu=obj_exp, amp=obj_amp, sigma=obj_width)
    # make a fit file using the expectation value data
    # first, make sure fname has proper format 
    # append descriptors to filename regardless of whether name is provided
    # emulates how COLORS treats naming
    if fit:
        auto = '{0} {1} fitted'.format(set_var, fit_type)
    elif center == 'exp_val':
        auto = '{0} {1} exp_value center'.format(set_var, fit_type)
    elif center == 'max':
        auto = '{0} {1} max value center'.format(set_var, fit_type)
    else:
        auto = '{0} {1}'.format(set_var, fit_type)
    # suffix:  let me add the .fit filename suffix
    if fname is not None:
        filepath, fname, filesuffix = filename_parse(fname)
        # path:  don't imply path if an absolute path is given
        fname = ' '.join([fname, auto])
        if filepath is None:
            filepath=obj.filepath
    else:
        # use object's filepath as default
        filepath = obj.filepath
        fname = auto
    
    if filepath is not None:
        fname = filepath + '\\' + fname
    fstr = find_name(fname, 'fit')
    if not fstr:
        print 'Could not write file without overwriting an existing file'
        print 'Aborting file write'
        return
    with file(fstr+'.fit', 'a') as exp_file:
        np.savetxt(exp_file, out, delimiter='\t', fmt='%.3f')
    print 'saved as {0}'.format(fstr+'.fit')

def filename_parse(fstr):
    """
    parses a filepath string into it's path, name, and suffix
    """
    split = fstr.split('\\')
    if len(split) == 1:
        file_path = None
    else:
        file_path = '\\'.join(split[0:-1])
    split2 = split[-1].split('.')
    # try and guess whether a suffix is there or not
    # my current guess is based on the length of the final split string
    # suffix is either 3 or 4 characters
    if len(split2[-1]) == 3 or len(split2[-1]) == 4:
        file_name = '.'.join(split2[0:-1])
        file_suffix = split2[-1]
    else:
        file_name = split[-1]
        file_suffix = None
    return file_path, file_name, file_suffix    
    
def gauss_residuals(p, y, x):
    """
    calculates the residual between y and a gaussian with:
        amplitude p[0]
        mean p[1]
        stdev p[2]
    """
    A, mu, sigma, offset = p
    err = y-A*np.exp(-(x-mu)**2 / (2*sigma**2)) - offset
    return err

