from datetime import datetime


import numpy as np

# Tube / fairing parameters
######################
# Mandrel settings
L = 1900. # longueur en mm
R = 125. # rayon en mm
# Fairing settings (if applicable)
C = .66 # paramètre de von Karman 

top_margin = 0. # useless for cylinders
bot_margin = 0. # distance from Z origin
cyl_Z_offset = 0.

# Fiber orientation (uncomment whichever mode is wanted)
####################
# Orientation setting (X winding)
orient = 30 # fiber orientation in degrees
# Step setting (hoop winding)
#filament_step = 100 # in mm
#orient = np.rad2deg(np.arcsin(filament_step / (2*np.pi*R)))

# legacy and wrong
#orient = np.rad2deg(np.deg2rad(90)-np.arctan((2*np.pi*R)/filament_step))

# Speeds / feeds
################
carriage_speed = 50 # carriage speed acts a speed multiplicator applied to both omega and Vz, not changing their ratio
om_func = lambda r : Vtan/r
Vtan = np.tan(np.deg2rad(90-orient)) # Vtan(z) ; implicitely, Vz = 1mm/s

# personal gibberish, keeping it just in case
# arbitrary_tan_speed_cst : vitesse linéaire tangentielle de référence (mm/s) 
# => v_cst = arbitrary_tan_speed_cst = omega*r => omega = arbitrary_tan_speed_cst / r
# fonction omega : donne la vitesse angulaire du tube
#om_func = lambda r : arbitrary_tan_speed_cst/(r/r)
#arbitrary_tan_speed_cst = .06
#om_func = lambda r : Vtan/r
#Vtan = np.tan(np.deg2rad(90-orient)) # Vtan(z) ; implicitely, Vz = 1mm/s
#om_func = lambda r : arbitrary_tan_speed_cst/(r*r)
#arbitrary_tan_speed_cst = 30

# Winding parameters
#####################
halfpass_shift = 180 # shift (deg) between halfpass FWD and halfpass BWD
#pass_shift = 45 # shift en degrès à la fin de chaque passe
#pass_count = int(360/pass_shift) #automated calculation for rendering all passes
#pass_shift = 135
#pass_count = 24 # number of passes to do. For optimal hoop results, use pass_count = int(360/pass_shift).
#pass_shift = 180 - 360/pass_count
pass_count = 80 # number of passes to do. For optimal hoop results, use pass_count = int(360/pass_shift).
pass_shift = 360/80

fwd_orient = -45

# Point density
################
step = 10 # Z step between points in mm
R_offset = 0

# Gcode generation
###################
output_file = f'{datetime.today().strftime("%Y-%m-%d-%H:%M:%S")}_X_{pass_count}P_L{L}mm_R{R}mm.gcode'

gcode_axis_theta = 'A'
gcode_speed_omega = 'S'

gcode_axis_Z = 'B'
gcode_speed_carriage = 'F'

gcode_filament_orientation = 'D'

#gcode_axis_R = 'C'

# Misc / irrelevant
#######
plot_mode = '3d'
spindle_speed = np.rad2deg(((carriage_speed*np.tan(np.deg2rad(90-orient)))/R))# in deg/s
# LEGACY
# use THIS for fairing
#top_margin = 30. # longueur en mm du cylindre devant coiffe (petit diam.)
#bot_margin = 80. # longueur en mm du cylindre derrière coiffe (gros diam.)
#step_count = 
