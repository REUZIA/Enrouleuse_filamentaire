#####################
# General notations #
#####################

''' Reference frame
z (mm) : distance from home on main carriage sliding axis // déplacement du chariot
r(z) (mm) : radius of the fairing for a given z // rayon de la pose du fil (au début rayon du tube)
omega(z) : calculated angular speed of the fairing for a given z, //vitesse de rotation du tube
           such that tangential linear speed remains the same all along the fairing
c(z) (deg) : fairing angle at a given z
'''

# Imports
##########

import cfg
import plotting
import curve_generation

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation

import gcode_editor

# Global vars
##############

global current_theta
current_theta = 0


#
def get_angle(a, b, c) :
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)

# Returns a list of equally spaced positions for the x axis (values are in mm)
def get_Lz() :

    Lz = np.concatenate((
        np.arange(1, cfg.top_margin, cfg.step), 
        np.arange(cfg.top_margin, cfg.L, cfg.step),
        np.arange(cfg.L, cfg.L + cfg.bot_margin, cfg.step),
        ))

    return np.array(Lz)

def omega(r) :

    return cfg.om_func(r)

## Get a list of Y speeds for each slice
#def get_LVr() :

# intégrer : ajouter theta(n) + (omega(n) - omega(n-1))
def get_theta(Lomega) :
    global current_theta

    #print(np.rad2deg(current_theta))

    theta = current_theta
    Ltheta = []
    for omega in Lomega :
        Ltheta.append(theta)
        theta += omega*cfg.step

    current_theta = Ltheta[-1]
        
    return np.array(Ltheta)


if __name__ == '__main__':
    # Get a list of z according to the cfg.step
    Lz = get_Lz()

    print(f"=DEBUG= Number of slices : {len(Lz)}")
    # Get a list of radii matching each z
    Lr = curve_generation.curve(Lz)

    # Get inverted values for return pass
    LzRev = list(reversed(Lz)) 
    LrRev = list(reversed(Lz)) 

    if(cfg.plot_mode == '2d') :
        '''2D plotting fairing curve'''
        plt.plot(Lz, Lr, label='r(mm)')

    # Get spindle angular speed
    Lomega = omega(Lr)

    if(cfg.plot_mode == '2d') :
        '''2D plotting angular speed'''
        plt.plot(Lz, Lomega*3000, label='ω(x) (rad/s)')

    else :
        '''3D preparing plot'''
        #ax = plt.axes(projection='3d')
        fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
        ax.set_xlim3d((-1.1*cfg.L/2, 1.1*cfg.L/2)) 
        ax.set_ylim3d((-1.1*cfg.L/2, 1.1*cfg.L/2)) 
        ax.set_zlim3d((0, 1.1*cfg.L))
        fig.tight_layout()

        plotting.plot_fairing(ax)
        plotting.plot_margin_limits(ax)
        # doesnt work
        #ax.set_box_aspect([ub - lb for lb, ub in (getattr(ax, f'get_{a}lim')() for a in 'xyz')])

    # Pass settings
    pass_shift = cfg.pass_shift # shift en degrès à la fin de chaque passe
    ######## current_shift = 0 # Gradually increasing shift

    # make new gcode if need be
    gcode_editor.gcode_clear()

    print(f'=DEBUG= carriage speed : {cfg.carriage_speed} mm/s')
    print(f'=DEBUG= spindle speed : {cfg.spindle_speed} deg/s')
