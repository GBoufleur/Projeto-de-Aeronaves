'''
This script executes the Fokker 100 example
'''

#IMPORTS
import numpy as np
from designTool.standard_airplane import standard_airplane
from designTool.geometry import geometry
from designTool.plots import plot_geometry
import pprint
from designTool.plot_views import plot_geometry_views


#=========================================

# SETUP

# Select airplane name from the standard_airplane function in designTool
airplane_name = 'crusair2'
#airplane_name = 'my_airplane'

#=========================================

# EXECUTION

# Load the airplane dictionary
airplane = standard_airplane(airplane_name)

# Execute the geometry module to compute all dimensions.
# This updates the airplane dictionary with new entries.
geometry(airplane)

# Plot airplane
plot_geometry(airplane, figname='3dview.png', az1=45, az2=-135)

# Plot airplane from three standard views
plot_geometry(airplane, figname='3dview_bottom.png', az1=-90, az2=0)
plot_geometry(airplane, figname='3dview_front.png', az1=0, az2=-90)
plot_geometry(airplane, figname='3dview_side.png', az1=0, az2=0)

# Print final dictionary
print(pprint.pformat(airplane))