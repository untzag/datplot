#datplot_ui
#by Blaise Thompson - blaise@untzag.com
#
#a program to plot .dat files (file formats as saved by COLORS)
#with a user friendly interface and all the 'normal' features built in
#
#built around fscolors.py, by Dan Kohler

#import general python pakages--------------------------------------------------

#os interaction packages
import os
import sys
import imp
import copy
import inspect
import subprocess
import ConfigParser
import glob #used to search through folders for files

#qt is used for gui handling, see Qtforum.org for info
from PyQt4.QtCore import * #* means import all
from PyQt4.QtGui import *

#matplotlib is used for plot generation and manipulation
import matplotlib
matplotlib.use('Qt4Agg')
print 'matplotlib version loaded:', matplotlib.__version__
print 'please note: datplot_ui forces Qt4Agg backend!'
import matplotlib.pyplot as plt
import matplotlib.colors as mplcolors
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.gridspec as grd
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.animation as animation

#numpy is used for general math in python
import numpy as np
from numpy import sin, cos

#scipy is used for some nice array manipulation
import scipy
from scipy.interpolate import griddata, interp1d
import scipy.integrate as integrate

#get filepath of current folder for relative filepath purposes------------------

filepath_of_folder = os.path.dirname( __file__ )

#import datplot-specific python pakages-----------------------------------------

#fscolors
fscolors_filepath = os.path.join(filepath_of_folder, 'fscolors')
sys.path.insert(0, fscolors_filepath)
import fscolors as f

#place windows backend applications into system PATH variable-------------------

#ffmpeg
ffmpeg_filepath = os.path.join(filepath_of_folder, 'program files', 'ffmpeg', 'bin')
os.environ['PATH'] += os.pathsep + ffmpeg_filepath
my_writer = animation.FFMpegWriter()

#define hard-coded global variables---------------------------------------------