#    print(f'Vtan : {cfg.Vtan} mm/s')


    # halfpass is a list of thetas matching z
    Pstart = [0,0]
    start_theta = 0
    for i in range(cfg.pass_count) :
        start_theta = current_theta
        #print('start theta', start_theta)
        # First halfpass
        #################

        # Relevant coordinates : r, theta, z
        # halfpass = list of halfpass thetas for each slice
        halfpass = get_theta(Lomega)

        # writing Gcode
        gcode_editor.gcode_write_comment(f'Moving hand to FWD position')
        gcode_editor.gcode_write_traj([halfpass[0]], [Lz[0]], [Lr[0]], [Lomega[0]], [cfg.fwd_orient]) # using first coordinates
        gcode_editor.gcode_write_comment(f'Pass {i}, Halfpass no. 1')
        gcode_editor.gcode_write_traj(halfpass, Lz, Lr, Lomega, [cfg.fwd_orient]*len(halfpass))
        #gcode_editor.gcode_write_comment(f'Moving hand to neutral')
        #gcode_editor.gcode_write_traj([halfpass[-1]], [Lz[-1]], [Lr[-1]], [Lomega[-1]], [0]) # using last coordinates

        # plotting halfpass
        plot_x = Lz
        plot_y = Lr*np.cos(halfpass)
        plot_z = Lr*np.sin(halfpass)
        # distance tangentielle parcourue pour un pas en Z
        d_tan = ((np.rad2deg(halfpass[2] - halfpass[1]))*(2*np.pi*cfg.R))/360
        print('=DEBUG= fiber orientation', np.rad2deg(np.arctan(cfg.step/d_tan)))
        plotting.plot_toolpath(plot_x, plot_y, plot_z, ax, i)
        #plotting.plot_toolpath_points(plot_x, plot_y, plot_z, ax, fig, i)
        ax.scatter(plot_y[0], plot_z[0], plot_x[0], color='green', s=50)
        ax.text(plot_y[0], plot_z[0], plot_x[0], f'HP{i}.1 start')
        if i > 0 :
            print('angle entre points de départ :',  get_angle(Pstart, [0,0], [plot_y[0], plot_z[0]]))
        Pstart = [plot_y[0], plot_z[0]]

        ax.scatter(plot_y[-1], plot_z[-1], plot_x[-1], color='red', s=50)
        ax.text(plot_y[-1], plot_z[-1], plot_x[-1], f'HP{i}.1 end')

        #H1end = [plot_y[-1], plot_z[-1]]
       

       # Inter-halfpass stuff
       ##################
        #current_theta += np.deg2rad(360+cfg.halfpass_shift)
        current_theta += np.deg2rad(360+cfg.halfpass_shift)
        
        #gcode_editor.gcode_write_comment(f'Pass {i}, executing halfpass 720 + shift={cfg.halfpass_shift}')
        #gcode_editor.gcode_write_traj([current_theta], [Lz[-1]], [Lr[-1]], [Lomega[-1]], [0])
        gcode_editor.gcode_write_comment(f'Pass {i}, executing halfpass 360 + shift={cfg.halfpass_shift}')
        gcode_editor.gcode_write_traj([current_theta], [Lz[-1]], [Lr[-1]], [Lomega[-1]], [cfg.fwd_orient])
        gcode_editor.gcode_write_comment(f'Moving hand to BWD position')
        gcode_editor.gcode_write_traj([current_theta], [Lz[-1]], [Lr[-1]], [Lomega[-1]], [-cfg.fwd_orient])

        # Return halfpass
        #################

        # Relevant coordinates : TODO

        halfpass = get_theta(Lomega) # not this

        # writing Gcode
        gcode_editor.gcode_write_comment(f'Pass {i}, Halfpass no. 2')
        gcode_editor.gcode_write_traj(halfpass, list(reversed(Lz)), list(reversed(Lr)), Lomega, [-cfg.fwd_orient]*len(halfpass))

        plot_x = list(reversed(Lz)) # reverse this
        plot_y = Lr*np.cos(halfpass)
        plot_z = Lr*np.sin(halfpass)

        plotting.plot_toolpath(plot_x, plot_y, plot_z, ax, i)
#        plotting.plot_toolpath_points(plot_x, plot_y, plot_z, ax, fig, i)
        ax.scatter(plot_y[0], plot_z[0], plot_x[0], color='blue', s=50)
        ax.text(plot_y[0], plot_z[0], plot_x[0], f'HP{i}.2 start')

        # TODO 
        #ax.scatter(plot_y[-1], plot_z[-1], plot_x[-1], color='orange', s=50)
        #ax.text(plot_y[-1], plot_z[-1], plot_x[-1], f'HP{i}.2 end')

        #print('angle entre HP1end et HP2start :',  get_angle(H1end, [0,0], [plot_y[-1], plot_z[-1]]))

        #gcode_editor.gcode_write_comment(f'Moving hand to neutral')
        #gcode_editor.gcode_write_traj([current_theta], [Lz[0]], [Lr[-1]], [Lomega[-1]], [0]) 
        #current_theta += np.deg2rad(360)
        #gcode_editor.gcode_write_comment(f'Pass {i}, executing 360')
        current_theta += np.deg2rad(360)
        gcode_editor.gcode_write_comment(f'Pass {i}, executing 360')
        gcode_editor.gcode_write_traj([current_theta], [Lz[0]], [Lr[-1]], [Lomega[-1]], [-cfg.fwd_orient]) # Lz[0] cause we're at home

        # Preparing next pass
        ######################

        # Shifting for next pass
        #####current_shift += pass_shift
        # Updating theta

#        print('theta avant correction : ', np.rad2deg(current_theta)%360)
#        print('diff angle :', 360 - np.rad2deg(current_theta - start_theta)%360)
        print(f'theta before catch up = {np.rad2deg(current_theta)}')
        catch_up = np.deg2rad(360 -  np.rad2deg(current_theta - start_theta)%360) # catch up with pass starting point
        current_theta += catch_up
        print(f'theta after catch up = {np.rad2deg(current_theta)}')
        print(f'catch_up = {np.rad2deg(catch_up)}')
        current_theta += np.deg2rad(pass_shift) # add shift
        print(f'theta after shift = {np.rad2deg(current_theta)}')
        print(f'pass shift = {pass_shift}')
        gcode_editor.gcode_write_comment(f'Pass {i}, executing catch-up to start point AND pass_shift = {cfg.pass_shift}')
        gcode_editor.gcode_write_traj([current_theta], [Lz[0]], [Lr[-1]], [Lomega[-1]], [0])
        #print('theta après correction : ', np.rad2deg(current_theta)%360)

    plt.axvline(x=cfg.top_margin, color='red', linestyle=':')
    plt.axvline(x=cfg.L, color='red', linestyle=':')

    if cfg.plot_mode == '2d' :
        plt.axis('equal')

    plt.legend()
    plt.grid()

    #ani = matplotlib.animation.FuncAnimation(fig, plotting.toolpath_update, frames=len(plot_x), interval=5)

    print('=INFO= GCode generated successfully !')

    plt.show()
