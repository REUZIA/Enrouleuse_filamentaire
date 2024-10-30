import cfg
import numpy as np

# Home all axes

# write coordinates arrays

def gcode_write_traj(Ltheta, Lz, Lr, Lomega, Lorient) :
	assert len(Ltheta) == len(Lz) == len(Lr) == len(Lomega) == len(Lorient), 'Bad coordinate list size'

	# creating Vz
	L_Vz = [s for s in [cfg.carriage_speed]*len(Lomega)]

	# scaling Lomega and converting to deg/s
	Lomega = [np.rad2deg(omega)*cfg.carriage_speed for omega in Lomega]

	#print(f'Z motion for a whole spin : {(360/Lomega[0])*cfg.carriage_speed}')

	with open(cfg.output_file, 'a') as f: 
		for (theta, Z, R, omega, Vz, cur_orient) in zip(Ltheta, Lz, Lr, Lomega, L_Vz, Lorient) :
			f.write((f"{cfg.gcode_axis_theta}{np.rad2deg(theta)} "
				f"{cfg.gcode_axis_Z}{Z} "
#				f"{cfg.gcode_axis_R}{R+cfg.R_offset} "
				f"{cfg.gcode_speed_omega}{omega} "
				f"{cfg.gcode_speed_carriage}{Vz} "
				f"{cfg.gcode_filament_orientation}{cur_orient}\n"))
	
def gcode_write_comment(comment) :
	with open(cfg.output_file, 'a') as f: 
		f.write(f'#{comment}\n')

def gcode_clear() :
	with open(cfg.output_file, 'w') as f :

		cfg_vars = [item for item in dir(cfg) if not item.startswith("__")]

		for var in cfg_vars :
			f.write(f'# {var} = {getattr(cfg, var)} ')
		
#		f.write(f'#{cfg.gcode_axis_theta} (spindle angle) | {cfg.gcode_axis_Z} (carriage longitudinal position) | {cfg.gcode_axis_R} (carriage radial position) | {cfg.gcode_speed_omega} (spindle speed in deg/s) | {cfg.gcode_speed_carriage} (carriage speed in mm/s) \n')
		#f.write(f'#{cfg.gcode_axis_theta} (spindle angle) | {cfg.gcode_axis_Z} (carriage longitudinal position) | {cfg.gcode_speed_omega} (spindle speed in deg/s) | {cfg.gcode_speed_carriage} (carriage speed in mm/s) \n')
		f.write(f'#{cfg.gcode_axis_theta} (spindle angle) | {cfg.gcode_axis_Z} (carriage longitudinal position) | {cfg.gcode_speed_omega} (spindle speed in deg/s) | {cfg.gcode_speed_carriage} (carriage speed in mm/s) | {cfg.gcode_filament_orientation} (filament orientation in deg) \n')
			

# write single array