#defaults for linetypes
#contour lines
line_contour_color_default = '#000000' #black
line_contour_line_width_default = 1
line_contour_line_style_default = 'solid'
#expectation value line
line_exp_color_default = '#000000' #black
line_exp_line_width_default = 2
line_exp_line_style_default = 'dashed'
#max value line
line_max_color_default = '#000000' #black
line_max_line_width_default = 2
line_max_line_style_default = 'dotted'
#binned value line
line_bin_color_default = '#FF0000' #red
line_bin_line_width_default = 2
line_bin_line_style_default = 'solid'
#abs value lines
line_abs_color_default = '#0000FF' #blue
line_abs_line_width_default = 2
line_abs_line_style_default = 'solid'

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        #program initiation 
        
        #initiate window
        QMainWindow.__init__(self, parent)
        
        #set window title
        self.setWindowTitle('.dat plotting (and more) in python')

        #set window size        
        self.window_verti_size = 240 #a row is ~20
        self.window_horiz_size = 600
        self.setGeometry(0,0, self.window_horiz_size, self.window_verti_size)
        self._center()
        self.resize(self.window_horiz_size, self.window_verti_size) 
        self.setMinimumSize(self.window_horiz_size, self.window_verti_size)
        self.setMaximumSize(self.window_horiz_size, self.window_verti_size)
        
        #call create_main_frame function (will fill in all custom elements)
        self.create_main_frame()
        
        #hide stuff
        self.normalization_options_widget.hide()
        self.additional_files_widget.hide()
        self.data_processing_widget.hide()
        self.data_presentation_widget.hide()
        self.label_widget.hide()

        #fill in line parameters to default
        self.linetype_choose_apply_defaults(line_to_control = 'contour', startup = True)
        self.linetype_choose_apply_defaults(line_to_control = 'bin', startup = True)
        self.linetype_choose_apply_defaults(line_to_control = 'max', startup = True)
        self.linetype_choose_apply_defaults(line_to_control = 'abs', startup = True)
        self.linetype_choose_apply_defaults(line_to_control = 'exp', startup = True)
        
        #initiate in 'flag globals'
        self.last_file_was_colortune = False
        self.loading_dat_file_now = False
        self.animating = False
        
        print ' '
        print 'datplot_ui startup complete with no errors'
                       
    def create_main_frame(self):
        #where is where all of the main ui stuff gets defined (what & where)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #basic properties for ui
        
        self.main_frame = QWidget() #type of frame (QWidget is a 'normal' frame)
        vbox = QVBoxLayout()

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #creating and 'wiring' ui elements

        #data file input########################################################
        
        #data file input line 0- - - - - - - - - - - - - - - - - - - - - - - - -
        
        file_input_label = QHBoxLayout()
        for w in [ QLabel("load data file:  ----------------------------------------------------------------------------------------------------------------------------------------------------------")]:
          file_input_label.addWidget(w)
          file_input_label.setAlignment(w, Qt.AlignVCenter)
        vbox.addLayout(file_input_label)

        #data file input line 1- - - - - - - - - - - - - - - - - - - - - - - - -      

        #constant to hold info re: main data loaded
        self.main_data_loaded = False          
        
        #the 'load file' button
        self.load_button = QPushButton("&load file")
        self.load_button.clicked.connect(lambda: self.load_file('main .dat file'))
                
        #the input textbox
        self.dat_filepath_textbox = QLineEdit()
        self.dat_filepath_textbox.setText('raw filepath')
        
        #the column type combobox
        self.column_combo = QComboBox()
        column_options = ['.dat format v2', '.dat format v1', '.dat format v0']
        self.column_combo.setToolTip('.dat v0 - pre winter 2012\n.dat v1 - winter 2012 through spring 2014\n.dat v2 - post spring 2014')
        self.column_combo.addItems(column_options)
        self.column_combo.currentIndexChanged.connect(lambda: self.datfile_info_extract('column_combo change'))
        self.column_combo.setMinimumWidth(100)
        
        file_input = QHBoxLayout()
        for w in [ self.load_button,
                   self.dat_filepath_textbox,
                   self.column_combo]:
            file_input.addWidget(w)
            file_input.setAlignment(w, Qt.AlignVCenter)
        vbox.addLayout(file_input)
        
        #data file input line 2- - - - - - - - - - - - - - - - - - - - - - - - -        

        my_row = QHBoxLayout()

        var_combobox_width = 100
        var_combobox_spacing = 20

        #the xvar combobox
        self.xvar_combo = QComboBox()
        xvar_options = ['choose...', 
                        'w1', 
                        'w2', 
                        'wm', 
                        'w1=w2', 
                        'w1=wm',
                        'w2=wm',
                        'w1=w2=wm',
                        'd1', 
                        'd2', 
                        'd1=d2']
        self.xvar_combo.addItems(xvar_options)
        self.xvar_combo.setMinimumWidth(var_combobox_width)
        self.xvar_combo.currentIndexChanged.connect(lambda: self.gui_handler('change to dimension comboboxes'))
        my_row.addWidget(QLabel("xvar:"))
        my_row.addWidget(self.xvar_combo)
        my_row.addSpacing(var_combobox_spacing)
        
        #the yvar combobox
        self.yvar_combo = QComboBox()
        yvar_options = ['choose...', 
                        'w1', 
                        'w2', 
                        'wm', 
                        'w1=w2', 
                        'w1=wm',
                        'w2=wm',
                        'w1=w2=wm',
                        'd1', 
                        'd2', 
                        'd1=d2']
        self.yvar_combo.addItems(yvar_options)
        self.yvar_combo.setMinimumWidth(var_combobox_width)
        self.yvar_combo.currentIndexChanged.connect(lambda: self.gui_handler('change to dimension comboboxes'))
        my_row.addWidget(QLabel("yvar:"))
        my_row.addWidget(self.yvar_combo)
        my_row.addSpacing(var_combobox_spacing)

        #the zvar combobox
        self.zvar_combo = QComboBox()
        zvar_options = ['ai0', 'ai1', 'ai2', 'ai3', 'ai4']
        self.zvar_combo.addItems(zvar_options)
        my_row.addWidget(QLabel("zvar:"))
        my_row.addWidget(self.zvar_combo)
        my_row.addSpacing(var_combobox_spacing+30)
        
        #colortune toggle
        self.colortune_toggle = QCheckBox('colortune')
        self.colortune_toggle.setToolTip('when checked, will transform mono axes to mono-OPA\nuseful for seeing how well tuned you are across a region')
        self.colortune_toggle.stateChanged.connect(lambda: self.gui_handler('change to dimension comboboxes'))
        my_row.addWidget(self.colortune_toggle)
    
        #reverse OPA roles toggle
        self.reverse_opa_roles_toggle = QCheckBox("reverse OPAs")
        self.reverse_opa_roles_toggle.setDisabled(True)
        self.reverse_opa_roles_toggle.setToolTip('FEATURE BROKEN WITH UPDATE WILL ADD IN AGAIN LATER\nunchecked (default): OPA1=w1, OPA2=w2\nchecked (option): OPA1=w2, OPA2=w1')
        my_row.addWidget(self.reverse_opa_roles_toggle)
        
        my_row.setAlignment(Qt.AlignVCenter)
        vbox.addLayout(my_row)
        
        #optional additional files##############################################
        
        self.additional_files_widget = QWidget()

        self.verti_size_additional_files = 100        

        my_grid = QGridLayout()
        
        #optional additional files line 0- - - - - - - - - - - - - - - - - - - -
                
        self.additional_files_hidden = QCheckBox('')
        self.additional_files_hidden.clicked.connect(lambda: self._hide('additional files')) 
        
        optional_file_input_label = QHBoxLayout()
        for w in [ QLabel("load optional additional files:  ---------------------------------------------------------------------------------------------------------------------------------"),
                   self.additional_files_hidden]:
          optional_file_input_label.addWidget(w)
          optional_file_input_label.setAlignment(w, Qt.AlignVCenter)
        vbox.addLayout(optional_file_input_label)
        
        #optional additional files line 1- - - - - - - - - - - - - - - - - - - -
        #abs scan
        
        abs_scan_row = 0

        #constant to hold info re: abs data loaded
        self.abs_data_loaded = False        
        
        #abs powersmoothness load button
        self.abs_load_button = QPushButton("load spectral data")
        self.abs_load_button.clicked.connect(lambda: self.load_file('jasco abs')) 
        my_grid.addWidget(self.abs_load_button, abs_scan_row, 0)   
        
        #abs powersmoothness textboox
        self.abs_filepath_textbox = QLineEdit()
        self.abs_filepath_textbox.setText('raw filepath')
        my_grid.addWidget(self.abs_filepath_textbox, abs_scan_row, 1)
        
        #x toggle
        self.abs_along_x_toggle = QCheckBox('x')
        self.abs_along_x_toggle.setDisabled(True)
        
        #y toggle
        self.abs_along_y_toggle = QCheckBox('y')
        self.abs_along_y_toggle.setDisabled(True)
        
        my_grid.addWidget(QLabel('show along...'), abs_scan_row, 2)
        my_row = QHBoxLayout()
        my_row.addWidget(self.abs_along_x_toggle)
        my_row.addWidget(self.abs_along_y_toggle)
        my_grid.addLayout(my_row, abs_scan_row, 3)        
        
        #the abs value linetype control button
        self.abs_linetype_button = QPushButton("line properties")
        self.abs_linetype_button.clicked.connect(lambda: self.linetype_choose_window_show('abs_data'))
        self.abs_linetype_button.setMaximumWidth(85)
        my_grid.addWidget(self.abs_linetype_button, abs_scan_row, 4)

        #plot abs scan
        self.plot_abs_button = QPushButton('plot abs data')
        self.abs_linetype_button.clicked.connect(lambda: self.on_plot_abs())
        my_grid.addWidget(self.plot_abs_button, abs_scan_row, 5)
        
        #optional additional files line 1- - - - - - - - - - - - - - - - - - - -
        #script
        
        script_row = 1      
        
        #script load button
        self.script_load_button = QPushButton("load extension")
        self.script_load_button.clicked.connect(lambda: self.load_file('script')) 
        my_grid.addWidget(self.script_load_button, script_row, 0)   
        
        #script table
        self.script_table = QTableWidget()
        self.script_table.insertColumn(0)
        self.script_table.setToolTip('extensions for datplot!\nrun before any other modifications - immediatly after calling fscolors.dat()\nrun in order of appearance in this table\nsee example in \extensions to make your own')
        my_grid.addWidget(self.script_table, script_row, 1)
        
        #script load button
        self.script_clear_button = QPushButton("remove selected")
        self.script_clear_button.clicked.connect(lambda: self.gui_handler('clear extensions')) 
        my_grid.addWidget(self.script_clear_button, script_row, 2)    
        
        #use script checkbox
        self.script_toggle = QCheckBox('use')
        self.script_toggle.setDisabled(True)
        my_grid.addWidget(self.script_toggle, script_row, 3)
        
        #optional additional files QTstuff - - - - - - - - - - - - - - - - - - -
        
        #set margins to zero
        self.additional_files_widget.setContentsMargins(0, 0, 0, 0)     
        my_grid.setContentsMargins(0, 0, 0, 0) 
               
        #add into higher level structure
        self.additional_files_widget.setLayout(my_grid)        
        vbox.addWidget(self.additional_files_widget)    
        
        #normalization options##################################################
        
        self.normalization_options_widget = QWidget()

        self.verti_size_normalization_options = 160
        
        my_grid = QGridLayout()        
        
        #normalization options line 0- - - - - - - - - - - - - - - - - - - - - -

        my_box = QHBoxLayout()        
        
        self.normalization_options_hidden = QCheckBox('')
        self.normalization_options_hidden.clicked.connect(lambda: self._hide('normalization options')) 
        
        for w in [ QLabel("normalize:  ------------------------------------------------------------------------------------------------------------------------------------------"), 
                   self.normalization_options_hidden]:
          my_box.addWidget(w)
          my_box.setAlignment(w, Qt.AlignVCenter)
        vbox.addLayout(my_box)
        
        #normalization options line 1- - - - - - - - - - - - - - - - - - - - - -
        #OPA1 pyro
        
        pyro1_row = 0
        
        my_grid.addWidget(QLabel('OPA1 pyro:'), pyro1_row, 0)
        
        my_grid.addWidget(QLabel('                                          channel:'), pyro1_row, 1)
        
        #opa1 pyro zvar combobox
        self.pyro1_zvar_combo = QComboBox()
        self.pyro1_zvar_combo.addItems(zvar_options)
        self.pyro1_zvar_combo.setCurrentIndex(1)
        my_grid.addWidget(self.pyro1_zvar_combo, pyro1_row, 2)
        
        #opa1 pyro znull textbox
        self.pyro1_znull_textbox = QLineEdit()
        self.pyro1_znull_textbox.setText('0.0')
        my_grid.addWidget(QLabel('znull:'), pyro1_row, 3)
        my_grid.addWidget(self.pyro1_znull_textbox, pyro1_row, 4)
        
        #opa1 pyro toggle
        self.pyro1_norm_toggle = QCheckBox("use")
        my_grid.addWidget(self.pyro1_norm_toggle, pyro1_row, 5)
        
        #opa1 pyro power textbox
        pstextboxsize = 30
        self.pyro1_power_textbox = QLineEdit()
        self.pyro1_power_textbox.setText('1')
        self.pyro1_power_textbox.setMaximumWidth(pstextboxsize)
        my_grid.addWidget(QLabel("to power:"), pyro1_row, 6)
        my_grid.addWidget(self.pyro1_power_textbox, pyro1_row, 7)
        
        #normalization options line 2- - - - - - - - - - - - - - - - - - - - - -
        #OPA2 pyro
        
        pyro2_row = 1
        
        my_grid.addWidget(QLabel('OPA2 pyro:'), pyro2_row, 0)
        
        my_grid.addWidget(QLabel('                                          channel:'), pyro2_row, 1)
        
        #opa2 pyro zvar combobox
        self.pyro2_zvar_combo = QComboBox()
        self.pyro2_zvar_combo.addItems(zvar_options)
        self.pyro2_zvar_combo.setCurrentIndex(2)
        my_grid.addWidget(self.pyro2_zvar_combo, pyro2_row, 2)
        
        #opa2 pyro znull textbox
        self.pyro2_znull_textbox = QLineEdit()
        self.pyro2_znull_textbox.setText('0.0')
        my_grid.addWidget(QLabel('znull:'), pyro2_row, 3)
        my_grid.addWidget(self.pyro2_znull_textbox, pyro2_row, 4)
       
        #opa2 pyro toggle
        self.pyro2_norm_toggle = QCheckBox("use")
        my_grid.addWidget(self.pyro2_norm_toggle, pyro2_row, 5)
        
        #opa2 pyro spinbox
        pstextboxsize = 30
        self.pyro2_power_textbox = QLineEdit()
        self.pyro2_power_textbox.setText('2')
        self.pyro2_power_textbox.setMaximumWidth(pstextboxsize)
        my_grid.addWidget(QLabel("to power:"), pyro2_row, 6)
        my_grid.addWidget(self.pyro2_power_textbox, pyro2_row, 7)
        
        #normalization options line 3- - - - - - - - - - - - - - - - - - - - - -
        #OPA1 powersmoothness
        
        OPA1ps_row = 2
        
        #opa1 powersmoothness load button
        self.opa1ps_load_button = QPushButton("load OPA1 normalization file")
        self.opa1ps_load_button.clicked.connect(lambda: self.load_file('OPA1 norm')) 
        my_grid.addWidget(self.opa1ps_load_button, OPA1ps_row, 0)             
        
        #opa1 powersmoothness textboox
        self.opa1ps_filepath_textbox = QLineEdit()
        self.opa1ps_filepath_textbox.setText('raw filepath (.dat or .fit)')
        my_grid.addWidget(self.opa1ps_filepath_textbox, OPA1ps_row, 1)
        
        #opa1 powersmoothness zvar combobox
        self.opa1_zvar_combo = QComboBox()
        self.opa1_zvar_combo.addItems(zvar_options)
        self.opa1_zvar_combo.setToolTip('only applies for .dat files')
        my_grid.addWidget(self.opa1_zvar_combo, OPA1ps_row, 2)
        
        #opa1 powersmoothness znull textbox
        self.opa1_znull_textbox = QLineEdit()
        self.opa1_znull_textbox.setText('0.0')
        self.opa1_znull_textbox.setDisabled(True)
        self.opa1_znull_textbox.setToolTip('placeholder for future feature')
        my_grid.addWidget(QLabel('znull:'), OPA1ps_row, 3)
        my_grid.addWidget(self.opa1_znull_textbox, OPA1ps_row, 4)
        
        #opa1 powersmoothness toggle
        self.opa1ps_norm_toggle = QCheckBox("use")
        my_grid.addWidget(self.opa1ps_norm_toggle, OPA1ps_row, 5)
        self.opa1ps_norm_toggle.setDisabled(True)
        
        #opa1 powersmoothness spinbox
        pstextboxsize = 30
        self.opa1ps_power_textbox = QLineEdit()
        self.opa1ps_power_textbox.setText('1')
        self.opa1ps_power_textbox.setMaximumWidth(pstextboxsize)
        my_grid.addWidget(QLabel("to power:"), OPA1ps_row, 6)
        my_grid.addWidget(self.opa1ps_power_textbox, OPA1ps_row, 7)
        
        #normalization options line 4- - - - - - - - - - - - - - - - - - - - - -
        #OPA2 powersmoothness
        
        OPA2ps_row = 3
        
        #opa2 powersmoothness load button
        self.opa2ps_load_button = QPushButton("load OPA2 normalization file")
        self.opa2ps_load_button.clicked.connect(lambda: self.load_file('OPA2 norm')) 
        my_grid.addWidget(self.opa2ps_load_button, OPA2ps_row, 0)             
        
        #opa2 powersmoothness textboox
        self.opa2ps_filepath_textbox = QLineEdit()
        self.opa2ps_filepath_textbox.setText('raw filepath (.dat or .fit)')
        my_grid.addWidget(self.opa2ps_filepath_textbox, OPA2ps_row, 1)
        
        #opa2 powersmoothness zvar combobox
        self.opa2_zvar_combo = QComboBox()
        self.opa2_zvar_combo.addItems(zvar_options)
        self.opa2_zvar_combo.setToolTip('only applies for .dat files')
        my_grid.addWidget(self.opa2_zvar_combo, OPA2ps_row, 2)
        
        #opa2 powersmoothness znull textbox
        self.opa2_znull_textbox = QLineEdit()
        self.opa2_znull_textbox.setText('0.0')
        self.opa2_znull_textbox.setDisabled(True)
        self.opa2_znull_textbox.setToolTip('placeholder for future feature')
        my_grid.addWidget(QLabel('znull:'), OPA2ps_row, 3)
        my_grid.addWidget(self.opa2_znull_textbox, OPA2ps_row, 4)
        
        #opa2 powersmoothness toggle
        self.opa2ps_norm_toggle = QCheckBox("use")
        my_grid.addWidget(self.opa2ps_norm_toggle, OPA2ps_row, 5)
        self.opa2ps_norm_toggle.setDisabled(True)
        
        #opa2 powersmoothness spinbox
        self.opa2ps_power_textbox = QLineEdit()
        self.opa2ps_power_textbox.setText('1')
        self.opa2ps_power_textbox.setMaximumWidth(pstextboxsize)
        my_grid.addWidget(QLabel("to power:"), OPA2ps_row, 6)
        my_grid.addWidget(self.opa2ps_power_textbox, OPA2ps_row, 7)
        
        #normalization options line 5- - - - - - - - - - - - - - - - - - - - - -
        #2D normalization data
        
        norm2D_row = 4
        
        #2D normalization data load button
        self.norm2D_load_button = QPushButton('load 2D normalization mask')
        self.norm2D_load_button.clicked.connect(lambda: self.load_file('norm2D')) 
        my_grid.addWidget(self.norm2D_load_button, norm2D_row, 0)             
        
        #2D normalization data textboox
        self.norm2D_filepath_textbox = QLineEdit()
        self.norm2D_filepath_textbox.setText('raw filepath (.dat)')
        my_grid.addWidget(self.norm2D_filepath_textbox, norm2D_row, 1)
        
        #2D normalization data zvar combobox
        self.norm2D_zvar_combo = QComboBox()
        self.norm2D_zvar_combo.addItems(zvar_options)
        my_grid.addWidget(self.norm2D_zvar_combo, norm2D_row, 2)
        
        #2D normalization data zmin textbox
        self.norm2D_znull_textbox = QLineEdit()
        self.norm2D_znull_textbox.setText('0.0')
        my_grid.addWidget(QLabel('znull:'), norm2D_row, 3)
        my_grid.addWidget(self.norm2D_znull_textbox, norm2D_row, 4)
        
        #2D normalization data toggle
        self.norm2D_norm_toggle = QCheckBox("use")
        my_grid.addWidget(self.norm2D_norm_toggle, norm2D_row, 5)
        self.norm2D_norm_toggle.setDisabled(True)  
        
        #normalization options line 6- - - - - - - - - - - - - - - - - - - - - -
        #plot mask
        
        plot_mask_row = 5
        
        my_grid.addWidget(QLabel('visualize normalization:'), plot_mask_row, 0)
        
        #type combo
        self.plot_mask_combo = QComboBox()
        plot_mask_combo_options = ['mask',
                                   'mask & final data',
                                   'raw data & mask',
                                   'raw data & final data',
                                   'raw data & mask & final data']
        self.plot_mask_combo.addItems(plot_mask_combo_options)
        self.plot_mask_combo.setDisabled(True)
        self.plot_mask_combo.setToolTip('for now, you may only plot the aggregate mask\nnew features should be coming later')
        my_grid.addWidget(self.plot_mask_combo, plot_mask_row, 1)
        
        #plot button
        self.plot_mask_button = QPushButton('plot')
        self.plot_mask_button.setMaximumWidth(40)
        self.plot_mask_button.clicked.connect(lambda: self.on_plot('plot', 'normalization mask'))
        my_grid.addWidget(self.plot_mask_button, plot_mask_row, 2)
        
        #plot button
        
        #normalization options QTstuff - - - - - - - - - - - - - - - - - - - - -
        
        #set margins to zero
        self.normalization_options_widget.setContentsMargins(0, 0, 0, 0)     
        my_grid.setContentsMargins(0, 0, 0, 0) 
               
        self.normalization_options_widget.setLayout(my_grid)        
        vbox.addWidget(self.normalization_options_widget)       
        
        #data processing options################################################
        
        self.data_processing_widget = QWidget()

        self.verti_size_data_processing = 90        

        my_grid = QGridLayout()
        
        #data processing options line 0- - - - - - - - - - - - - - - - - - - - -
        
        self.data_processing_hidden = QCheckBox('')
        self.data_processing_hidden.clicked.connect(lambda: self._hide('data processing')) 
        
        data_processing_label = QHBoxLayout()
        for w in [ QLabel("data processing:  -----------------------------------------------------------------------------------------------------------------------------"),
                   self.data_processing_hidden]:
          data_processing_label.addWidget(w)
          data_processing_label.setAlignment(w, Qt.AlignVCenter)
        vbox.addLayout(data_processing_label)
        
        #data processing options line 1- - - - - - - - - - - - - - - - - - - - -
        #settings
        
        settings_row_number = 0
        
        my_grid.addWidget(QLabel(".fit settings:"), settings_row_number, 0)
        
        my_grid.addWidget(QLabel("              amplitude calc:"), settings_row_number, 1)         
        
        #amplitude type combobox
        self.amp_type_comobobox = QComboBox()
        amp_type_comobobox_options = ['by binning', 'by max value']
        self.amp_type_comobobox.addItems(amp_type_comobobox_options)
        my_grid.addWidget(self.amp_type_comobobox, settings_row_number, 2)
        
        #fit format combobox
        self.fit_format_comobobox = QComboBox()
        fit_format_comobobox_options = ['new .fit', 'old .fit']
        self.fit_format_comobobox.setToolTip('.fit format global')
        self.fit_format_comobobox.addItems(fit_format_comobobox_options)
        my_grid.addWidget(self.fit_format_comobobox, settings_row_number, 4)        
        
        #data processing options line 2- - - - - - - - - - - - - - - - - - - - -
        #binning
        
        binning_row_number = 1
        
        my_grid.addWidget(QLabel("binned value:"), binning_row_number, 0)
        
        #x sideplot toggle
        self.xsideplot_toggle = QCheckBox("x")
        
        #y sideplot toggle
        self.ysideplot_toggle = QCheckBox("y")
        
        my_grid.addWidget(QLabel("               show along..."), binning_row_number, 1)
        my_row = QHBoxLayout()
        my_row.addWidget(self.xsideplot_toggle)
        my_row.addWidget(self.ysideplot_toggle)
        my_grid.addLayout(my_row, binning_row_number, 2)

        #the binned value linetype control button
        self.binned_value_linetype_button = QPushButton("line properties")
        self.binned_value_linetype_button.clicked.connect(lambda: self.linetype_choose_window_show('binned_value'))
        my_grid.addWidget(self.binned_value_linetype_button, binning_row_number, 3)
        
        #data processing options line 3- - - - - - - - - - - - - - - - - - - - -
        #max

        max_row_number = 2      
        
        my_grid.addWidget(QLabel("max value:"), max_row_number, 0)
        
        #the choose max value dimension combobox
        self.max_value_dimension_combobox = QComboBox()
        max_value_dimension_combobox_options = ['none', 'against x', 'against y']
        self.max_value_dimension_combobox.addItems(max_value_dimension_combobox_options)
        self.max_value_dimension_combobox.currentIndexChanged.connect(lambda: self.gui_handler('max value combobox changed'))
        my_grid.addWidget(self.max_value_dimension_combobox, max_row_number, 1)
        
        #the show max value toggle
        self.max_value_show_toggle = QCheckBox('show on 2D plot')
        my_grid.addWidget(self.max_value_show_toggle, max_row_number, 2)
        self.max_value_show_toggle.setDisabled(True)
        
        #the max value linetype control button
        self.max_value_linetype_button = QPushButton("line properties")
        self.max_value_linetype_button.clicked.connect(lambda: self.linetype_choose_window_show('max_value'))
        my_grid.addWidget(self.max_value_linetype_button, max_row_number, 3)
        
        #the save .fit file button
        self.save_max_fit_file_button = QPushButton('save as .fit file')
        self.save_max_fit_file_button.clicked.connect(lambda: self.on_save('max_value .fit'))
        self.save_max_fit_file_button.setToolTip('placeholder for future feature')
        my_grid.addWidget(self.save_max_fit_file_button, max_row_number, 4)
        self.save_max_fit_file_button.setDisabled(True)   
        
        #data processing options line 4- - - - - - - - - - - - - - - - - - - - -
        #expectation value
        
        expectation_row_number = 3
        
        my_grid.addWidget(QLabel("expectation value:"), expectation_row_number, 0)
        
        #the choose expectation value dimension combobox
        self.exp_value_dimension_combobox = QComboBox()
        exp_value_combobox_options = ['none', 'against x', 'against y']
        self.exp_value_dimension_combobox.addItems(exp_value_combobox_options)
        self.exp_value_dimension_combobox.currentIndexChanged.connect(lambda : self.gui_handler('exp value combobox changed'))
        my_grid.addWidget(self.exp_value_dimension_combobox, expectation_row_number, 1)
        
        #the show expectation value toggle
        self.exp_value_show_toggle = QCheckBox('show on 2D plot')
        my_grid.addWidget(self.exp_value_show_toggle, expectation_row_number, 2)
        self.exp_value_show_toggle.setDisabled(True)
        
        #the expectation value linetype control button
        self.expectation_value_linetype_button = QPushButton("line properties")
        self.expectation_value_linetype_button.clicked.connect(lambda: self.linetype_choose_window_show('exp_value'))
        my_grid.addWidget(self.expectation_value_linetype_button, expectation_row_number, 3)
        
        #the save .fit file button
        self.save_fit_file_button = QPushButton('save as .fit file')
        self.save_fit_file_button.clicked.connect(lambda: self.on_save('exp_value .fit'))
        my_grid.addWidget(self.save_fit_file_button, expectation_row_number, 4)
        self.save_fit_file_button.setDisabled(True)
        
        #data processing QTstuff - - - - - - - - - - - - - - - - - - - - - - - -
        
        #set margins to zero
        self.data_processing_widget.setContentsMargins(0, 0, 0, 0)     
        my_grid.setContentsMargins(0, 0, 0, 0) 
               
        #add into higher level structure
        self.data_processing_widget.setLayout(my_grid)        
        vbox.addWidget(self.data_processing_widget)
        
        #data presentation######################################################
        
        self.data_presentation_widget = QWidget()

        self.verti_size_data_presentation = 160        

        my_grid = QGridLayout()        
        
        #data presentation options line 0- - - - - - - - - - - - - - - - - - - -
        
        self.data_presentation_hidden = QCheckBox('')
        self.data_presentation_hidden.clicked.connect(lambda: self._hide('data presentation'))
         
        data_presentation_label = QHBoxLayout()
        for w in [ QLabel("data presentation:  -----------------------------------------------------------------------------------------------------------------------------"),
                   self.data_presentation_hidden]:
          data_presentation_label.addWidget(w)
          data_presentation_label.setAlignment(w, Qt.AlignVCenter)
        vbox.addLayout(data_presentation_label)
        
        #data presentation options line 1- - - - - - - - - - - - - - - - - - - -
        
        units_row_number = 0
        
        my_grid.addWidget(QLabel('units:'), units_row_number, 0)
        
        #color units comobobox
        self.color_units_combo = QComboBox()
        color_units_options = ['wn',
                               'nm']
        self.color_units_combo.addItems(color_units_options)
        self.color_units_combo.currentIndexChanged.connect(lambda: self.datfile_info_extract('data file'))
        self.color_units_combo.currentIndexChanged.connect(lambda: self.label_autofill('x axis'))
        self.color_units_combo.currentIndexChanged.connect(lambda: self.label_autofill('y axis'))
        self.color_units_combo.currentIndexChanged.connect(lambda: self.label_autofill('title'))
        color_label = QLabel('color:')
        my_grid.addWidget(color_label, units_row_number, 1)
        my_grid.setAlignment(color_label, Qt.AlignRight)
        my_grid.addWidget(self.color_units_combo, units_row_number, 2)
        
        #delay units comobobox
        self.delay_units_combo = QComboBox()
        delay_units_options = ['fs',
                               'ps',
                               'ns']
        self.delay_units_combo.addItems(delay_units_options)
        self.delay_units_combo.setDisabled(True)
        self.delay_units_combo.setToolTip('placeholder for future feature')
        delay_label = QLabel('delay:')
        my_grid.addWidget(delay_label, units_row_number, 3)
        my_grid.setAlignment(delay_label, Qt.AlignRight)
        my_grid.addWidget(self.delay_units_combo, units_row_number, 4)
        
        #data presentation options line 2- - - - - - - - - - - - - - - - - - - -
        
        interpolation_row_number = 1      
        
        my_grid.addWidget(QLabel("interpolation:"), interpolation_row_number, 0)
        
        #the plot type combobox
        self.plot_type_combo = QComboBox()
        plot_type_combo_options = ['interpolate', 'plot pixels']
        self.plot_type_combo.addItems(plot_type_combo_options)
        self.plot_type_combo.setMinimumWidth(40)
        self.plot_type_combo.setToolTip('interpolate - fill in spaces between gridpoints with delaunay interpolation\npixels - plot one \'pixel\' for each gridpoint')
        self.plot_type_combo.currentIndexChanged.connect(lambda: self.gui_handler())
        interpolation_label = QLabel('interpolation type:')
        my_grid.addWidget(interpolation_label, interpolation_row_number, 1)
        my_grid.setAlignment(interpolation_label, Qt.AlignRight)
        my_grid.addWidget(self.plot_type_combo, interpolation_row_number, 2)

        #the grid factor input spinbox
        self.gridfactor_choose = QSpinBox()
        self.gridfactor_choose.setSingleStep(1)
        self.gridfactor_choose.setMinimum(1)
        self.gridfactor_choose.setValue(2)
        interpolation_factor_label = QLabel('interpolation factor:')
        my_grid.addWidget(interpolation_factor_label, interpolation_row_number, 3)
        my_grid.setAlignment(interpolation_factor_label, Qt.AlignRight)
        my_grid.addWidget(self.gridfactor_choose, interpolation_row_number, 4)
        
        #data presentation options line 3- - - - - - - - - - - - - - - - - - - -
        
        smoothing_row_number = 2
        
        my_grid.addWidget(QLabel('smoothing:'), smoothing_row_number, 0)
        
        smoothing_label = QLabel("with # points along...")
        my_grid.addWidget(smoothing_label, smoothing_row_number, 1)     
        my_grid.setAlignment(smoothing_label, Qt.AlignRight)
               
        #the xsmooth spinbox
        self.xsmooth_choose = QSpinBox()
        self.xsmooth_choose.setSingleStep(1)
        self.xsmooth_choose.setValue(2)
        my_row = QHBoxLayout()
        my_row.addWidget(QLabel("x:"))
        my_row.addWidget(self.xsmooth_choose)
        
        #the ysmooth spinbox
        self.ysmooth_choose = QSpinBox()
        self.ysmooth_choose.setSingleStep(1)
        self.ysmooth_choose.setValue(2)
        my_row.addWidget(QLabel("y:"))
        my_row.addWidget(self.ysmooth_choose)
        my_grid.addLayout(my_row, smoothing_row_number, 2)
        
        #the smoothing toggle
        self.smoothing_toggle = QCheckBox("smooth")
        self.smoothing_toggle.stateChanged.connect(lambda: self.gui_handler('smoothing toggle changed'))
        self.smoothing_toggle.setToolTip('2D kaiser window smoothing')
        my_grid.addWidget(self.smoothing_toggle, smoothing_row_number, 3)   
        my_grid.setAlignment(self.smoothing_toggle, Qt.AlignRight)
        
        #the visualize smoothing push button
        self.plot_smoothing_button = QPushButton('visualize smoothing')
        self.plot_smoothing_button.setToolTip('somewhat experimental and buggy for now\nsorry')
        self.plot_smoothing_button.clicked.connect(lambda: self.on_plot('plot', 'visualize smoothing'))
        my_grid.addWidget(self.plot_smoothing_button, smoothing_row_number, 4)
        
        #data presentation options line 4- - - - - - - - - - - - - - - - - - - -
        
        zscale_row_number = 3
        
        my_grid.addWidget(QLabel("z scale:"), zscale_row_number, 0)
        
        #z_min input textbox
        self.zmin_choose = QLineEdit()
        self.zmin_choose.setText('native')
        self.zmin_choose.setToolTip('use \'native\' to use min of data file (default)\nor put in any number')
        my_row = QHBoxLayout()        
        my_row.addWidget(QLabel("z null:"))
        my_row.addWidget(self.zmin_choose)
        my_grid.addLayout(my_row, zscale_row_number, 1)
        
        #the offset textbox
        self.offset_choose = QLineEdit()
        self.offset_choose.setText('0')
        self.offset_choose.setToolTip('offset')
        
        #z_max input textbox
        self.zmax_choose = QLineEdit()
        self.zmax_choose.setText('native')
        self.zmax_choose.setToolTip('use \'native\' to use max of data file (default)\nor put in any number')
        my_row = QHBoxLayout()        
        my_row.addWidget(QLabel("z max:"))
        my_row.addWidget(self.zmax_choose)
        my_grid.addLayout(my_row, zscale_row_number, 2)
        
        #the plot-scale combobox
        self.colormap_type = QComboBox()
        colormap_options = ['int',
                            'amp',
                            'log',
                            'raw']
        self.colormap_type.addItems(colormap_options)
        self.colormap_type.setCurrentIndex(3)        
        z_scaling_label = QLabel('z scaling:')
        my_grid.addWidget(z_scaling_label, zscale_row_number, 3)
        my_grid.setAlignment(z_scaling_label, Qt.AlignRight)
        my_grid.addWidget(self.colormap_type, zscale_row_number, 4)
        
        #data presentation options line 5- - - - - - - - - - - - - - - - - - - -

        zpresentation_row_number = 4
        
        my_grid.addWidget(QLabel("z presentation:"), zpresentation_row_number, 0)
        
        #the colorbar toggle
        self.colorbar_toggle = QCheckBox("show colorbar")
        self.colorbar_toggle.setChecked(True)
        my_grid.addWidget(self.colorbar_toggle, zpresentation_row_number, 1)
        my_grid.setAlignment(self.colorbar_toggle, Qt.AlignRight)
        
        #the colorbar type comobobox
        self.colorbar_type = QComboBox()
        colorbar_options = ['default',
                            'skyebar',
                            'greyscale',
                            'greenscale',
                            'signed',
                            'flag',
                            'invisible']
        self.colorbar_type.addItems(colorbar_options)
        self.colorbar_type.setToolTip('alternative colorbars\nthis is somewhat experimental\nuse at your own risk')
        my_row = QHBoxLayout()
        my_row.addWidget(self.colorbar_type)
        
        
        #the colorbar presentation checkbox
        self.colorbar_dynamic_range_toggle = QCheckBox('fill')
        self.colorbar_dynamic_range_toggle.setChecked(False)
        self.colorbar_dynamic_range_toggle.setToolTip('when checked, colorbar will always show all colors\nuseful for signed data, otherwise can be ignored')
        my_row.addWidget(self.colorbar_dynamic_range_toggle)
        my_grid.addLayout(my_row, zpresentation_row_number, 2)
        
        #the contour toggle
        self.contour_toggle = QCheckBox("show contour lines")
        my_grid.addWidget(self.contour_toggle)
        my_grid.setAlignment(self.contour_toggle, Qt.AlignRight)
        
        #the contour number spinbox
        self.contour_number_spinbox = QSpinBox()
        self.contour_number_spinbox.setMinimum(0)
        self.contour_number_spinbox.setSingleStep(1)
        self.contour_number_spinbox.setValue(9)
        self.contour_number_spinbox.setMaximumWidth(35)
        my_row = QHBoxLayout()
        my_row.addWidget(self.contour_number_spinbox)
        
        #the contour linetype control button
        self.contour_linetype_button = QPushButton("line properties")
        self.contour_linetype_button.clicked.connect(lambda: self.linetype_choose_window_show('contour'))
        my_row.addWidget(self.contour_linetype_button)
        my_grid.addLayout(my_row, zpresentation_row_number, 4)
        
        #data presentation options line 5- - - - - - - - - - - - - - - - - - - -

        other_row_number = 5
        
        my_grid.addWidget(QLabel('other:'), other_row_number, 0)

        #the normalization type combobox
        self.ntype_combo = QComboBox()
        ntype_combo_options = ['default',
                               'vertical', 
                               'horizontal']
        self.ntype_combo.addItems(ntype_combo_options)
        self.ntype_combo.setMinimumWidth(40)
        normalize_along_slices_label = QLabel('normalize along slices:')
        my_grid.addWidget(normalize_along_slices_label, other_row_number, 1)
        my_grid.setAlignment(normalize_along_slices_label, Qt.AlignRight)
        my_grid.addWidget(self.ntype_combo, other_row_number, 2)

        #the aspect input spinbox
        self.aspect_choose = QLineEdit()
        self.aspect_choose.setText('0')
        aspect_label = QLabel("aspect (y/x):")
        my_grid.addWidget(aspect_label, other_row_number, 3)
        my_grid.setAlignment(aspect_label, Qt.AlignRight)
        my_grid.addWidget(self.aspect_choose, other_row_number, 4)

        #data presentation QTstuff - - - - - - - - - - - - - - - - - - - - - - -
        
        #set margins to zero
        self.data_presentation_widget.setContentsMargins(0, 0, 0, 0)     
        my_grid.setContentsMargins(0, 0, 0, 0)
        
        #set column widths
        column_width = 500
        my_grid.setColumnMinimumWidth(1, column_width)
        my_grid.setColumnMinimumWidth(2, column_width)
        my_grid.setColumnMinimumWidth(3, column_width)
        my_grid.setColumnMinimumWidth(4, column_width)

        #add into higher level structure
        self.data_presentation_widget.setLayout(my_grid)        
        vbox.addWidget(self.data_presentation_widget) 
        
        #label##################################################################
        
        self.label_widget = QWidget()

        self.verti_size_label = 120        

        my_grid = QGridLayout()        
        
        #data presentation options line 0- - - - - - - - - - - - - - - - - - - -
        
        self.label_hidden = QCheckBox('')
        self.label_hidden.clicked.connect(lambda: self._hide('label'))
         
        label_label = QHBoxLayout()
        for w in [ QLabel("label:  -----------------------------------------------------------------------------------------------------------------------------------------------------------"),
                   self.label_hidden]:
          label_label.addWidget(w)
          label_label.setAlignment(w, Qt.AlignVCenter)
        vbox.addLayout(label_label) 
        
        #label line 1- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        row_number = 0
        
        #load label configuation file
        self.load_label_config = QPushButton('load cfg')
        self.load_label_config.clicked.connect(lambda: self.load_file('labels'))
        my_grid.addWidget(self.load_label_config, row_number, 0)
        
        #label configuration file textbox
        self.label_config_textbox = QLineEdit()
        my_grid.addWidget(self.label_config_textbox, row_number, 1)
        config_filepath = self.ini_handler('config', 'read', 'label', 'cfg filepath')
        if os.path.isfile(config_filepath):
            self.label_config_textbox.setText(config_filepath)
        else: #load data through qfiledialog
            filepath = os.path.join(filepath_of_folder, 'labels') 
            filepath = QFileDialog.getOpenFileName(self,
                                                   'No LABELS file found - please choose one!',
                                                   filepath,
                                                   'LABELS files (*.labels);;All Files (*.*)')
            self.ini_handler('config', 'write', 'label', 'cfg filepath', filepath)
            self.label_config_textbox.setText(filepath)                                     
                                                   
        #label line 2- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        row_number = 1

        #the plot title toggle
        self.title_toggle = QCheckBox("show title")
        self.title_toggle.setChecked(True)
        my_row = QHBoxLayout()
        my_row.addWidget(self.title_toggle)
        my_row.addSpacing(400)

        #the fontsize input textbox
        self.font_size_choose = QLineEdit()
        self.font_size_choose.setText('16')       
        my_row.addWidget(QLabel('fontsize(global):'))
        my_row.addWidget(self.font_size_choose)
        my_grid.addLayout(my_row, row_number, 1)

        #label line 3- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        row_number = 2
     
        #the plot title textbox
        self.plot_title_textbox = QLineEdit()
        self.plot_title_textbox.setText(r'use LaTeX formating')
        my_grid.addWidget(QLabel('title:'), row_number, 0)
        my_grid.addWidget(self.plot_title_textbox, row_number, 1)
        
        #label line 4- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        row_number = 3

        #the xvar title textbox
        self.xvar_title_textbox = QLineEdit()
        self.xvar_title_textbox.setText(r'use LaTeX formating')
        my_grid.addWidget(QLabel('xlabel:'), row_number, 0)
        my_grid.addWidget(self.xvar_title_textbox, row_number, 1)

        #label line 5- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        row_number = 4

        #the yvar title textbox
        self.yvar_title_textbox = QLineEdit()
        self.yvar_title_textbox.setText(r'use LaTeX formating')
        my_grid.addWidget(QLabel('ylabel:'), row_number, 0)
        my_grid.addWidget(self.yvar_title_textbox, row_number, 1)
               
        #label QTstuff - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        #set margins to zero
        self.label_widget.setContentsMargins(0, 0, 0, 0)     
        my_grid.setContentsMargins(0, 0, 0, 0)
        
        #set column widths
        column_width = 20
        my_grid.setColumnMinimumWidth(0, column_width)
        my_grid.setColumnMinimumWidth(1, column_width)

        #add into higher level structure
        self.label_widget.setLayout(my_grid)        
        vbox.addWidget(self.label_widget) 
     
        #plot###################################################################
        
        #plot line 0 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        plot_options_label = QHBoxLayout()
        for w in [ QLabel("plot:  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")]:
          plot_options_label.addWidget(w)
          plot_options_label.setAlignment(w, Qt.AlignVCenter)
        vbox.addLayout(plot_options_label)
        
        #plot line 1 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        my_row = QHBoxLayout()
        
        #the 'animate' push-button
        self.animate_button = QPushButton("animate")
        self.animate_button.clicked.connect(lambda: self.on_animate())
        my_row.addWidget(self.animate_button)
        my_row.addSpacing(400)
        
        #the 'plot' push-button
        self.plot_button = QPushButton("plot")
        self.plot_button.clicked.connect(lambda: self.on_plot('plot', 'default'))
        my_row.addWidget(self.plot_button)
        
        #the 'save' push-button
        self.save_figure_button = QPushButton('save transparent fig')
        self.save_figure_button.clicked.connect(lambda: self.on_plot('save', 'default'))
        my_row.addWidget(self.save_figure_button)
        
        my_row.setAlignment(Qt.AlignVCenter)
        vbox.addLayout(my_row)
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #activate ui
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        
    def _center(self):
        #a function which ensures that the window appears in the center of the screen at startup
        
        screen = QDesktopWidget().screenGeometry() 
        size = self.geometry() 
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def _hide(self,
             element):
                 
        if element == 'normalization options': #--------------------------------
        
            if self.normalization_options_hidden.checkState() == 2: #2=checked
                #shown --> hidden
                self.normalization_options_widget.show()
                self.window_verti_size = self.window_verti_size + self.verti_size_normalization_options
            else:
                #hidden --> shown
                self.normalization_options_widget.hide()
                self.window_verti_size = self.window_verti_size - self.verti_size_normalization_options
                pass

        elif element == 'additional files': #-----------------------------------
        
            if self.additional_files_hidden.checkState() == 2: #2=checked
                #hidden --> shown
                self.additional_files_widget.show()
                self.window_verti_size = self.window_verti_size + self.verti_size_additional_files     
            else:
                #shown --> hidden
                self.additional_files_widget.hide()
                self.window_verti_size = self.window_verti_size - self.verti_size_additional_files
                
        elif element == 'data processing': #------------------------------------
        
            if self.data_processing_hidden.checkState() == 2: #2=checked
                #hidden --> shown
                self.data_processing_widget.show()
                self.window_verti_size = self.window_verti_size + self.verti_size_data_processing
            else:
                #shown --> hidden
                self.data_processing_widget.hide()
                self.window_verti_size = self.window_verti_size - self.verti_size_data_processing   
                
        elif element == 'data presentation': #----------------------------------
        
            if self.data_presentation_hidden.checkState() == 2: #2=checked
                #hidden --> shown
                self.data_presentation_widget.show()
                self.window_verti_size = self.window_verti_size + self.verti_size_data_presentation
            else:
                #shown --> hidden
                self.data_presentation_widget.hide()
                self.window_verti_size = self.window_verti_size - self.verti_size_data_presentation
                
        elif element == 'label': #----------------------------------------------
        
            if self.label_hidden.checkState() == 2: #2=checked
                #hidden --> shown
                self.label_widget.show()
                self.window_verti_size = self.window_verti_size + self.verti_size_label
            else:
                #shown --> hidden
                self.label_widget.hide()
                self.window_verti_size = self.window_verti_size - self.verti_size_label
                
        else: #-----------------------------------------------------------------
            print ' ' 
            print 'element not recognized in hide'                
        
        self.resize(self.window_horiz_size, self.window_verti_size) 
        self.setMinimumSize(self.window_horiz_size, self.window_verti_size)
        self.setMaximumSize(self.window_horiz_size, self.window_verti_size)     

    def on_plot(self,
                save_or_plot,
                plot_type):
                    
        print ' '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'on_plot running'
      
        #what happens when you click the plot button (the important part)
        
        #clear stuff that needs it - - - - - - - - - - - - - - - - - - - - - - -
        
        self.filename_comments = ''
        
        #call dat class- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        #apply fit filetype
        if self.fit_format_comobobox.currentText() == 'old .fit':
            f.fit.old_cols = True
        else:
            f.fit.old_cols = False

        #collect neccessary variables for input into dat class
        filepath_input = unicode(self.dat_filepath_textbox.text())
        if unicode(self.yvar_combo.currentText()) == '1D data':
            scantype_input = '1d'
        else:
            scantype_input = '2d'
        self.xvar_input = self.input_parser(dimension = 'x')
        self.yvar_input = self.input_parser(dimension = 'y')
        self.zvar_input = unicode(self.zvar_combo.currentText())
        grid_factor_input = self.gridfactor_choose.value()
        #.dat cols
        if self.column_combo.currentText() == '.dat format v0':
            cols_input = 'v0'
        elif self.column_combo.currentText() == '.dat format v1':
            cols_input = 'v1'
        elif self.column_combo.currentText() == '.dat format v2':
            cols_input = 'v2'
        else:
            print '  self.column_combo.currentText() not recognized in on_plot!'
        #colortune?
        if self.colortune_toggle.checkState() == 2: #2=checked
            colortune_input = True
        else:
            colortune_input = False

        #create self.instance
        print ' '
        self.instance = f.dat(filepath=filepath_input,
                            scantype=scantype_input,
                            zvar=self.zvar_input,
                            xvar=self.xvar_input,
                            yvar=self.yvar_input, 
                            user_created=True,
                            cols=cols_input,
                            grid_factor=grid_factor_input,
                            colortune=colortune_input)

        #run script if called for- - - - - - - - - - - - - - - - - - - - - - - -
        
        if self.script_toggle.checkState() == 2: #2=checked
            for i in range(self.script_table.rowCount()):
                script_filepath = str(self.script_table.item(i, 0).text())
                print script_filepath
                sys.path.insert(0, script_filepath)
                script_filename = str(os.path.basename(script_filepath))
                extension_script = imp.load_source(script_filename, script_filepath)
                extension_script.run(instance=self.instance)
        else:
            pass
          
        #font size support - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        #must come before plot2d called
        font_size_input = float(self.font_size_choose.text())
        self.instance.font_size = font_size_input
        
        #apply zmin, zmax- - - - - - - - - - - - - - - - - - - - - - - - - - - -
            
        #zmin
        if unicode(self.zmin_choose.text()) == 'native':
            self.instance.znull = self.instance.znull
        else:
            self.instance.znull = float(self.zmin_choose.text())
        #zmax
        if unicode(self.zmax_choose.text()) == 'native':
            pass
        else:
            self.instance.zmax = float(self.zmax_choose.text())
            
        #remove data in the case of plotting a mask- - - - - - - - - - - - - - -

        if plot_type == 'normalization mask':
            for i in range(len(self.instance.zi)):
                for j in range(len(self.instance.zi[0])):
                    self.instance.zi[i] = 1
        else:
            pass                
                
        #normalize data- - - - - - - - - - - - - - - - - - - - - - - - - - - - -      

        self.normalize('default')          

        #apply ntype - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        ntype_input = unicode(self.ntype_combo.currentText())
        if ntype_input == 'default':
            pass
        else:
            self.instance.normalize(ntype_input)
        print 'normalization type =', ntype_input
        
        #smooth data - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
     
        if self.smoothing_toggle.checkState() == 2: #2 = 'checked', 0 = 'unchecked'
            self.smooth()
        else:
            pass
        
        #call plot2d - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
          
        #collect
        #pixelated input toggle
        pixelated_input_state = self.plot_type_combo.currentText()
        if pixelated_input_state == 'interpolate':
            pixelated_input = False
        elif pixelated_input_state == 'plot pixels':
            self.filename_comments = self.filename_comments + ' PIXELATED'
            pixelated_input = True
        #alt_zi
        alt_zi_text = unicode(self.colormap_type.currentText())
        if alt_zi_text == 'raw':
            alt_zi_input = None
        else:
            alt_zi_input = alt_zi_text
        #contour options
        contour_input = self.contour_toggle.checkState()
        self.instance.contour_kwargs['colors']=contour_color
        self.instance.contour_kwargs['linewidths']=float(contour_line_width)
        self.instance.contour_n = int(self.contour_number_spinbox.text())
        
        #control colorbar
        self.define_colorbar()
        
        #dynamic range toggle
        if self.colorbar_dynamic_range_toggle.checkState() == 2: #2=checked
            dynamic_range_input = True
        else:
            dynamic_range_input = False
        
        #aspect
        aspect_input = float(self.aspect_choose.text())
        
        #call
        print ' '
        print 'calling...'
        self.instance.plot2d(alt_zi=alt_zi_input,
                        scantype='2d',
                        contour=contour_input,
                        aspect=aspect_input,
                        pixelated=pixelated_input,
                        dynamic_range=dynamic_range_input)
        print '(self.instance.plot2d call completed)'
                        
        #expectation, max value plotting implementation- - - - - - - - - - - - -
        #must come before sideplot implementation for some reason
        
        #expectation value
        if self.exp_value_show_toggle.checkState() == 2: #2 = checked
          if self.exp_value_dimension_combobox.currentText() == 'none':
              pass
          elif self.exp_value_dimension_combobox.currentText() == 'against x':
              my_values = self.instance.exp_value(axis='x')
              plt.plot(self.instance.xi, my_values,
                       color = exp_color,
                       linewidth = exp_line_width,
                       linestyle = exp_line_style)
          elif self.exp_value_dimension_combobox.currentText() == 'against y':
              my_values = self.instance.exp_value(axis='y')
              plt.plot(my_values, self.instance.yi,
                       color = exp_color,
                       linewidth = exp_line_width,
                       linestyle = exp_line_style)
          else:
              print ' ' 
              print 'exp_value_combobox value not recognized!'
        else:
          pass
      
        #max value
        if self.max_value_show_toggle.checkState() == 2: #2 = checked
          if self.max_value_dimension_combobox.currentText() == 'none':
              pass
          elif self.max_value_dimension_combobox.currentText() == 'against x':
              zi = self.instance.zi.copy()
              yi = self.instance.yi.copy()
              my_values = np.zeros(self.instance.xi.shape)
              for i in range(my_values.shape[0]):
                  temp_zi = zi[:,i]
                  index_of_max = np.argmax(temp_zi)
                  my_values[i] = yi[index_of_max]
                  print self.instance.xi[i], my_values[i]
              plt.plot(self.instance.xi, my_values,
                       color = max_color,
                       linewidth = max_line_width,
                       linestyle = max_line_style)
              
          elif self.max_value_dimension_combobox.currentText() == 'against y':
              zi = self.instance.zi.copy()
              xi = self.instance.xi.copy()
              my_values = np.zeros(self.instance.xi.shape)
              for i in range(my_values.shape[0]):
                  temp_zi = zi[i,:]
                  index_of_max = np.argmax(temp_zi)
                  my_values[i] = xi[index_of_max]
              plt.plot(my_values, self.instance.yi,
                       color = max_color,
                       linewidth = max_line_width,
                       linestyle = max_line_style)
          else:
              print ' ' 
              print 'exp_value_combobox value not recognized!'
        else:
          pass

        #sideplot implementation - - - - - - - - - - - - - - - - - - - - - - - -
        
        #binned data
        if self.xsideplot_toggle.checkState() == 2: #2 = 'checked', 0 = 'unchecked' 
            x_proj_input = True
        else:
            x_proj_input = False
        if self.ysideplot_toggle.checkState() == 2: #2 = 'checked', 0 = 'unchecked' 
            y_proj_input = True
        else:
            y_proj_input = False
        self.instance.side_plot_proj_kwargs['linewidth'] = bin_line_width
        self.instance.side_plot_proj_linetype = bin_color
        
        #abs scans
        #for x axis
        if self.abs_along_x_toggle.checkState() == 2:
          print '  ... along x'
          #get filepath
          filepath_input = str(self.abs_filepath_textbox.text())
          #create NIRscan instance
          x_abs_instance = f.NIRscan()
          #load in file
          x_abs_instance.add(filepath = filepath_input, dataName = 'my_abs_data')
        else:
          x_abs_instance = None
        #for y axis
        if self.abs_along_y_toggle.checkState() == 2:
          print '  ... along y'
          #get filepath
          filepath_input = str(self.abs_filepath_textbox.text())
          #create NIRscan instance
          y_abs_instance = f.NIRscan()
          #load in file
          y_abs_instance.add(filepath = filepath_input, dataName = 'my_abs_data')
        else:
          y_abs_instance = None
        self.instance.side_plot_else_kwargs['linewidth'] = abs_line_width
        self.instance.side_plot_else_linetype = abs_color


        #apply above to create side plots
        self.instance.side_plots(self.instance.s1,
                                 x_proj=x_proj_input,
                                 y_proj=y_proj_input,
                                 x_obj=x_abs_instance,
                                 y_obj=y_abs_instance)

        #control lables/title of plot- - - - - - - - - - - - - - - - - - - - - -
        
        #collect
        xlabel_input_unicode = unicode(self.xvar_title_textbox.text())
        xlabel_input = r'{}'.format(xlabel_input_unicode)
        ylabel_input_unicode = unicode(self.yvar_title_textbox.text())  
        ylabel_input = r'{}'.format(ylabel_input_unicode)  
        title_input = unicode(self.plot_title_textbox.text()) 
        
        #apply
        self.instance.s1.set_xlabel(xlabel_input)
        self.instance.s1.set_ylabel(ylabel_input)
        if self.title_toggle.checkState() == 2: #2 = 'checked', 0 = 'unchecked'
            print ' '
            print 'showing title...'
            self.instance.s1.set_title(title_input)
        else:
            pass
        
        #colorbar toggle - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        if self.colorbar_toggle.checkState() == 2: #2=checked
          self.instance.colorbar()
        else:
          pass
        
        #show or save final plot!- - - - - - - - - - - - - - - - - - - - - - - -
        
        if plot_type == 'default' or plot_type == 'normalization mask':
    
            if save_or_plot == 'plot':
              plt.show()
              print ' ' 
              print 'plot shown!'
              
            elif save_or_plot == 'save':
            
              if self.animating == False:
                  #get filepath through QFileDialog
                  filepath = str(self.dat_filepath_textbox.text())
                  filename = filepath[0:-4]
                  default_filename = str(filename) + str(self.filename_comments) + '.png'
                  filepath = QFileDialog.getSaveFileName(self,
                                                         'save transparent figure', #window title
                                                         default_filename,
                                                         'PNG files (*.png);;All Files (*.*)')
              else:
                  filepath = self.animating_current_save_path
              filepath = str(filepath)
              filepath = filepath.replace('.png', '') #remove the .png, as dan adds it later
              print ' '
              
              if self.animating == True:
                  self.instance.savefig(fname=filepath,
                                        transparent=False)
              else:
                  self.instance.savefig(fname=filepath,
                                        transparent=True)

            elif save_or_plot == 'pass':
                pass
              
            else:
              print ' '
              print 'save_or_plot not recognized in on_plot!'
              
        elif plot_type == 'visualize smoothing':
            
            fontsize_for_vis_smoothing = font_size_input - 7

            #get raw data again and put into seperate instance of fscolors
            filetype_input = str(self.dat_filepath_textbox.text())
            raw_instance = f.dat(filepath=filepath_input,
                                scantype=scantype_input,
                                zvar=self.zvar_input,
                                xvar=self.xvar_input,
                                yvar=self.yvar_input, 
                                user_created=True,
                                cols=cols_input,
                                grid_factor=1,
                                colortune=False)
                                
            #raw_instance.normalize()
                                
            #create figure
            plt.close()
            gs = matplotlib.gridspec.GridSpec(1, 2, height_ratios=(1,1), width_ratios=(1,1))
            
            #add raw data to figure (left hand side)
            x_step = np.abs(raw_instance.xi[1] - raw_instance.xi[0])
            y_step = np.abs(raw_instance.yi[1] - raw_instance.yi[0])
            sp1 = plt.subplot(gs[0,0])
            sp1.imshow(raw_instance.zi, origin='lower', cmap=raw_instance.mycm, 
                             interpolation='nearest', 
                             extent=[raw_instance.xi.min() - x_step/2., 
                                     raw_instance.xi.max() + x_step/2., 
                                     raw_instance.yi.min() - y_step/2., 
                                     raw_instance.yi.max() + y_step/2.])
            sp1.set_title('raw data', fontsize = fontsize_for_vis_smoothing+3)
            sp1.grid()
            
            v = np.array([raw_instance.xi.min(), raw_instance.xi.max(),
                          raw_instance.yi.min(), raw_instance.yi.max()])
            plt.gca().axis(np.around(v))            
            
            sp1.set_xlim([-10, 10])
            sp1.set_autoscaley_on(False)
            sp1.set_autoscalex_on(False)
            plt.yticks(fontsize = fontsize_for_vis_smoothing)
            plt.xticks(rotation = 45, fontsize = fontsize_for_vis_smoothing)        
            
            #add processed data to figure (right hand side)
            sp2 = plt.subplot(gs[0,1], sharex=sp1, sharey=sp1)
            sp2.contourf(self.instance.xi, self.instance.yi, self.instance.zi, 200, cmap=self.instance.mycm)
            sp2.set_title('interpolated, smoothed',fontsize = fontsize_for_vis_smoothing+3)
            sp2.grid()
            plt.yticks(fontsize = fontsize_for_vis_smoothing)
            plt.xticks(rotation = 45, fontsize = fontsize_for_vis_smoothing)
            
            #show plot
            
            plt.show()            
                
        else:
            pass
        
    def on_plot_abs(self):

        filepath = str(self.abs_filepath_textbox.text())

        NIR_instance = f.NIRscan()
        NIR_instance.add(filepath=filepath,
                         dataName=None)
        
        NIR_instance.plot(scantype='default',
                          xtype='wn')
        
        
        
    def on_animate(self):
        
        MainWindow_instance = self.__getattribute__
        
        self.my_dialog = AnimateWindow(MainWindow_instance)      
        self.my_dialog.show()
                
    def normalize(self,
                  normalizetype):
                         
        #startup - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        if normalizetype == 'default':
            pass
        
        elif normalizetype == 'visualize':
            pass
        
        else:
            print 'normalizetype not recognized in on_normalize!'
            
        #.dat cols
        if self.column_combo.currentText() == '.dat format v0':
            cols_input = 'v0'
        elif self.column_combo.currentText() == '.dat format v1':
            cols_input = 'v1'
        elif self.column_combo.currentText() == '.dat format v2':
            cols_input = 'v2'
        else:
            print '  self.column_combo.currentText() not recognized in on_plot!'

        #pyro normalization support- - - - - - - - - - - - - - - - - - - - - - -

        if self.pyro1_norm_toggle.checkState() == 2 or self.pyro2_norm_toggle.checkState() == 2:
            
            print ' '
            print 'normalizing by pyros'
            
            #pyro 1
            if self.pyro1_norm_toggle.checkState() == 2:
                pyro1_channel = str(self.pyro1_zvar_combo.currentText())
                pyro1_power = float(self.pyro1_power_textbox.text())
                pyro1_znull = float(self.pyro1_znull_textbox.text())
                print '  OPA1 by channel {0} to power {1} with znull {2}'.format(pyro1_channel, pyro1_power, pyro1_znull)
                pyro1_data = (self.instance.zvars[pyro1_channel]-pyro1_znull)**pyro1_power
                self.instance.zi = self.instance.zi / pyro1_data
            else:
                pass
            
            #pyro 2
            if self.pyro2_norm_toggle.checkState() == 2:
                pyro2_channel = str(self.pyro2_zvar_combo.currentText())
                pyro2_power = float(self.pyro2_power_textbox.text())
                pyro2_znull = float(self.pyro2_znull_textbox.text())
                print '  OPA1 by channel {0} to power {1} with znull {2}'.format(pyro2_channel, pyro2_power, pyro2_znull)
                pyro2_data = (self.instance.zvars[pyro2_channel]-pyro2_znull)**pyro2_power
                self.instance.zi = self.instance.zi / pyro2_data
            else:
                pass
            
            #reset zmax, zmin
            self.instance.zmax = np.max(self.instance.zi)
            self.instance.znull = np.min(self.instance.zi)
            
        else:
            pass

        #powersmoothness normalization support - - - - - - - - - - - - - - - - -

        if self.opa1ps_norm_toggle.checkState() == 2 or self.opa1ps_norm_toggle.checkState() == 2:
  
            #parse axes
            if self.xvar_input in ('w1', 'l1'):
                x_identity = 'w1'
            elif self.xvar_input in ('w2', 'l2'):
                x_identity = 'w2'
            else:
                x_identity = 'none'
            if self.yvar_input in ('w1', 'l1'):
                y_identity = 'w1'
            elif self.yvar_input in ('w2', 'l2'):
                y_identity = 'w2'
            else:
                y_identity = 'none'
                
            #pull info about OPA p.s. usage from gui
            if self.opa1ps_norm_toggle.checkState() == 2: #2=checked
              use_OPA1 = True
            else:
              use_OPA1 = False
            if self.opa2ps_norm_toggle.checkState() == 2: #2=checked
              use_OPA2 = True
            else:
              use_OPA2 = False
                
            #assign everything
            if self.reverse_opa_roles_toggle.checkState() == 0: #0=unchecked
              #OPA1=w1, OPA2=w2
              #x axis
              if x_identity == 'w1' and use_OPA1 == True:
                  x_file_input = unicode(self.opa1ps_filepath_textbox.text())
                  xnSigVar_input = str(self.opa1_zvar_combo.currentText())
                  xpower_input = float(self.opa1ps_power_textbox.text())
              elif x_identity == 'w2' and use_OPA2 == True:
                  x_file_input = unicode(self.opa2ps_filepath_textbox.text())
                  xnSigVar_input = str(self.opa2_zvar_combo.currentText())
                  xpower_input = float(self.opa2ps_power_textbox.text())
              else:
                  x_file_input = 'trash'
                  xnSigVar_input = 'ai0'
                  xpower_input = None
              #y axis
              if y_identity == 'w1' and use_OPA1 == True:
                  y_file_input = unicode(self.opa1ps_filepath_textbox.text())
                  ynSigVar_input = str(self.opa1_zvar_combo.currentText())
                  ypower_input = float(self.opa1ps_power_textbox.text())
              elif y_identity == 'w2' and use_OPA2 == True:
                  y_file_input = unicode(self.opa2ps_filepath_textbox.text())
                  ynSigVar_input = str(self.opa2_zvar_combo.currentText())
                  ypower_input = float(self.opa2ps_power_textbox.text())
              else:
                  y_file_input = 'trash'
                  ynSigVar_input = 'ai0'
                  ypower_input = None
            elif self.reverse_opa_roles_toggle.checkState() == 2: #2=checked
              #OPA1=w2, OPA2=21
              #x axis
              if x_identity == 'w1' and use_OPA2 == True:
                  x_file_input = unicode(self.opa2ps_filepath_textbox.text())
                  xnSigVar_input = str(self.opa2_zvar_combo.currentText())
                  xpower_input = float(self.opa2ps_power_textbox.text())
              elif x_identity == 'w2' and use_OPA1 == True:
                  x_file_input = unicode(self.opa1ps_filepath_textbox.text())
                  xnSigVar_input = str(self.opa1_zvar_combo.currentText())
                  xpower_input = float(self.opa1ps_power_textbox.text())
              else:
                  x_file_input = 'trash'
                  xnSigVar_input = 'ai0'
                  xpower_input = None
              #y axis
              if y_identity == 'w1' and use_OPA2 == True:
                  y_file_input = unicode(self.opa2ps_filepath_textbox.text())
                  ynSigVar_input = str(self.opa2_zvar_combo.currentText())
                  ypower_input = float(self.opa2ps_power_textbox.text())
              elif y_identity == 'w2' and use_OPA1 == True:
                  y_file_input = unicode(self.opa1ps_filepath_textbox.text())
                  ynSigVar_input = str(self.opa1_zvar_combo.currentText())
                  ypower_input = float(self.opa1ps_power_textbox.text())
              else:
                  y_file_input = 'trash'
                  ynSigVar_input = 'ai0'
                  ypower_input = None
            
            #normalize, scale
            print '  messages from fscolors:'
            self.instance.normalize(ntype = 'b',
                                    x_file = x_file_input,
                                    y_file = y_file_input,
                                    xnSigVar = xnSigVar_input,
                                    ynSigVar = ynSigVar_input,
                                    xpower = xpower_input,
                                    ypower = ypower_input)
                               
        else:
            pass
                           
        #2D mask normalization support - - - - - - - - - - - - - - - - - - - - -

        if self.norm2D_norm_toggle.checkState() == 2:
            
            print ' '
            print 'normalizing by 2D mask'

            #gather variables from ui
            filepath_input = str(self.norm2D_filepath_textbox.text())
            znull_input = float(self.norm2D_znull_textbox.text())
            
            #create fscolors instance of the 2D mask file
            mask_instance = f.dat(filepath=filepath_input,
                                  scantype='2d',
                                  zvar=self.zvar_input,
                                  xvar=self.xvar_input,
                                  yvar=self.yvar_input, 
                                  user_created=True,
                                  cols=cols_input,
                                  grid_factor=1,
                                  znull=znull_input,
                                  colortune=False)
            
            #grid the data onto the main dat file instance                   
            mask_instance._gengrid(xlis=self.instance.xi,
                                   ylis=self.instance.yi)
                                   
            #normalize the mask
            mask_instance.normalize()
                
            #normalize the data with the mask                
            self.instance.zi = ((self.instance.zi - self.instance.znull) / mask_instance.zi) + self.instance.znull

            #reset zmax, zmin
            self.instance.zmax = np.max(self.instance.zi)
            #self.instance.znull = np.min(self.instance.zi)
        
        else:
            pass        
        
        #finish- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        if normalizetype == 'default':
            pass
        
        elif normalizetype == 'visualize':
            pass
        
        else:
            print 'normalizetype not recognized in on_normalize!'
            
    def smooth(self):
        
        #startup - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        #gather inputs
        x_input = self.xsmooth_choose.value()
        y_input = self.ysmooth_choose.value()

        #print startup message
        print ' '
        print 'smoothing data'
        print '  {} along x'.format(x_input)
        print '  {} along y'.format(y_input)
        print '  this may take a while...'
        
        #smoothing support - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        self.instance.smooth(x=x_input, y=y_input)
        
        #apply zmin, zmax again- - - - - - - - - - - - - - - - - - - - - - - - -
            
        #zmin
        if unicode(self.zmin_choose.text()) == 'native':
            self.instance.zmin = self.instance.zmin + float(self.offset_choose.text())
        else:
            self.instance.zmin = float(self.zmin_choose.text()) + float(self.offset_choose.text())
        #zmax
        if unicode(self.zmax_choose.text()) == 'native':
            pass
        else:
            self.instance.zmax = float(self.zmax_choose.text())
            
        #finish- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        
        self.filename_comments = self.filename_comments + ' SMOOTHED'
        print '  done smoothing!'

          
    def on_save(self,
                savetype):    
        print ' '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'on_save running'
        print ' '
        print 'savetype =', savetype
        
        #get everyting ready - - - - - - - - - - - - - - - - - - - - - - - - - -
                  
        #collect neccessary variables for input into dat class
        filepath_input = unicode(self.dat_filepath_textbox.text())
        if unicode(self.yvar_combo.currentText()) == '1D data':
            scantype_input = '1d'
        else:
            scantype_input = '2d'
        self.xvar_input = self.input_parser(dimension = 'x')
        self.yvar_input = self.input_parser(dimension = 'y')
        self.zvar_input = unicode(self.zvar_combo.currentText())
        column_combo_state = unicode(self.column_combo.currentText())
        grid_factor_input = self.gridfactor_choose.value()
        #.dat cols
        if self.column_combo.currentText() == '.dat format v0':
            cols_input = 'v0'
        elif self.column_combo.currentText() == '.dat format v1':
            cols_input = 'v1'
        elif self.column_combo.currentText() == '.dat format v2':
            cols_input = 'v2'
        else:
            print '  self.column_combo.currentText() not recognized in on_save!'

        #create self.instance
        print ' '
        self.instance = f.dat(filepath=filepath_input,
                              scantype=scantype_input,
                              zvar=self.zvar_input,
                              xvar=self.xvar_input,
                              yvar=self.yvar_input, 
                              user_created=True, 
                              cols=cols_input,
                              grid_factor=grid_factor_input)
                 
        #save- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            
        if savetype == 'exp_value .fit' or 'max_value .fit':
            
          #get filepath through QFileDialog
          filepath = unicode(self.dat_filepath_textbox.text())
          filepath = filepath[0:-4] #remove .dat extension
          filepath = QFileDialog.getSaveFileName(self,
                                                 'save .fit file', #window title
                                                 filepath,
                                                 'FIT files (*.fit);;All Files (*.*)')
          #get center type
          if savetype == 'exp_value .fit':
              center = 'exp_val'
          elif savetype == 'max_value .fit':
              center = 'max'
          else:
              print 'something went wrong...'
              return
          print center
          #get dimension from UI
          if center == 'exp_val':
              if self.exp_value_dimension_combobox.currentText() == 'none':
                  print 'you must choose a dimension before saving a .fit file!'
                  return
              elif self.exp_value_dimension_combobox.currentText() == 'against x':
                  dimension_input = 'x'
              elif self.exp_value_dimension_combobox.currentText() == 'against y':
                  dimension_input = 'y'
              else:
                  print ' ' 
                  print 'exp_value_combobox value not recognized!'
          elif center == 'max':
              print 'max logic'
              if self.max_value_dimension_combobox.currentText() == 'none':
                  print 'you must choose a dimension before saving a .fit file!'
                  return
              elif self.max_value_dimension_combobox.currentText() == 'against x':
                  dimension_input = 'x'
              elif self.max_value_dimension_combobox.currentText() == 'against y':
                  dimension_input = 'y'
              else:
                  print ' ' 
                  print 'exp_value_combobox value not recognized!'
          else:
              return
          #apply fit filetype
          if self.fit_format_comobobox.currentText() == 'old .fit':
              f.fit.old_cols = True
          else:
              f.fit.old_cols = False
          #get amplitude type
          if self.amp_type_comobobox.currentText() == 'by binning':
              amp_input = 'int'
          elif self.amp_type_comobobox.currentText() == 'by max value':
              amp_input = 'max'
          #print some stuff
          print ' '
          print 'taking expectation value against {} and creating .fit file'.format(dimension_input)
          #call make_tune, let it do the rest                  
          f.make_tune(obj = self.instance,
                      set_var = dimension_input, 
                      amp = amp_input,
                      center = center,
                      fname = str(filepath))
        
        else:
          print ' '
          print 'on_save called, but savetype not recognized!'
          return
    
    def input_parser(self,
                     dimension):
                         
        #startup - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        print ' '
        print 'input_parser running'
        print '  for', dimension
                       
        #get info from ui- - - - - - - - - - - - - - - - - - - - - - - - - - - -
                       
        if dimension == 'x':
            dimension_combobox_text = unicode(self.xvar_combo.currentText())
        elif dimension == 'y':
            dimension_combobox_text = unicode(self.yvar_combo.currentText())
        else:
            print 'dimension not recognized in input_parser'
            return
        
        #decide on input to give fscolors- - - - - - - - - - - - - - - - - - - -
      
        if self.color_units_combo.currentText() == 'wn':
            if 'w1' in dimension_combobox_text:
                var_input = 'w1'
            elif 'w2' in dimension_combobox_text:
                var_input = 'w2'
            elif 'wm' in dimension_combobox_text:
                var_input = 'wm'
            elif 'd1' in dimension_combobox_text:
                var_input = 'd1'
            elif 'd2' in dimension_combobox_text:
                var_input = 'd2'
            else:
                print '  input_parser can\'t decide!'
                return
        elif self.color_units_combo.currentText() == 'nm':
            if 'w1' in dimension_combobox_text:
                var_input = 'l1'
            elif 'w2' in dimension_combobox_text:
                var_input = 'l2'
            elif 'wm' in dimension_combobox_text:
                var_input = 'lm'
            elif 'd1' in dimension_combobox_text:
                var_input = 'd1'
            elif 'd2' in dimension_combobox_text:
                var_input = 'd2'
            else:
                print '  input_parser can\'t decide!'
                return
        else:
            print '  color_units_combo value not recognized in units_parser'
            return
        
        #return input to calling function- - - - - - - - - - - - - - - - - - - -
        
        print '  var input to fscolors =', var_input
        return var_input

        
    def gui_handler(self,
                    because_of = None):
        
        #to control gui changes

        if because_of == None:
            
            pass
              
        elif because_of == 'loading dat file':
          
          self.loading_dat_file_now = True
              
          self.datfile_info_extract('data file')
          
          self.loading_dat_file_now = False
          self.gui_handler('change to dimension comboboxes')          
        
        elif because_of == 'change to dimension comboboxes':
          
          if self.loading_dat_file_now == True:
            pass
          else:
            energies = ['w1','w2', 'wm', 'l1', 'l2', 'lm']
            #for x dimension
            x_dimension = self.input_parser('x')
            if x_dimension in energies:
              if self.abs_data_loaded == True:
                  self.abs_along_x_toggle.setDisabled(False)
              else:
                  pass
              self.abs_along_x_toggle.setToolTip('')
            else:
              self.abs_along_x_toggle.setChecked(False)
              self.abs_along_x_toggle.setDisabled(True)
              self.abs_along_x_toggle.setToolTip('cannot plot absorption data against a non-energy axis')
            #for y dimension
            y_dimension = self.input_parser('y')
            if y_dimension in energies:
              if self.abs_data_loaded == True:
                  self.abs_along_y_toggle.setDisabled(False)
              else:
                  pass
              self.abs_along_y_toggle.setToolTip('')
            else:
              self.abs_along_y_toggle.setChecked(False)
              self.abs_along_y_toggle.setDisabled(True)
              self.abs_along_y_toggle.setToolTip('cannot plot absorption data against a non-energy axis')
            
            #autofill labels
            self.label_autofill('x_axis')
            self.label_autofill('y_axis')
            self.label_autofill('title')
            
        elif because_of == 'max value combobox changed':
            
            if self.main_data_loaded == True:
                if self.max_value_dimension_combobox.currentText() == 'none':
                    self.max_value_show_toggle.setChecked(False)
                    self.max_value_show_toggle.setDisabled(True)
                    self.save_max_fit_file_button.setDisabled(True)
                else:
                    self.max_value_show_toggle.setChecked(True)
                    self.max_value_show_toggle.setDisabled(False)
                    self.save_max_fit_file_button.setDisabled(False)
            else:
                if self.max_value_dimension_combobox.currentText() == 'none':
                    self.max_value_show_toggle.setChecked(False)
                    self.max_value_show_toggle.setDisabled(True)
                    self.save_max_fit_file_button.setDisabled(True)
                else:
                    self.max_value_show_toggle.setChecked(True)
                    self.max_value_show_toggle.setDisabled(False)
                    self.save_max_fit_file_button.setDisabled(True)
        
        elif because_of == 'exp value combobox changed':

            if self.main_data_loaded == True:
                if self.exp_value_dimension_combobox.currentText() == 'none':
                    self.exp_value_show_toggle.setChecked(False)
                    self.exp_value_show_toggle.setDisabled(True)
                    self.save_fit_file_button.setDisabled(True)
                else:
                    self.exp_value_show_toggle.setChecked(True)
                    self.exp_value_show_toggle.setDisabled(False)
                    self.save_fit_file_button.setDisabled(False)
            else:
                if self.exp_value_dimension_combobox.currentText() == 'none':
                    self.exp_value_show_toggle.setChecked(False)
                    self.exp_value_show_toggle.setDisabled(True)
                    self.save_fit_file_button.setDisabled(True)
                else:
                    self.exp_value_show_toggle.setChecked(True)
                    self.exp_value_show_toggle.setDisabled(False)
                    self.save_fit_file_button.setDisabled(True)
            
        elif because_of == 'smoothing toggle changed':
            
            pass
        
        elif because_of == 'clear extensions':
        
            self.script_table.removeRow(self.script_table.currentRow())

        else:
          
          print ' '
          print 'because_of not recognized in gui_handler!'
          return
        
    def load_file(self,
                  file_type):
                
        print ' '            
        
        if file_type == 'main .dat file': #- - - - - - - - - - - - - - - - - - -
        
          print 'loading data file'
          
          if self.animating == False:
              #load data through qfiledialog
              filepath = str(self.dat_filepath_textbox.text())
              filepath = QFileDialog.getOpenFileName(self,
                                                     'Open a data file',
                                                     filepath,
                                                     'DAT files (*.dat);;All Files (*.*)')
          else:
              filepath = str(self.dat_filepath_textbox.text())
          #accomplish some ui changes
          if os.path.isfile(filepath):
              self.dat_filepath_textbox.setText(filepath)
              self.gui_handler('loading dat file')
              self.main_data_loaded = True           
          else:
              self.dat_filepath_textbox.setText('raw filepath')
              self.main_data_loaded = False
          self.gui_handler('exp value combobox changed')
          self.gui_handler('max value combobox changed') 
          
        elif file_type == 'OPA1 norm': # - - - - - - - - - - - - - - - - - - - -
        
          print 'loading normalization data for OPA1'
          #load data through qfiledialog
          filepath = str(self.opa1ps_filepath_textbox.text())
          filepath = QFileDialog.getOpenFileName(self,
                                                 'Open a data file',
                                                 filepath,
                                                 'FIT files (*.fit);;DAT files (*.dat);;All Files (*.*)')
          #accomplish some ui changes
          if os.path.isfile(filepath):
              self.opa1ps_norm_toggle.setDisabled(False)
              self.opa1ps_norm_toggle.setChecked(True)
              self.opa1ps_filepath_textbox.setText(filepath)
          else:
              self.opa1ps_norm_toggle.setDisabled(True)
              self.opa1ps_norm_toggle.setChecked(False)
              self.opa1ps_filepath_textbox.setText('raw filepath')
          
        elif file_type == 'OPA2 norm': # - - - - - - - - - - - - - - - - - - - -
        
          print 'loading normalization data for OPA2'
          #load data through qfiledialog
          filepath = str(self.opa2ps_filepath_textbox.text())
          filepath = QFileDialog.getOpenFileName(self,
                                                 'Open a data file',
                                                 filepath,
                                                 'FIT files (*.fit);;DAT files (*.dat);;All Files (*.*)')
          #accomplish some ui changes
          if os.path.isfile(filepath):
              self.opa2ps_norm_toggle.setDisabled(False)
              self.opa2ps_norm_toggle.setChecked(True)
              self.opa2ps_filepath_textbox.setText(filepath)
          else:
              self.opa2ps_norm_toggle.setDisabled(True)
              self.opa2ps_norm_toggle.setChecked(False)
              self.opa2ps_filepath_textbox.setText('raw filepath')

        elif file_type == 'norm2D': #- - - - - - - - - - - - - - - - - - - - - -
            
          print 'loading 2D normalization file'
          #load data through qfiledialog
          filepath = str(self.norm2D_filepath_textbox.text())
          filepath = QFileDialog.getOpenFileName(self,
                                                 'Open a data file',
                                                 filepath,
                                                 'DAT files (*.dat);;All Files (*.*)')
          #accomplish some ui changes
          if os.path.isfile(filepath):
              self.norm2D_norm_toggle.setDisabled(False)
              self.norm2D_norm_toggle.setChecked(True)
              self.norm2D_filepath_textbox.setText(filepath)
              self.datfile_info_extract('norm2D file')
          else:
              self.norm2D_norm_toggle.setDisabled(True)
              self.norm2D_norm_toggle.setChecked(False)
              self.norm2D_filepath_textbox.setText('raw filepath')
              
        elif file_type == 'jasco abs': # - - - - - - - - - - - - - - - - - - - -
        
          print 'loading absorbance data from jasco UV-VIS-NIR'
          #load data through qfiledialog
          filepath = str(self.abs_filepath_textbox.text())
          filepath = QFileDialog.getOpenFileName(self,
                                                 'Open a Jasco absorbance data file',
                                                 filepath,
                                                 'TXT files (*.txt);;All Files (*.*)')
          #accomplish some ui changes
          if os.path.isfile(filepath):
              self.abs_filepath_textbox.setText(filepath)
              self.abs_data_loaded = True
              self.gui_handler('change to dimension comboboxes')
          else:
              self.dat_filepath_textbox.setText('raw filepath')
              self.abs_data_loaded = False
              
        elif file_type == 'script': #- - - - - - - - - - - - - - - - - - - - - -
            
          print 'loading extension script'
          #use folder chosen if filled out, otherwise use default folder
          if self.script_table.rowCount() > 0:
              last_row = self.script_table.rowCount() - 1
              print last_row
              print self.script_table.item(last_row, 0).text()
              filepath = str(self.script_table.item(last_row, 0).text())
              if os.path.isfile(filepath):
                  pass
              else:
                  filepath = os.path.join(filepath_of_folder, 'extensions') 
          else:
              filepath = os.path.join(filepath_of_folder, 'extensions') 
          #load data through qfiledialog
          filepath = QFileDialog.getOpenFileName(self,
                                                 'Open a datplot extension script',
                                                 filepath,
                                                 'PY files (*.py);;All Files (*.*)')
          #accomplish some ui changes               
          if os.path.isfile(filepath):
              self.script_toggle.setDisabled(False)
              self.script_toggle.setChecked(True)
              current_row = self.script_table.rowCount()
              self.script_table.insertRow(current_row)
              cell = QTableWidgetItem()
              cell.setText(filepath)
              #cell.setData(Qt.AlignJustify, Qt.TextAlignmentRole) #this doesn't break it, but it also doesn't fix it
              self.script_table.setItem(0, current_row, cell)
          else:
              print '  sorry - no file found!'
          #force script_table to look good
          self.script_table.horizontalHeader().hide()
          self.script_table.horizontalHeader().setStretchLastSection(True)
          self.script_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
          self.script_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
          for i in range(self.script_table.rowCount()):
              self.script_table.setRowHeight(i, 20)
             
              
        elif file_type == 'labels': #- - - - - - - - - - - - - - - - - - - - - -
        
          print 'loading labels configuration file'
          filepath = os.path.join(filepath_of_folder, 'labels') 
          #load data through qfiledialog
          filepath = QFileDialog.getOpenFileName(self,
                                                 'Open a labels configuration file',
                                                 filepath,
                                                 'LABELS files (*.labels);;All Files (*.*)')
          if os.path.isfile(filepath):
              self.label_config_textbox.setText(filepath)
              self.ini_handler('config', 'write', 'label', 'cfg filepath', filepath)
              self.label_autofill('x_axis')
              self.label_autofill('y_axis')
              self.label_autofill('title')
          else:
              print '  sorry - no file found!'
              self.label_config_textbox.setText('raw filepath')

        else: #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
          print ' '
          print 'file_type not recognized in load_file!'
          return
          
        #filepath must yield file
        if os.path.isfile(filepath):
          print ' '
          print 'file loaded!'
        else:
          print 'filepath',filepath,'does not yield a file'
          return
          
    def datfile_info_extract(self,
                             file_identity):
        
        #startup - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        print 'datfile_info_extract running'
        print '  file_identity =', file_identity

        #import data from file - - - - - - - - - - - - - - - - - - - - - - - - -

        if file_identity == 'data file':            
            filepath = self.dat_filepath_textbox.text()
        elif file_identity == 'norm2D file':
            filepath = self.norm2D_filepath_textbox.text()
        elif file_identity == 'column_combo change':
            if currently_running == True:
                pass
            else:
                self.datfile_info_extract('data file')
        else:
            print ' '
            print 'file_identity not recognized in datfile_info_extract'
            return
        filepath = str(filepath)
        rawDat = np.genfromtxt(filepath, dtype=np.float)
        self.data = rawDat.T #transpose data

        #begin - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -        
        
        currently_running = True
        
        #auto-update dat filetype- - - - - - - - - - - - - - - - - - - - - - - -
        #based on how many columns there are in the array
        
        if len(self.data) == 28:
            print '  .dat file format v2 recognized'
            self.column_combo.setCurrentIndex(0)
        elif len(self.data) == 18:
            print '  .dat file format v1 recognized'
            self.column_combo.setCurrentIndex(1)
        elif len(self.data) == 16:
            print '  .dat file format v0 recognized'
            self.column_combo.setCurrentIndex(2)
        else:
            print '  .dat file format not recognized!'
            
        #import things from ui, fscolors - - - - - - - - - - - - - - - - - - - -

        w1_col        = self.cols('.dat', 'w1')
        w2_col        = self.cols('.dat', 'w2')
        wm_col        = self.cols('.dat', 'wm')   
        d1_col        = self.cols('.dat', 'd1')   
        d2_col        = self.cols('.dat', 'd2')
        zcol          = self.cols('.dat', 'data')
        pyro1_channel = self.cols('.dat', 'pyro1')
        pyro2_channel = self.cols('.dat', 'pyro2')
            
        #set zmin, zmax- - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        
        #get values from data
        data_min = np.min(self.data[zcol])
        data_max = np.max(self.data[zcol])
                    
        #update tooltips
        if file_identity == 'data file':
            self.zmin_choose.setToolTip('native zmin for .dat file currently loaded = {}\nalternatively you may type the string \'native\''.format(data_min))
            self.zmax_choose.setToolTip('native zmax for .dat file currently loaded = {}\nalternatively you may type the string \'native\''.format(data_max))
            #for pyros as well...
            pyro1_min = np.min(self.data[pyro1_channel])
            pyro1_max = np.max(self.data[pyro1_channel])
            self.pyro1_znull_textbox.setToolTip('for currently loaded file:\n  zmin = {0}\n  zmax = {1}'.format(pyro1_min, pyro1_max))
            pyro2_min = np.min(self.data[pyro2_channel])
            pyro2_max = np.max(self.data[pyro2_channel])
            self.pyro2_znull_textbox.setToolTip('for currently loaded file:\n  zmin = {0}\n  zmax = {1}'.format(pyro2_min, pyro2_max))
            
        elif file_identity == 'norm2D file':
            self.norm2D_znull_textbox.setToolTip('for currently loaded file:\n  zmin = {0}\n  zmax = {1}'.format(data_min, data_max))
        else:
            pass

        #discover dimensions - - - - - - - - - - - - - - - - - - - - - - - - - -
        #only for data file...

        if file_identity == 'data file':
            scan_dimensions, dimensions_equal = self.discover_dimensions(filepath)
        else:
            pass
        
        self.dimensions_equal = dimensions_equal
        
        #set comboboxes- - - - - - - - - - - - - - - - - - - - - - - - - - -
     
        #x dimension = scan_dimensions[0]
        print '  setting xvar to', scan_dimensions[0]
        if scan_dimensions[0] == 'w1':
            self.xvar_combo.setCurrentIndex(1)
        elif scan_dimensions[0] == 'w2':
            self.xvar_combo.setCurrentIndex(2)
        elif scan_dimensions[0] == 'wm':
            self.xvar_combo.setCurrentIndex(3)
        elif scan_dimensions[0] == 'w1=w2':
            self.xvar_combo.setCurrentIndex(4)
        elif scan_dimensions[0] == 'w1=wm':
            self.xvar_combo.setCurrentIndex(5)
        elif scan_dimensions[0] == 'w2=wm':
            self.xvar_combo.setCurrentIndex(6)
        elif scan_dimensions[0] == 'w1=w2=wm':
            self.xvar_combo.setCurrentIndex(7)
        elif scan_dimensions[0] == 'd1':
            self.xvar_combo.setCurrentIndex(8)
        elif scan_dimensions[0] == 'd2':
            self.xvar_combo.setCurrentIndex(9)
        elif scan_dimensions[0] == 'd1=d2':
            self.xvar_combo.setCurrentIndex(10)
        else:
            print '  x scan dimension not recognized!'
            
        #y dimension = scan_dimensions[1]
        print '  setting yvar to', scan_dimensions[1]    
        if scan_dimensions[1] == 'w1':
            self.yvar_combo.setCurrentIndex(1)
        elif scan_dimensions[1] == 'w2':
            self.yvar_combo.setCurrentIndex(2)
        elif scan_dimensions[1] == 'wm':
            self.yvar_combo.setCurrentIndex(3)
        elif scan_dimensions[1] == 'w1=w2':
            self.yvar_combo.setCurrentIndex(4)
        elif scan_dimensions[1] == 'w1=wm':
            self.yvar_combo.setCurrentIndex(5)
        elif scan_dimensions[1] == 'w2=wm':
            self.yvar_combo.setCurrentIndex(6)
        elif scan_dimensions[1] == 'w1=w2=wm':
            self.yvar_combo.setCurrentIndex(7)
        elif scan_dimensions[1] == 'd1':
            self.yvar_combo.setCurrentIndex(8)
        elif scan_dimensions[1] == 'd2':
            self.yvar_combo.setCurrentIndex(9)
        elif scan_dimensions[1] == 'd1=d2':
            self.yvar_combo.setCurrentIndex(10)
        else:
            print '  y scan dimension not recognized!'  
            
        #set labels- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            
        self.label_autofill('x axis')
        self.label_autofill('y axis')
        self.label_autofill('title')

        #finish- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        currently_running = False
        
    def discover_dimensions(self,
                            filepath):
                                
        print filepath
                                 
        #import things from ui, fscolors - - - - - - - - - - - - - - - - - - - - 
        
        w1_col        = self.cols('.dat', 'w1')
        w2_col        = self.cols('.dat', 'w2')
        w3_col        = self.cols('.dat', 'w3')
        wm_col        = self.cols('.dat', 'wm')   
        d1_col        = self.cols('.dat', 'd1')   
        d2_col        = self.cols('.dat', 'd2')
        zcol          = self.cols('.dat', 'data')
        pyro1_channel = self.cols('.dat', 'pyro1')
        pyro2_channel = self.cols('.dat', 'pyro2')
                               
        filepath = str(filepath)
        
        #re-import data- - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        rawDat = np.genfromtxt(filepath, dtype=np.float)  
        self.data = rawDat.T #transpose data
        
        #special cases...  - - - - - - - - - - - - - - - - - - - - - - - - - - -

        #colortune files
        if 'Pts Test' in filepath or 'Ints Test'  in filepath:
          #exp_value_dimension_combobox
          self.exp_value_dimension_combobox.setCurrentIndex(1)
          #color_units_combobox
          if self.last_file_was_colortune == True:
              pass #bandaid to allow for use of wavenumbers if the user desires
          else:
              self.color_units_combo.setCurrentIndex(1)
          #general stuff
          self.last_file_was_colortune = True
          self.colortune_toggle.setChecked(True)
          #self.plot_type_combo.setCurrentIndex(1)
          print '  found text implying Colortune in filename...'
          #set title
          if 'OPA1' in filepath:
              print '  ... for OPA1'
              self.plot_title_textbox.setText('OPA1 colortune')
              if self.reverse_opa_roles_toggle.checkState() == 2:
                  self.xvar_combo.setCurrentIndex(2)
              else:
                  self.xvar_combo.setCurrentIndex(1)
              self.yvar_combo.setCurrentIndex(3)
              self.xvar_title_textbox.setText(r'$\mathrm{\bar\nu_{OPA_1} \left(cm^{-1}\right)}$')
              self.yvar_title_textbox.setText(r'$\mathrm{\bar\nu_m-\bar\nu_{OPA_1} \left(cm^{-1}\right)}$')
          elif 'OPA2' in filepath:
              print '  ... for OPA2'
              self.plot_title_textbox.setText('OPA2 colortune')
              if self.reverse_opa_roles_toggle.checkState() == 2:
                  self.xvar_combo.setCurrentIndex(1)
              else:
                  self.xvar_combo.setCurrentIndex(2)
              self.yvar_combo.setCurrentIndex(3)
              self.xvar_title_textbox.setText(r'$\mathrm{\bar\nu_{OPA_2} \left(cm^{-1}\right)}$')
              self.yvar_title_textbox.setText(r'$\mathrm{\bar\nu_m-\bar\nu_{OPA_2} \left(cm^{-1}\right)}$')
          elif 'OPA3' in filepath:
              print '  ... for OPA3'
              self.plot_title_textbox.setText('OPA3 colortune')
              if self.reverse_opa_roles_toggle.checkState() == 2:
                  self.xvar_combo.setCurrentIndex(1)
              else:
                  self.xvar_combo.setCurrentIndex(2)
              self.yvar_combo.setCurrentIndex(3)
              self.xvar_title_textbox.setText(r'$\mathrm{\bar\nu_{OPA_3} \left(cm^{-1}\right)}$')
              self.yvar_title_textbox.setText(r'$\mathrm{\bar\nu_m-\bar\nu_{OPA_3} \left(cm^{-1}\right)}$')
          else:
              print '  ... for unknown OPA... no guesses applied'
          return #exit the function
        elif self.last_file_was_colortune == True: #only called if current file is NOT a colortune file
          self.colortune_toggle.setChecked(False)
          #exp_value_dimension_combobox
          self.exp_value_dimension_combobox.setCurrentIndex(0)
          #color_units_combobox
          self.color_units_combo.setCurrentIndex(0)
          #self.plot_type_combo.setCurrentIndex(0)
          self.last_file_was_colortune = False
        else:
            pass
        
        #all other files...

        #define constants, reset to defaults
        self.dimension_cols = [w1_col, w2_col, wm_col, d1_col, d2_col]
        self.dimension_identity = ['static', 'static', 'static', 'static', 'static']
        
        #find which dimensions are scanned
        for i in range(len(self.dimension_cols)):
            if np.var(self.data[self.dimension_cols[i]]) < 1:
                pass
            else:
                self.dimension_identity[i] = 'scanned'
                
        #print what was found
        print '  w1', self.dimension_identity[0]
        print '  w2', self.dimension_identity[1]
        print '  wm', self.dimension_identity[2]
        print '  d1', self.dimension_identity[3]
        print '  d2', self.dimension_identity[4]

        #initiate dimensions_equal as all true        
        dimensions_equal = np.zeros((len(self.dimension_cols), len(self.dimension_cols)), dtype=bool)
        for i in range(len(dimensions_equal)):
            for j in range(len(dimensions_equal[0])):
                dimensions_equal[i, j] = True
        
        #check if dimensions are scanned together
        within = 2 #native units
        for i in range(len(self.dimension_cols)):
            for j in range(len(self.dimension_cols)):
                for k in range(len(self.data[0])):
                    upper_bound = self.data[self.dimension_cols[j], k] + within
                    lower_bound = self.data[self.dimension_cols[j], k] - within
                    test_point = self.data[self.dimension_cols[i], k] 
                    if upper_bound > test_point > lower_bound:
                        pass
                    else:
                        dimensions_equal[i, j] = False
                        
        scan_dimensions = ['none', 'none', 'none', 'none', 'none']
        current_dimension = 0
        
        #w1
        if self.dimension_identity[0] == 'scanned': #w1 scanned
            if dimensions_equal[0, 1] == True and dimensions_equal[0, 2] == True: #w1=w2=wm
                scan_dimensions[current_dimension] = 'w1=w2=wm'
                self.dimension_identity[1] = 'scanned with w1'
                self.dimension_identity[2] = 'scanned with w1'
                current_dimension = current_dimension + 1
            elif dimensions_equal[0, 1] == True and dimensions_equal[0, 2] == False: #w1=w2
                scan_dimensions[current_dimension] = 'w1=w2'
                self.dimension_identity[1] = 'scanned with w1'
                current_dimension = current_dimension + 1     
            elif dimensions_equal[0, 1] == False and dimensions_equal[0, 2] == True: #w1=wm
                scan_dimensions[current_dimension] = 'w1=wm'
                self.dimension_identity[2] = 'scanned with w1'
                current_dimension = current_dimension + 1
            else: #w1 alone
                scan_dimensions[current_dimension] = 'w1'
                current_dimension = current_dimension + 1
        else:
            pass      
        #w2           
        if self.dimension_identity[1] == 'scanned': #w2 scanned
            if dimensions_equal[1, 2] == True: #w2=wm
                scan_dimensions[current_dimension] = 'w2=wm'
                self.dimension_identity[2] = 'scanned with w1'
                current_dimension = current_dimension + 1
            else:
                scan_dimensions[current_dimension] = 'w2'
                current_dimension = current_dimension + 1
        else:
            pass
        #wm
        if self.dimension_identity[2] == 'scanned': #wm scanned alone
            scan_dimensions[current_dimension] = 'wm'
            current_dimension = current_dimension + 1
        else:
            pass
        #d1
        if self.dimension_identity[3] == 'scanned': #d1 scanned
            if dimensions_equal[3, 4] == True: #d1=d2
                scan_dimensions[current_dimension] = 'd1=d2'
                self.dimension_identity[4] = 'scanned with d1'
                current_dimension = current_dimension + 1
            else: #d1 alone
                scan_dimensions[current_dimension] = 'd1'
                current_dimension = current_dimension + 1
        else:
            pass
        #d2
        if self.dimension_identity[4] == 'scanned': #d2 scanned alone
            scan_dimensions[current_dimension] = 'd2'
            current_dimension = current_dimension + 1
        else:
            pass
        
        #discover dimension averages- - - - - - - - - - - - - - - -  - - - - - -
        
        global dimension_average
        dimension_average = np.zeros(len(self.dimension_identity))        

        #w1
        if self.color_units_combo.currentText() == 'wn':
            dimension_average[0] = np.average(1e7/(self.data[w1_col]))
        elif self.color_units_combo.currentText == 'nm':
            dimension_average[0] = np.average(self.data[w1_col])
        else:
            print '  color_units_combo currentText not recognized in discover_dimensions!'
        #w2
        if self.color_units_combo.currentText() == 'wn':
            dimension_average[1] = np.average(1e7/(self.data[w2_col]))
        elif self.color_units_combo.currentText == 'nm':
            dimension_average[1] = np.average(self.data[w2_col])
        else:
            print '  color_units_combo currentText not recognized in discover_dimensions!'
        #wm
        if self.color_units_combo.currentText() == 'wn':
            dimension_average[2] = np.average(1e7/(self.data[wm_col]))
        elif self.color_units_combo.currentText == 'nm':
            dimension_average[2] = np.average(self.data[wm_col])
        else:
            print '  color_units_combo currentText not recognized in discover_dimensions!'
        #d1
        dimension_average[3] = np.average(self.data[d1_col])
        #d2
        dimension_average[4] = np.average(self.data[d2_col])

        #finish- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -        
  
        global dimension_identity
        dimension_identity = self.dimension_identity
        
        return scan_dimensions, dimensions_equal
 
    def label_autofill(self,
                       which_label):
    
        #fills lablels based on assignments made in .labels config file
        
        #startup----------------------------------------------------------------
        
        print ' ' 
        print 'label_autofill running'

        #import things from ui, fscolors----------------------------------------

        w1_col        = self.cols('.dat', 'w1')
        w2_col        = self.cols('.dat', 'w2')
        wm_col        = self.cols('.dat', 'wm')   
        d1_col        = self.cols('.dat', 'd1')   
        d2_col        = self.cols('.dat', 'd2')
        zcol          = self.cols('.dat', 'data')
        pyro1_channel = self.cols('.dat', 'pyro1')
        pyro2_channel = self.cols('.dat', 'pyro2')
   
        #import strings from .labels config file--------------------------------

        #general symbols
        between_dimensions = self.ini_handler('labels', 'read', 'other', 'symbol between dimensions')
        before_value = self.ini_handler('labels', 'read', 'other', 'symbol before value')
        left_bracket = self.ini_handler('labels', 'read', 'other', 'left bracket')
        right_bracket = self.ini_handler('labels', 'read', 'other', 'right bracket')
   
        #units
        units_wn = self.ini_handler('labels', 'read', 'colors (wn)', 'units')
        p_units_wn = left_bracket + units_wn + right_bracket
        units_nm = self.ini_handler('labels', 'read', 'colors (nm)', 'units')
        p_units_nm = left_bracket + units_nm + right_bracket
        units_eV = self.ini_handler('labels', 'read', 'colors (eV)', 'units')
        p_units_eV = left_bracket + units_eV + right_bracket
        units_fs = self.ini_handler('labels', 'read', 'delays', 'units (fs)')
        p_units_fs = left_bracket + units_fs + right_bracket
        units_ps = self.ini_handler('labels', 'read', 'delays', 'units (ps)')
        p_units_ps = left_bracket + units_ps + right_bracket
        units_ns = self.ini_handler('labels', 'read', 'delays', 'units (ns)')
        p_units_ns = left_bracket + units_ns + right_bracket
        
        #w1
        if self.ini_handler('labels', 'read', 'view', 'w1') == 'True':
            w1_wn = self.ini_handler('labels', 'read', 'colors (wn)', 'w1')
            w1_nm = self.ini_handler('labels', 'read', 'colors (nm)', 'w1')
            w1_eV = self.ini_handler('labels', 'read', 'colors (eV)', 'w1')
            eq_w1_wn = between_dimensions + w1_wn
            eq_w1_nm = between_dimensions + w1_nm
            eq_w1_eV = between_dimensions + w1_nm
        else:
            w1_wn = ''
            w1_nm = ''
            w1_eV = ''
            eq_w1_wn = ''
            eq_w1_nm = '' 
            eq_w1_eV = ''
            
        #w2
        if self.ini_handler('labels', 'read', 'view', 'w2') == 'True':
            w2_wn = self.ini_handler('labels', 'read', 'colors (wn)', 'w2')
            w2_nm = self.ini_handler('labels', 'read', 'colors (nm)', 'w2')
            w2_eV = self.ini_handler('labels', 'read', 'colors (eV)', 'w2')
            eq_w2_wn = between_dimensions + w2_wn
            eq_w2_nm = between_dimensions + w2_nm
            eq_w2_eV = between_dimensions + w2_nm
        else:
            w2_wn = ''
            w2_nm = ''
            w2_eV = ''
            eq_w2_wn = ''
            eq_w2_nm = '' 
            eq_w2_eV = ''
            
        #w3
        if self.ini_handler('labels', 'read', 'view', 'w3') == 'True':
            w3_wn = self.ini_handler('labels', 'read', 'colors (wn)', 'w3')
            w3_nm = self.ini_handler('labels', 'read', 'colors (nm)', 'w3')
            w3_eV = self.ini_handler('labels', 'read', 'colors (eV)', 'w3')
            eq_w3_wn = between_dimensions + w3_wn
            eq_w3_nm = between_dimensions + w3_nm
            eq_w3_eV = between_dimensions + w3_nm
        else:
            w3_wn = ''
            w3_nm = ''
            w3_eV = ''
            eq_w3_wn = ''
            eq_w3_nm = '' 
            eq_w3_eV = ''
            
        #wm
        if self.ini_handler('labels', 'read', 'view', 'wm') == 'True':
            wm_wn = self.ini_handler('labels', 'read', 'colors (wn)', 'wm')
            wm_nm = self.ini_handler('labels', 'read', 'colors (nm)', 'wm')
            wm_eV = self.ini_handler('labels', 'read', 'colors (eV)', 'wm')
            eq_wm_wn = between_dimensions + wm_wn
            eq_wm_nm = between_dimensions + wm_nm
            eq_wm_eV = between_dimensions + wm_nm
        else:
            wm_wn = ''
            wm_nm = ''
            wm_eV = ''
            eq_wm_wn = ''
            eq_wm_nm = '' 
            eq_wm_eV = ''
            
        #d1
        if self.ini_handler('labels', 'read', 'view', 'd1') == 'True':
            d1 = self.ini_handler('labels', 'read', 'delays', 'd1')
            eq_d1 = between_dimensions + d1
        else:
            d1 = ''
            eq_d1 = ''
            
        #d2   
        if self.ini_handler('labels', 'read', 'view', 'd2') == 'True':
            d2 = self.ini_handler('labels', 'read', 'delays', 'd2')
            eq_d2 = between_dimensions + d2
        else:
            d2 = ''
            eq_d2 = ''
            
        #decide which particular strings to use for each dimension, unit--------
            
        #colors
        if self.color_units_combo.currentText() == 'wn':
            w1 = w1_wn
            w2 = w2_wn
            w3 = w3_wn
            wm = wm_wn
            eq_w1 = eq_w1_wn
            eq_w2 = eq_w2_wn
            eq_w3 = eq_w3_wn
            eq_wm = eq_wm_wn
            units_color = units_wn
            p_units_color = p_units_wn
        elif self.color_units_combo.currentText() == 'nm':
            w1 = w1_nm
            w2 = w2_nm
            w3 = w3_nm
            wm = wm_nm
            eq_w1 = eq_w1_nm
            eq_w2 = eq_w2_nm
            eq_w3 = eq_w3_nm
            eq_wm = eq_wm_nm
            units_color = units_nm
            p_units_color = p_units_nm
        elif self.color_units_combo.currentText() == 'eV':
            w1 = w1_eV
            w2 = w2_eV
            w3 = w3_eV
            wm = wm_eV
            eq_w1 = eq_w1_eV
            eq_w2 = eq_w2_eV
            eq_w3 = eq_w3_eV
            eq_wm = eq_wm_eV
            units_color = units_eV
            p_units_color = p_units_eV
        else:
            print '  self.color_units_combo.currentText() not recognized in label_autofill'
            return
           
        #delays
        if self.delay_units_combo.currentText() == 'fs':
            units_delay = units_fs
            p_units_delay = p_units_fs
        elif self.delay_units_combo.currentText() == 'ps':
            units_delay = units_ps
            p_units_delay = p_units_ps
        elif self.delay_units_combo.currentText() == 'ns':
            units_delay = units_ns
            p_units_delay = p_units_ns
        else:
            print '  self.delay_units_combo.currentText() not recognized in label_autofill'
            return        
     
        #autofill axes lables---------------------------------------------------
         
        combobox_text = 'undefined!'

        #get the appropriate combobox- - - - - - - - - - - - - - - - - - - -

        if which_label == 'x_axis':
            combobox_text = unicode(self.xvar_combo.currentText())
        elif which_label == 'y_axis':
            combobox_text = unicode(self.yvar_combo.currentText())
        else:
            pass

        #decide what axes_label should be- - - - - - - - - - - - - - - - - -

        axes_label = r'undefined!'

        #if color
        if combobox_text == 'w1':
          axes_label = r'$\mathrm{' + w1 + p_units_color + r'}$'
        elif combobox_text == 'w2':
          axes_label = r'$\mathrm{' + w2 + p_units_color + r'}$'
        elif combobox_text == 'wm':
          if self.colortune_toggle.checkState() == 2: #2=checked
              axes_label = r'$\mathrm{\bar\nu_m-\bar\nu_{OPA} \left(cm^{-1}\right)}$'
          else:
              axes_label = r'$\mathrm{' + wm + p_units_color + r'}$'
        elif combobox_text == 'w1=wm':
          axes_label = r'$\mathrm{' + w1 + eq_wm + p_units_color + r'}$'
        elif combobox_text == 'w2=wm':
          axes_label = r'$\mathrm{' + w2 + eq_wm + p_units_color + r'}$'
        elif combobox_text == 'w1=w2':
          axes_label = r'$\mathrm{' + w1 + eq_w2 + p_units_color + r'}$'
        elif combobox_text == 'w1=w2=wm':
          axes_label = r'$\mathrm{' + w1 + eq_w2 + eq_wm_wn + p_units_color + r'}$'
        else:
            pass
            
        #if delay
        if combobox_text == 'd1':
          axes_label = r'$\mathrm{' + d1 + p_units_delay + r'}$'
        elif combobox_text == 'd2':
          axes_label = r'$\mathrm{' + d2 + p_units_delay + r'}$'
        elif combobox_text == 'd1=d2':
          axes_label = r'$\mathrm{' + d1 + eq_d2 + p_units_delay + r'}$'
        elif combobox_text == '1D data':
          pass
        else:
          pass
        
        #send axes label text to textbox - - - - - - - - - - - - - - - - - -
            
        if which_label == 'x_axis':
            print 'here 2nd'
            self.xvar_title_textbox.setText(axes_label)
            print '  xvar_title_textbox populated'
        elif which_label == 'y_axis':
            self.yvar_title_textbox.setText(axes_label)
            print '  yvar_title_textbox populated'
        else:#problem
            pass
                
        #autofill title---------------------------------------------------------

        title_text = r'$'
        
        value = 'undefined'
        
        if which_label == 'title':
            
            #w1- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            if self.dimension_identity[0] == 'static': #w1
                #get value
                if self.color_units_combo.currentText() == 'wn':
                    value = str(np.around(1e7/(self.data[w1_col, 0]))) + r'\,'
                elif self.color_units_combo.currentText() == 'nm':
                    value = str(np.around(self.data[w1_col, 0])) + r'\,'
                else:
                    print '  color_units_combo value not recognized in axis_label_autofill'
                #create title
                if self.dimensions_equal[0, 1] == True and self.dimensions_equal[0, 2] == True: #w1=w2=wm
                    title_text = title_text + r'\,\,\,\mathrm{' + w1 + eq_w2 + eq_wm + before_value + value + units_color + r'}'
                    self.dimension_identity[1] = 'static with w1'
                    self.dimension_identity[2] = 'static with w1'
                elif self.dimensions_equal[0, 1] == True and self.dimensions_equal[0, 2] == False: #w1=w2
                    title_text = title_text + r'\,\,\,\mathrm{' + w1 + eq_w2 + before_value + value + units_color + r'}'
                    self.dimension_identity[1] = 'static with w1'     
                elif self.dimensions_equal[0, 1] == False and self.dimensions_equal[0, 2] == True: #w1=wm
                    title_text = title_text + r'\,\,\,\mathrm{' + w1 + eq_wm + before_value + value + units_color + r'}'
                    self.dimension_identity[2] = 'static with w1'
                else: #w1 alone
                    title_text = title_text + r'\,\,\,\mathrm{' + w1 + before_value + value + units_color + r'}'
            else:
                pass
            
            #w2- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -         
            if self.dimension_identity[1] == 'static': #w2
                #get value
                if self.color_units_combo.currentText() == 'wn':
                    value = str(np.around(1e7/(self.data[w2_col, 0]))) + r'\,'
                elif self.color_units_combo.currentText() == 'nm':
                    value = str(np.around(self.data[w2_col, 0])) + r'\,'
                else:
                    print '  color_units_combo value not recognized in axis_label_autofill'
                #create title
                if self.dimensions_equal[1, 2] == True: #w2=wm
                    title_text = title_text + r'\,\,\,\mathrm{' + w2 + eq_wm + before_value + value + units_color + r'}'
                    self.dimension_identity[2] = 'static with w1'
                else: #w2 alone
                    title_text = title_text + r'\,\,\,\mathrm{' + w2 + before_value + value + units_color + r'}'
            else:
                pass
        
            #wm- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
            if self.dimension_identity[2] == 'static': #wm alone
                #get value
                if self.color_units_combo.currentText() == 'wn':
                    value = str(np.around(1e7/(self.data[wm_col, 0]))) + r'\,'
                elif self.color_units_combo.currentText() == 'nm':
                    value = str(np.around(self.data[w2_col, 0])) + r'\,'
                else:
                    print '  color_units_combo value not recognized in axis_label_autofill'
                #create title
                title_text = title_text + r'\,\,\,\mathrm{' + wm + before_value + value + units_color + r'}'
            else:
                pass
            
            #d1- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
            if self.dimension_identity[3] == 'static': #d1
                #get value
                value = str(np.around(self.data[d1_col, 0])) + r'\,'
                #create title
                if self.dimensions_equal[3, 4] == True: #d1=d2
                    title_text = title_text + r'\,\,\,\mathrm{' + d1 + eq_d2 + before_value + value + units_delay + r'}'
                    self.dimension_identity[4] = 'static with d1'
                else: #d1 alone
                    title_text = title_text + r'\,\,\,\mathrm{' + d1 + before_value + value + units_delay + r'}'
            else:
                pass
            
            #d2- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
            if self.dimension_identity[4] == 'static': #d2 alone
                #get value
                value = str(np.around(self.data[d2_col, 0])) + r'\,'       
                #set title
                title_text = title_text + r'\,\,\,\mathrm{' + d2 + before_value + value + units_delay + r'}'
            else:
                pass
            
            #set text- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            title_text = title_text+r'$'
            self.plot_title_textbox.setText(title_text)
        
        else:
            pass
        
    def define_colorbar(self):
        
        current_colorbar = self.colorbar_type.currentText()
        
        print ' '
        print 'setting colorbar to', current_colorbar
        
        if current_colorbar == 'default':
            colormap_input = ['#FFFFFF', #white
                              '#0000FF', #blue
                              '#00FFFF', #aqua
                              '#00FF00', #green
                              '#FFFF00', #yellow
                              '#FF0000', #red
                              '#881111'] #burgandy
                              
        elif current_colorbar == 'skyebar':
            colormap_input = ['#FFFFFF', #white
                              '#000000', #black
                              '#0000FF', #blue
                              '#00FFFF', #cyan
                              '#64FF00', #light green
                              '#FFFF00', #yellow
                              '#FF8000', #orange
                              '#FF0000', #red
                              '#800000'] #dark red
                              
        elif current_colorbar == 'greyscale':
            colormap_input = ['#FFFFFF', #white
                              '#000000'] #black
                              
        elif current_colorbar == 'greenscale':
            colormap_input = ['#000000', #black
                              '#00FF00'] #green
                              
        elif current_colorbar == 'signed':
            colormap_input = ['#0000FF', #blue
                              '#002AFF', 
                              '#0055FF',
                              '#007FFF', 
                              '#00AAFF', 
                              '#00D4FF', 
                              '#00FFFF',
                              '#FFFFFF', #white
                              '#FFFF00', 
                              '#FFD400', 
                              '#FFAA00', 
                              '#FF7F00', 
                              '#FF5500', 
                              '#FF2A00',
                              '#FF0000'] #red
                              
        elif current_colorbar == 'flag':
            colormap_input = ['#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000', #black
                              '#FF0000', #red
                              '#FFFFFF', #white
                              '#0000FF', #blue
                              '#000000'] #black    
                              
        elif current_colorbar == 'invisible':
            colormap_input = ['#FFFFFF', #white
                              '#FFFFFF'] #white
                              
        else:
            print 'colorbar type not recognized in define_colorbar!'
            return
            
        f.dat.mycm = mplcolors.LinearSegmentedColormap.from_list('current colormap',colormap_input)
            
    def linetype_choose_apply_defaults(self,
                                       line_to_control,
                                       startup=False):
                                                                                          
        if startup == True:
            if line_to_control == 'contour':
                global contour_color
                contour_color = line_contour_color_default
                global contour_line_width
                contour_line_width = line_contour_line_width_default
                global contour_line_style 
                contour_line_style = line_contour_line_style_default
            elif line_to_control == 'exp':
                global exp_color
                exp_color = line_exp_color_default
                global exp_line_width
                exp_line_width = line_exp_line_width_default
                global exp_line_style 
                exp_line_style = line_exp_line_style_default
            elif line_to_control == 'max':
                global max_color
                max_color = line_max_color_default
                global max_line_width
                max_line_width = line_max_line_width_default
                global max_line_style 
                max_line_style = line_max_line_style_default
            elif line_to_control == 'bin':
                global bin_color
                bin_color = line_bin_color_default
                global bin_line_width
                bin_line_width = line_bin_line_width_default
                global bin_line_style 
                bin_line_style = line_bin_line_style_default
            elif line_to_control == 'abs':
                global abs_color
                abs_color = line_abs_color_default
                global abs_line_width
                abs_line_width = line_abs_line_width_default
                global abs_line_style 
                abs_line_style = line_abs_line_style_default
            else:
                print 'error 0 in linetype_apply_defaults!'
                return
    
        else:  
                                           
            if line_to_control == 'contour':
                
                pass
                
            else:
                
                pass
                
            
            
    def linetype_choose_window_show(self,
                                    line_to_control):
                                
        print ' ' 
        if line_to_control == 'contour':     
            print 'opening window to define contour line properties'     
            self.linetype_window_title = 'define properties for contour lines'        
            self.my_dialog = LinetypeChooseWindow(line_to_control = line_to_control)      
            self.my_dialog.show()
        elif line_to_control == 'exp_value':
          print 'opening window to define expectation value line properties'   
          self.linetype_window_title = 'define properties for expectation value line'
          self.my_dialog = LinetypeChooseWindow(line_to_control = 'exp') 
          self.my_dialog.show()
        elif line_to_control == 'binned_value':
          print 'opening window to define expectation value line properties'
          self.linetype_window_title = 'define properties for binned value lines'
          self.my_dialog = LinetypeChooseWindow(line_to_control = 'bin')
          self.my_dialog.show()
        elif line_to_control == 'max_value':
          print 'opening window to define max value line properties'
          self.linetype_window_title = 'define properties for max value line'
          self.my_dialog = LinetypeChooseWindow(line_to_control = 'max')
          self.my_dialog.show()
        elif line_to_control == 'abs_data':
          print 'opening window to define absorption sideplot line properties'
          self.linetype_window_title = 'define properties for absoprtion data lines'
          self.my_dialog = LinetypeChooseWindow(line_to_control = 'abs')
          self.my_dialog.show()
        else:
            print 'line_to_control not recognized in linetype_choose_window_show!'
            return
            
        global current_linetype_choose_window
        current_linetype_choose_window = self.my_dialog
        
    def ini_handler(self,
                    ini_type,
                    interaction,
                    section,
                    option,
                    value = None):
                        
        #handles reading and writing to ini files with ConfigParser package      
        
        #get correct filepath based on ini_type- - - - - - - - - - - - - - - - -

        ini_filepath = ''
        if ini_type == 'config':
            ini_filepath = os.path.join(filepath_of_folder, 'program files', 'config.ini')
        elif ini_type == 'labels':
            ini_filepath = str(self.label_config_textbox.text())
        else:
            print 'ini_type not recognized in ini_handler'
            return
            
        #do action - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        config = ConfigParser.SafeConfigParser()
        
        if interaction == 'read':
            config.read(ini_filepath) 
            return config.get(section, option)
        elif interaction == 'write':
            value = str(value) #ensure 'value' is a string
            config.read(ini_filepath)
            config.set(section, option, value)  # update
            with open(ini_filepath, 'w') as configfile:    # save
                config.write(configfile)
        
    def cols(self,
             filetype,
             col_name):
                 
        col = 0
                 
        if filetype == '.dat': # - - - - - - - - - - - - - - - - - - - - - - - -
        
            print self.column_combo.currentText()
        
            if self.column_combo.currentText() == '.dat format v0':
                if col_name == 'w1':
                    col = f.dat.cols_v0['w1'][0]
                elif col_name == 'w2':
                    col = f.dat.cols_v0['w2'][0]
                elif col_name == 'w3':
                    print ' '
                    print 'warning! you are calling w3 for .dat format v0'
                    col = 0
                elif col_name == 'wm':
                    col = f.dat.cols_v0['wm'][0]
                elif col_name == 'd1':
                    col = f.dat.cols_v0['d1'][0]
                elif col_name == 'd2':
                    col = f.dat.cols_v0['d2'][0]
                elif col_name == 'data':
                    col = f.dat.cols_v0[str(self.zvar_combo.currentText())][0]
                elif col_name == 'pyro1':
                    col = f.dat.cols_v0[str(self.pyro1_zvar_combo.currentText())][0]
                elif col_name == 'pyro2':
                    col = f.dat.cols_v0[str(self.pyro2_zvar_combo.currentText())][0]
                else:
                    print ' '
                    print 'col_name not recognized in cols'
            elif self.column_combo.currentText() == '.dat format v1':
                if col_name == 'w1':
                    col = f.dat.cols_v1['w1'][0]
                elif col_name == 'w2':
                    col = f.dat.cols_v1['w2'][0]
                elif col_name == 'w3':
                    print ' '
                    print 'warning! you are calling w3 for .dat format v1'
                    col = 0               
                elif col_name == 'wm':
                    col = f.dat.cols_v1['wm'][0]
                elif col_name == 'd1':
                    col = f.dat.cols_v1['d1'][0]
                elif col_name == 'd2':
                    col = f.dat.cols_v1['d2'][0]
                elif col_name == 'data':
                    col = f.dat.cols_v1[str(self.zvar_combo.currentText())][0]
                elif col_name == 'pyro1':
                    col = f.dat.cols_v1[str(self.pyro1_zvar_combo.currentText())][0]
                elif col_name == 'pyro2':
                    col = f.dat.cols_v1[str(self.pyro2_zvar_combo.currentText())][0]
                else:
                    print ' '
                    print 'col_name not recognized in cols'
            elif self.column_combo.currentText() == '.dat format v2':
                if col_name == 'w1':
                    col = f.dat.cols_v2['w1'][0]
                elif col_name == 'w2':
                    col = f.dat.cols_v2['w2'][0]
                elif col_name == 'w3':
                    col = f.dat.cols_v2['w3'][0]  
                elif col_name == 'wm':
                    col = f.dat.cols_v2['wm'][0]
                elif col_name == 'd1':
                    col = f.dat.cols_v2['d1'][0]
                elif col_name == 'd2':
                    col = f.dat.cols_v2['d2'][0]
                elif col_name == 'data':
                    col = f.dat.cols_v2[str(self.zvar_combo.currentText())][0]
                elif col_name == 'pyro1':
                    col = f.dat.cols_v2[str(self.pyro1_zvar_combo.currentText())][0]
                elif col_name == 'pyro2':
                    col = f.dat.cols_v2[str(self.pyro2_zvar_combo.currentText())][0]
                else:
                    print ' '
                    print 'col_name not recognized in cols'         
            else: 
                print ' '
                print 'dat file format not recognized in cols'
                return
        
        else: #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            print ' '
            print 'filetype not recognized in cols'
            
        return col
            
    def add_actions(self, target, actions):

        #to allow for actions in ui        
        
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self,
                        text,
                        slot=None,
                        shortcut=None, 
                        icon=None,
                        tip=None,
                        checkable=False, 
                        signal="triggered()"):
                            
        #to allow for actions in ui        
            
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
     

#animate window class-----------------------------------------------------------

class AnimateWindow(QMainWindow):
    
    def __init__(self,
                 MainWindow_instance,
                 parent=None):

        #initiate window
        QMainWindow.__init__(self, parent)
        self.MainWindow_instance = MainWindow_instance
        
        #set window title
        self.setWindowTitle('create an animation!')

        #set window size        
        window_verti_size = 400
        window_horiz_size = 400
        self.setGeometry(0,0, window_horiz_size, window_verti_size)
        self._center()
        self.resize(window_horiz_size, window_verti_size) 
        self.setMinimumSize(window_horiz_size, window_verti_size)
        self.setMaximumSize(window_horiz_size, window_verti_size)
        
        self.create_main_frame()

    def create_main_frame(self):
                                  
        #where is where all of the main ui stuff gets defined (what & where)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #basic properties for ui
        
        self.main_frame = QWidget()
        vbox = QVBoxLayout()
        
        #load files#############################################################    
        
        #load files row 0- - - - - - - - - - - - - - - - - - - - - - - - - - - -

        file_input_label = QHBoxLayout()
        for w in [ QLabel("load files:  ----------------------------------------------------------------------------------------------------------------------------------------------------------")]:
          file_input_label.addWidget(w)
          file_input_label.setAlignment(w, Qt.AlignVCenter)
        vbox.addLayout(file_input_label)

        #load files row 1- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        my_row = QHBoxLayout()

        my_row.addWidget(QLabel('point datplot to a folder containing all the dat files you wish to include'))        
        
        my_row.setAlignment(Qt.AlignVCenter)     
        vbox.addLayout(my_row)           
        
        #load files row 4- - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        my_row = QHBoxLayout()

        my_row.addWidget(QLabel('please ensure that all files in that folder have the same dimensions'))        
        
        my_row.setAlignment(Qt.AlignVCenter)     
        vbox.addLayout(my_row)       

        #choose dimensions######################################################   

        #choose dimensions row 0 - - - - - - - - - - - - - - - - - - - - - - - -
 
        file_input_label = QHBoxLayout()
        for w in [ QLabel("choose dimensions:  ----------------------------------------------------------------------------------------------------------------------------------------------------------")]:
          file_input_label.addWidget(w)
          file_input_label.setAlignment(w, Qt.AlignVCenter)
        vbox.addLayout(file_input_label)
  
        #choose dimensions row 1 - - - - - - - - - - - - - - - - - - - - - - - -
        
        my_row = QHBoxLayout()
                
        #animate_along_dimension combobox
        self.animate_along_combobox = QComboBox()
        dimensions = ['w1',
                      'w2',
                      'wm',
                      'd1',
                      'd2']
        self.animate_along_combobox.addItems(dimensions)
        my_row.addWidget(QLabel('animate along:'))
        my_row.addWidget(self.animate_along_combobox)
        my_row.addSpacing(300)
        
        #forwards_or_backwards
        self.animation_direction_combobox = QComboBox()
        directions = ['downwards',
                      'upwards']
        self.animation_direction_combobox.addItems(directions)
        self.animation_direction_combobox.setToolTip('downwards - largest to smallest value\nupwards - smallest to largest value')
        my_row.addWidget(QLabel('direction:'))
        my_row.addWidget(self.animation_direction_combobox)
        
        my_row.setAlignment(Qt.AlignVCenter)     
        vbox.addLayout(my_row)       

        #choose dimensions row 2 - - - - - - - - - - - - - - - - - - - - - - - -
        
        my_row = QHBoxLayout()

        my_row.addWidget(QLabel('datplot will use following files (as ordered):'))  
        my_row.addSpacing(100)
        
        #reload files button
        self.reload_files_button = QPushButton('load/reload')
        self.reload_files_button.clicked.connect(lambda: self.load_files())
        my_row.addWidget(self.reload_files_button)
        
        my_row.setAlignment(Qt.AlignVCenter)     
        vbox.addLayout(my_row)       
        
        #choose dimensions row 3 - - - - - - - - - - - - - - - - - - - - - - - -

        my_row = QHBoxLayout()

        self.file_table = QTableWidget()
        #self.file_table.setMaximumHeight(100)
        
        my_row.addWidget(self.file_table)
        vbox.addLayout(my_row)   
       
        #choose dimensions row 4 - - - - - - - - - - - - - - - - - - - - - - - -

        my_row = QHBoxLayout()
        
        #interpolate
        self.interpolate_frames_toggle = QCheckBox('interpolate data')
        my_row.addWidget(self.interpolate_frames_toggle)
        my_row.addSpacing(110)
                
        #to step size x
        self.nframes = QDoubleSpinBox()
        self.nframes.setMinimum(1)
        self.nframes.setSingleStep(1)
        self.nframes.setDecimals(0)
        self.nframes.setValue(25)
        my_row.addWidget(QLabel('number of frames:'))
        my_row.addWidget(self.nframes)
                
        my_row.setAlignment(Qt.AlignVCenter)     
        vbox.addLayout(my_row)     

        #presentation###########################################################        

        #presentation row 0- - - - - - - - - - - - - - - - - - - - - - - - - - -

        file_input_label = QHBoxLayout()
        for w in [ QLabel("presentation:  ----------------------------------------------------------------------------------------------------------------------------------------------------------")]:
          file_input_label.addWidget(w)
          file_input_label.setAlignment(w, Qt.AlignVCenter)
        vbox.addLayout(file_input_label)
        
        #presentation row 1- - - - - - - - - - - - - - - - - - - - - - - - - - -

        my_row = QHBoxLayout()
        
        #plot on the same colorbar
        self.share_colorbar_toggle = QCheckBox('frames share colorbar')
        self.share_colorbar_toggle.setChecked(True)
        my_row.addWidget(self.share_colorbar_toggle)
        my_row.addSpacing(75)
        
        #the speed factor control
        self.animation_speed_factor_textbox = QLineEdit()
        self.animation_speed_factor_textbox.setText('1.0')
        my_row.addWidget(QLabel('animation speed factor:'))
        my_row.addWidget(self.animation_speed_factor_textbox)
        
        my_row.setAlignment(Qt.AlignVCenter)        
        vbox.addLayout(my_row)

        #animate################################################################        

        #animate row 0 - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        file_input_label = QHBoxLayout()
        for w in [ QLabel("animate:  ----------------------------------------------------------------------------------------------------------------------------------------------------------")]:
          file_input_label.addWidget(w)
          file_input_label.setAlignment(w, Qt.AlignVCenter)
        vbox.addLayout(file_input_label)

        #animate row 1 - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        my_row = QHBoxLayout()
        
        #the 'animate' push-button
        self.animate_button = QPushButton("animate")
        self.animate_button.clicked.connect(lambda: self.on_animate())
        my_row.addWidget(QLabel('animation could take a while - ensure your choices are correct'))
        my_row.addWidget(self.animate_button)        
        
        my_row.setAlignment(Qt.AlignVCenter)        
        vbox.addLayout(my_row)
                
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #activate ui
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame) 
        
    def on_animate(self):

        #startup - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        MainWindow.animating = True
        
        print ' '
        print 'on_animate running'      
        
        #clear images_to_stitch directory
        stitch_folder_path = os.path.join(filepath_of_folder, 'temp', 'images_to_stitch')
        os.chdir(stitch_folder_path)
        for any_file in glob.glob('*.*'):
            os.remove(any_file)
            
        dat_files = self.dat_files
            
        #get output filepath - - - - - - - - - - - - - - - - - - - - - - - - - -
            
        print ' '
        print 'choose your savefile!'

        #get path of folder dat files folder
        filepath = str(MainWindow.dat_filepath_textbox.text())
        folderpath = os.path.dirname(filepath)

        #get path of outupt animation via QFileDialog
        default_filename = folderpath + '\\animation.mp4'
        output_path = QFileDialog.getSaveFileName(self,
                                                  'save animation', #window title
                                                  default_filename,
                                                  'MP4 files (*.mp4);;All Files (*.*)')             
        output_path = str(output_path)

        #interpolate (if desired)- - - - - - - - - - - - - - - - - - - - - - - -

        if self.interpolate_frames_toggle.checkState() == 2: #2=checked
            self.interpolate_dat_files()
        else:
            pass

        #find znull, zmax (if needed)- - - - - - - - - - - - - - - - - - - - - -

        if self.share_colorbar_toggle.checkState() == 2: #2 = checked
            zmin_array = np.zeros(len(dat_files))
            zmax_array = np.zeros(len(dat_files))
            for i in range(len(dat_files)): 
                #change filepath textbox
                current_dat_filepath = os.path.join(folderpath + '\\' + dat_files[i])
                MainWindow.dat_filepath_textbox.setText(current_dat_filepath)
                MainWindow.load_file('main .dat file')      
                #load file into fscolors and pass through all manipulations
                MainWindow.on_plot('pass', 'default')
                #extract zmin, zmax
                zmin_array[i] = MainWindow.instance.zmin
                zmax_array[i] = MainWindow.instance.zmax
                #...
                print dimension_identity
            MainWindow.zmin_choose.setText(str(np.min(zmin_array)))
            MainWindow.zmax_choose.setText(str(np.max(zmax_array)))
        else:
            MainWindow.zmin_choose.setText('native')
            MainWindow.zmax_choose.setText('native')

        #generate images - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        for i in range(len(dat_files)):
            #change filepath textbox
            current_dat_filepath = os.path.join(folderpath + '\\' + dat_files[i])
            MainWindow.dat_filepath_textbox.setText(current_dat_filepath)
            MainWindow.load_file('main .dat file')      
            #create properly named image file
            current_filename = 'image' + str(i).zfill(5) + '.png'
            MainWindow.animating_current_save_path = os.path.join(stitch_folder_path + '\\' + current_filename)
            MainWindow.on_plot('save', 'default')
            print dimension_identity

        #stitch images into video file - - - - - - - - - - - - - - - - - - - - -
        
        print ' '
        print 'calling ffmpeg subprocess'
        print 'messages from ffmpeg to follow:'
        print ' '
        
        speed_factor = str(float(self.animation_speed_factor_textbox.text()))
        
        chdir_path = stitch_folder_path
        os.chdir(chdir_path)
        
        subprocess.call(['ffmpeg',        #main application
                         '-f',            #?
                         'image2',        #?
                         '-r',            #?
                         speed_factor,    #speed factor (higher = faster)
                         '-i',            #?
                         'image%05d.png', #input filename format (image00001.png, for example)
                         '-vcodec',       #?
                         'mpeg4',         #quicktime mp4
                         '-y',            #?
                         output_path])    #final output filepath

        #delete images - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        chdir_path = os.path.join(filepath_of_folder, 'temp', 'images_to_stitch')
        os.chdir(chdir_path)
        for any_file in glob.glob('*.*'):
            os.remove(any_file)

        #finish- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                
        print ' '
        print 'animation generation complete!'        
        
        MainWindow.animating = False
        
    def interpolate_dat_files(self):
        
        #startup - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        print ' '
        print 'interpolate_dat_files is running!'
        
        #make variables local
        dat_files = self.dat_files
        value = self.value

        #get path of folder dat files folder
        filepath = str(MainWindow.dat_filepath_textbox.text())
        folderpath = os.path.dirname(filepath)

        #learn dimensons of dat files- - - - - - - - - - - - - - - - - - - - - -

        #change filepath textbox
        current_dat_filepath = os.path.join(folderpath + '\\' + dat_files[0])
        MainWindow.dat_filepath_textbox.setText(current_dat_filepath)
        MainWindow.load_file('main .dat file')      
        #load file into fscolors and pass through all manipulations
        MainWindow.on_plot('pass', 'default')
        #extract information
        dat_xi = MainWindow.instance.xi
        dat_yi = MainWindow.instance.yi

        #create 3D dataset of raw data - - - - - - - - - - - - - - - - - - - - -

        raw_dataset = np.zeros([len(dat_files), len(dat_xi), len(dat_yi)])
        for i in range(len(dat_files)):
            #change filepath textbox
            current_dat_filepath = os.path.join(folderpath + '\\' + dat_files[i])
            MainWindow.dat_filepath_textbox.setText(current_dat_filepath)
            MainWindow.load_file('main .dat file')      
            #load file into fscolors and pass through all manipulations
            MainWindow.on_plot('pass', 'default')
            #add data to raw dataset
            raw_dataset[i] = MainWindow.instance.zi

        #generate array of frame values- - - - - - - - - - - - - - - - - - - - -  

        number_of_frames = float(self.nframes.text())
        
        interpolation_values = np.linspace(np.max(value), #start
                                           np.min(value), #stop
                                           number_of_frames)

        #interpolate 3D dataset onto interpolation_values- - - - - - - - - - - -

        print ' '
        print 'interpolating 3D dataset'
        print '  this could take a while, please be patient...'

        #unpack raw dataset into a 1D array
        #and associate each point with the 3 values
        t_values = np.zeros(0)
        x_values = np.zeros(0)
        y_values = np.zeros(0)
        data_values = np.zeros(0)  
        for i in range(len(raw_dataset[:, 0, 0])):
            for j in range(len(raw_dataset[0, :, 0])):
                for k in range(len(raw_dataset[0, 0, :])):
                    t_values = np.append(t_values, value[i])
                    x_values = np.append(x_values, dat_xi[j])
                    y_values = np.append(y_values, dat_yi[k])
                    data_values = np.append(data_values, raw_dataset[i,j,k])
        
        #create similar 1D arrays for 'destination' array values
        t_finals = np.zeros(0)
        x_finals = np.zeros(0)
        y_finals = np.zeros(0)
        for i in range(len(interpolation_values)):
            for j in range(len(dat_xi)):
                for k in range(len(dat_yi)):
                    t_finals = np.append(t_finals, interpolation_values[i])
                    x_finals = np.append(x_finals, dat_xi[j])
                    y_finals = np.append(y_finals, dat_yi[k])
        
        #interpolate data with griddata (scipy)
        interpolated_dataset = griddata((t_values, x_values, y_values), #original values
                                        data_values, #data corresponding to intial values
                                        (t_values[None,:], x_values[None,:], y_values[None,:]), #final values
                                        method='linear',
                                        fill_value=0.0)
        
        print '  done!'
        print '  interpolated_dataset.shape = ', interpolated_dataset.shape
                                 
        #write dat file for each frame - - - - - - - - - - - - - - - - - - - - -

        #get path of place to save files
        fakedat_folderpath = os.path.join(filepath_of_folder, 'temp', 'generated_dat_files')      
        os.chdir(fakedat_folderpath)
      
        #clear previous files in folder
        for any_file in glob.glob('*.*'):
            os.remove(any_file)
        
        #clear current dat_files array
        dat_files = np.zeros(0, dtype=str)        
        
        #write dat files
        print ' '
        for i in range(len(interpolation_values)):
            #create fakedata array
            fakedat_array = np.zeros(0)
            #...........................................
            #...........................................
            #create file
            current_filepath = os.path.join(fakedat_folderpath, '\\{}.fakedat'.format(i))
            fakedat = open(current_filepath, 'w')
            #write to file
            np.savetxt(fakedat, fakedat_array)
            #close file
            fakedat.close()
            #append filepath onto dat_files
            dat_files = np.append(dat_files, current_filepath)
            #finish
            print 'fake dat file {0} of {1} written...'.format(i+1, len(interpolation_values))
            pass

        #return new fake dat files - - - - - - - - - - - - - - - - - - - - - - - 

        self.dat_files = dat_files
        
    def load_files(self):

        #startup - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -        
        
        print ' '
        print 'load_files running'
        
        #clear table
        for i in range(self.file_table.rowCount()):
            self.file_table.removeRow(0)
        for i in range(self.file_table.columnCount()):
            self.file_table.removeColumn(0)

        #get path of folder dat files folder
        filepath = str(MainWindow.dat_filepath_textbox.text())
        folderpath = os.path.dirname(filepath)

        #use glob to find all files that end with .dat in folder 'folderpath'- -
        os.chdir(folderpath)
        self.dat_files = np.zeros(0, dtype=str)
        for dat_file in glob.glob("*.dat"):
            self.dat_files = np.append(self.dat_files, dat_file)
        print '  found {} .dat files:'.format(len(self.dat_files))

        #order files correctly - - - - - - - - - - - - - - - - - - - - - - - - - 
       
        self.value = np.zeros(len(self.dat_files))
        for i in range(len(self.dat_files)):
            current_dat_filepath = os.path.join(folderpath + '/' + self.dat_files[i])
            MainWindow.discover_dimensions(current_dat_filepath)
            self.value[i] = np.around(dimension_average[self.animate_along_combobox.currentIndex()])
        
        #sort files
        file_order = np.argsort(self.value)
        dat_files_dummy = copy.deepcopy(self.dat_files)
        value_dummy = copy.deepcopy(self.value)
        for i in range(len(file_order)):
            #deal with reversal option
            if self.animation_direction_combobox.currentText() == 'downwards':
                current_file = file_order[len(file_order)-1-i]
            elif self.animation_direction_combobox.currentText() == 'upwards':
                current_file = file_order[i]
            else:
                print 'animation_direction_combobox.currentText() not recognized in load_files!'

            #sort files accordingly
            self.dat_files[i] = dat_files_dummy[current_file]
            self.value[i] = value_dummy[current_file]
        
        #fill table- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

        #create column to hold dat filepaths
        self.file_table.insertColumn(0)
        header = QTableWidgetItem()
        header.setText('.dat file')
        self.file_table.setHorizontalHeaderItem(0, header)
        self.file_table.setColumnWidth(0, 247)

        #create column to hold dimension value
        self.file_table.insertColumn(1)
        header = QTableWidgetItem()
        header.setText('dimension value')
        self.file_table.setHorizontalHeaderItem(1, header)
        self.file_table.setColumnWidth(1, 100)
       
        for i in range(len(self.dat_files)):
            #create row
            self.file_table.insertRow(i)
            #fill filepath name
            cell = QTableWidgetItem()
            cell.setText(self.dat_files[i])
            self.file_table.setItem(i, 0, cell)
            self.file_table.setRowHeight(i, 25)
            #fill dimension value
            cell = QTableWidgetItem()
            cell.setText(str(self.value[i]))
            self.file_table.setItem(i, 1, cell)
            self.file_table.setRowHeight(i, 25)           

    def _center(self):
        #a function which ensures that the window appears in the center of the screen at startup
        
        screen = QDesktopWidget().screenGeometry() 
        size = self.geometry() 
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
class LinetypeChooseWindow(QMainWindow):

    def __init__(self,
                 line_to_control,
                 parent=None):
        
        #initiate window
        QMainWindow.__init__(self, parent)
        self.line_to_control = line_to_control
        
        #set window title
        self.setWindowTitle('choose ' + line_to_control + ' line properties')

        #set window size        
        window_verti_size = 450
        window_horiz_size = 510
        self.setGeometry(0,0, window_horiz_size, window_verti_size)
        self._center()
        self.resize(window_horiz_size, window_verti_size) 
        self.setMinimumSize(window_horiz_size, window_verti_size)
        self.setMaximumSize(window_horiz_size, window_verti_size)
        
        #call upon currently set colors etc
        if line_to_control == 'contour':
          color = contour_color
          line_width = contour_line_width
          line_style = contour_line_style
        elif line_to_control == 'exp':
          color = exp_color
          line_width = exp_line_width
          line_style = exp_line_style
        elif line_to_control == 'bin':
          color = bin_color
          line_width = bin_line_width
          line_style = bin_line_style
        elif line_to_control == 'max':
          color = max_color
          line_width = max_line_width
          line_style = max_line_style
        elif line_to_control == 'abs':
          color = abs_color
          line_width = abs_line_width
          line_style = abs_line_style
        else:
          print ' '
          print 'line_to_control not recognized in LinetypeChooseWindow__init__!'

        #call create_main_frame function (will fill in all custom elements)
        self.create_linetype_frame(color = color,
                                   line_width = line_width,
                                   line_style = line_style)
                                
    def create_linetype_frame(self,
                              color,
                              line_width,
                              line_style):
                                  
        #where is where all of the main ui stuff gets defined (what & where)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #basic properties for ui
        
        self.main_frame = QWidget()
        vbox = QVBoxLayout()
        
        #row 0 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        my_row = QHBoxLayout()
        my_row.addWidget(QLabel('choose line color: -----------------------------------------------------------------------------------------------------------------------------'))
        my_row.setAlignment(Qt.AlignVCenter)
        vbox.addLayout(my_row)
        
        #row 1 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -        
        
        my_row = QHBoxLayout()
        
        my_startup_color = QColor(color)
        self.my_color_picker = QColorDialog(my_startup_color)
        self.my_color_picker.setOption(QColorDialog.NoButtons)
        my_row.addWidget(self.my_color_picker)
        
        my_row.setAlignment(Qt.AlignVCenter)
        vbox.addLayout(my_row)
        
        #row 2 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        my_row = QHBoxLayout()
        my_row.addWidget(QLabel('choose line properties: -----------------------------------------------------------------------------------------------------------------------------'))
        my_row.setAlignment(Qt.AlignVCenter)
        vbox.addLayout(my_row)
        
        #row 4 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        my_row = QHBoxLayout()
        
        #line style combobox 
        self.line_style_combo = QComboBox()
        line_style_combo_options = ['solid',       #0
                                    'dashed',      #1
                                    'dotted',      #2
                                    'dashdot']     #3
        self.line_style_combo.addItems(line_style_combo_options)    
        if line_style == 'solid':
            self.line_style_combo.setCurrentIndex(0)
        elif line_style == 'dashed':
            self.line_style_combo.setCurrentIndex(1)
        elif line_style == 'dotted':
            self.line_style_combo.setCurrentIndex(2)
        elif line_style == 'dashdot':
            self.line_style_combo.setCurrentIndex(3)
        else:
            print ' '
            print 'line_style not recognized!'
            return
        self.line_style_combo.setMinimumWidth(100)
        my_row.addWidget(QLabel('line style:'))
        my_row.addWidget(self.line_style_combo)
        my_row.addSpacing(200)
        #disable line style combobox if doing contour, where there is no control
        if self.line_to_control in ['contour', 'abs', 'bin']:
            self.line_style_combo.setCurrentIndex(0)
            self.line_style_combo.setDisabled(True)
            self.line_style_combo.setToolTip('cannot (yet) control line style of {} lines'.format(self.line_to_control))
        else:
            pass
        
        #linewidth textbox
        self.linewidth_textbox = QLineEdit()
        self.linewidth_textbox.setText(str(line_width))
        my_row.addWidget(QLabel('line weight:'))
        my_row.addWidget(self.linewidth_textbox)
             
        my_row.setAlignment(Qt.AlignVCenter)
        vbox.addLayout(my_row)
        
        
        #row 4 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
        my_row = QHBoxLayout()
        my_row.addWidget(QLabel('choose action: -----------------------------------------------------------------------------------------------------------------------------'))
        my_row.setAlignment(Qt.AlignVCenter)
        vbox.addLayout(my_row)
        
        #row 5 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        my_row = QHBoxLayout()
        
        #the set to defaults button
        self.set_to_defaults_button = QPushButton("reset to defaults")
        self.set_to_defaults_button.clicked.connect(lambda: self.on_defaults())
        my_row.addWidget(self.set_to_defaults_button)
        
        #the cancel button
        self.cancel_button = QPushButton("cancel")
        self.cancel_button.clicked.connect(lambda: self.on_cancel())
        my_row.addWidget(self.cancel_button)
        
        #the apply button
        self.apply_button = QPushButton("apply")
        self.apply_button.clicked.connect(lambda: self.on_apply())
        my_row.addWidget(self.apply_button)
        
        my_row.setAlignment(Qt.AlignVCenter)
        vbox.addLayout(my_row)
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #activate ui
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)  

    def on_defaults(self):
        
        print '  setting to defaults'
        
        if self.line_to_control == 'contour':
            global contour_color
            contour_color = line_contour_color_default
            global contour_line_width
            contour_line_width = line_contour_line_width_default
            global contour_line_style 
            contour_line_style = line_contour_line_style_default
        elif self.line_to_control == 'exp':
            global exp_color
            exp_color = line_exp_color_default
            global exp_line_width
            exp_line_width = line_exp_line_width_default
            global exp_line_style 
            exp_line_style = line_exp_line_style_default
        elif self.line_to_control == 'max':
            global max_color
            max_color = line_max_color_default
            global max_line_width
            max_line_width = line_max_line_width_default
            global max_line_style 
            max_line_style = line_max_line_style_default
        elif self.line_to_control == 'bin':
            global bin_color
            bin_color = line_bin_color_default
            global bin_line_width
            bin_line_width = line_bin_line_width_default
            global bin_line_style 
            bin_line_style = line_bin_line_style_default
        elif self.line_to_control == 'abs':
            global abs_color
            abs_color = line_abs_color_default
            global abs_line_width
            abs_line_width = line_abs_line_width_default
            global abs_line_style 
            abs_line_style = line_abs_line_style_default
            
        #restart (not the cleanest, but it works)
        global current_linetype_choose_window
        self.store_customs_and_close()
        self.my_dialog = LinetypeChooseWindow(line_to_control = self.line_to_control)
        self.my_dialog.show()
        current_linetype_choose_window = self.my_dialog
    
    def on_cancel(self):
      
        print '  action canceled - no changes applied'
        
        #close
        self.store_customs_and_close()
    
    def on_apply(self):
        
        #collect variables from UI
        color_input = str((self.my_color_picker.currentColor()).name())
        line_width_input = float(self.linewidth_textbox.text())
        line_type_input = str(self.line_style_combo.currentText())
        
        #store to globals
        if self.line_to_control == 'contour':
          global contour_color
          contour_color = color_input
          global contour_line_width
          contour_line_width = line_width_input
          global coutour_line_style
          coutour_line_style = line_type_input
        elif self.line_to_control == 'exp':
          global exp_color
          exp_color = color_input
          global exp_line_width
          exp_line_width = line_width_input
          global exp_line_style
          exp_line_style = line_type_input
        elif self.line_to_control == 'bin':
          global bin_color
          bin_color = color_input
          global bin_line_width
          bin_line_width = line_width_input
          global bin_line_style
          bin_line_style = line_type_input
        elif self.line_to_control == 'max':
          global max_color
          max_color = color_input
          global max_line_width
          max_line_width = line_width_input
          global max_line_style
          max_line_style = line_type_input
        elif self.line_to_control == 'abs':
          global abs_color
          abs_color = color_input
          global abs_line_width
          abs_line_width = line_width_input
          global abs_line_style
          abs_line_style = line_type_input
        else:
          print ' '
          print 'line_to_control not recognized in on_apply!'
        
        print '  color set to', color_input
        print '  line style set to', abs_line_style
        print '  line width set to', abs_line_width
        
        #close
        #save custom colors
        for i in range(self.my_color_picker.customCount()):
          custom_color_value = self.my_color_picker.customColor(i)
          self.my_color_picker.setCustomColor(i, custom_color_value)
          
        #close window
        current_linetype_choose_window.close()
        
    def store_customs_and_close(self):
      
        #save custom colors
        for i in range(self.my_color_picker.customCount()):
          custom_color_value = self.my_color_picker.customColor(i)
          self.my_color_picker.setCustomColor(i, custom_color_value)
          
        #close window
        current_linetype_choose_window.close()
                                     
    def _center(self):
        
        #a function which ensures that the window appears in the center of the screen at startup
        
        screen = QDesktopWidget().screenGeometry() 
        size = self.geometry() 
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
#small piece of code to actually execute 'AppForm' when python runs code--------
#this allows the user to double click on the file to run the program

def main():
    app = QApplication(sys.argv)
    global MainWindow
    MainWindow = MainWindow()
    MainWindow.show()
    app.exec_()
    return MainWindow
main_form = main()
print main_form