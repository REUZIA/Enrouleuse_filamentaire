# TODO divide margins by step or something
# TODO check units consistency

# we won't use SI m but mm

#####################
# General notations #
#####################

''' Reference frame
z (mm) : distance from home on main carriage sliding axis
r(z) (mm) : radius of the fairing for a given z
omega(z) : calculated angular speed of the fairing for a given z, 
           such that tangential linear speed remains the same all along the fairing
c(z) (deg) : fairing angle at a given z
'''

import numpy as np
import matplotlib.pyplot as plt

import polar

#global C, L, R # Fairing parameters
#global arbitrary_tan_speed_cst, x_speed, cfg.top_margin, bot_margin, step # Winding parameters


global current_theta
current_theta = 0

def plot_fairing() :

    z_max = int(cfg.top_margin + L + bot_margin)

    z = np.linspace(0, z_max, int(z_max/step))
    rho = curve(z)
    print(len(rho))

    #steps around circle from 0 to 2*pi(360degrees)
    #reshape at the end is to be able to use np.dot properly
    revolve_steps = np.linspace(0, np.pi*2, z_max).reshape(1,z_max)

    theta = revolve_steps
    #convert rho to a column vector
    rho_column = rho.reshape(z_max,1)
    x = rho_column.dot(np.cos(theta))
    y = rho_column.dot(np.sin(theta))

    zs, rs = np.meshgrid(z, rho)

    #plotting
    fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
    fig.tight_layout(pad = 0.0)
    #transpose zs or you get a helix not a revolve.
    # you could add rstride = int or cstride = int kwargs to control the mesh density
    ax.plot_surface(x, y, zs.T, color = 'blue', shade = True)

    ax.set_xlim3d((-(R+.1*R)/2, (R+.1*R)/2)) 
    ax.set_ylim3d((-(R+.1*R)/2, (R+.1*R)/2)) 
    ax.set_zlim3d((0, R+.1*R))

# Von Haack function
def von_haack(z) :
    global C, L, R

    theta = np.arccos(1-(2*z)/L)

    expr1 = R/np.sqrt(np.pi)
    expr2 = theta - (np.sin(2*theta)/2) + C*(np.sin(theta))**3

    rs = (expr1*np.sqrt(expr2))

    return rs

# Compute a curve taking top and bottom margins into account
def curve(z) :
    global C, L, R

    # cast to np types
    if(type(z) == int ) :
        z = np.astype('float')
    if(type(z) == list ) :
        z = np.array(z).astype('float')

    z_conditions = [z < cfg.top_margin, (cfg.top_margin <= z) & (z < L), z >= L]
    z_func = [von_haack(cfg.top_margin), von_haack, von_haack(L)]
    # z NEEDS to be a float or an array of floats
    rs = np.piecewise(z, z_conditions, z_func) 

    return rs

# Returns a list of equally spaced positions for the x axis (values are in mm)
def get_Lz() :
    global arbitrary_tan_speed_cst, cfg.top_margin, bot_margin, step

    Lz = np.concatenate((
        np.arange(1,cfg.top_margin,step), 
        np.arange(cfg.top_margin,L,step),
        np.arange(L,L+bot_margin,step),
        ))

    return np.array(Lz)

def omega(r) :

    return cfg.om_func(r)



# intégrer : ajouter theta(n) + (omega(n) - omega(n-1))
def get_theta(Lomega) :
    global current_theta

    print(np.rad2deg(current_theta))

    theta = current_theta
    Ltheta = []
    for omega in Lomega :
        Ltheta.append(theta)
        theta += omega*step

    current_theta = Ltheta[-1]
        
    return np.array(Ltheta)

if __name__ == '__main__':
    # Get a list of z according to the step
    Lz = get_Lz()
    # Get a list of radii matching each z
    Lr = curve(Lz)

    # Get inverted values for return pass
    LzRev = list(reversed(Lz)) 
    LrRev = list(reversed(Lz)) 

    plot = '3d'

    if(plot == '2d') :
        '''2D plotting fairing curve'''
        plt.plot(Lz, Lr, label='r(mm)')

    # Get spindle angular speed
    Lomega = omega(Lr)

    if(plot == '2d') :
        '''2D plotting angular speed'''
        plt.plot(Lz, Lomega*3000, label='ω(x) (rad/s)')

    else :
        '''3D preparing plot'''
        ax = plt.axes(projection='3d')
        ax.set_xlim3d((-(L+.1*L)/2, (L+.1*L)/2)) 
        ax.set_ylim3d((-(L+.1*L)/2, (L+.1*L)/2)) 
        ax.set_zlim3d((0, L+.1*L))

        plot_fairing()
        # doesnt work
        #ax.set_box_aspect([ub - lb for lb, ub in (getattr(ax, f'get_{a}lim')() for a in 'xyz')])

    #    xs = np.linspace(-100, 100)
    #    ys = np.linspace(-100, 100)
    #    X, Y = np.meshgrid(xs, ys)
    #    Z = cfg.top_margin
    #    ax.plot_surface(X, Y, Z)


    # Pass settings
    pass_shift = 10 # shift en degrès à la fin de chaque passe
    ######## current_shift = 0 # Gradually increasing shift

    # halfpass is a list of thetas matching z
    for i in range(1) :
        # First halfpass
        #################

        # Relevant coordinates : r, theta, z
        halfpass = get_theta(Lomega)
        plot_x = Lz
        plot_y = Lr*np.cos(halfpass)
        plot_z = Lr*np.sin(halfpass)
        
        if(plot == '2d') :
            '''2D plotting projection of trajectory on 2D plane'''
            plt.plot(plot_x, plot_y, label='pass no. '+str(i)+' fwd')
        else :
            '''3D plotting trajectory'''
            ax.plot3D(plot_y, plot_z, plot_x, label='pass no. '+str(i)+' fwd')
       
        current_theta += np.deg2rad(360+180)

        # Return halfpass
        #################

        # Relevant coordinates : TODO
        halfpass = list(reversed(get_theta(Lomega)))
        plot_x = Lz
        plot_y = Lr*np.cos(halfpass)
        plot_z = Lr*np.sin(halfpass)

        if(plot == '2d') :
            '''2D plotting projection of trajectory on 2D plane'''
            plt.plot(plot_x, plot_y, label='pass no. '+str(i)+' fwd')
        else :
            '''3D plotting trajectory'''
            ax.plot3D(plot_y, plot_z, plot_x, label='pass no. '+str(i)+' fwd')

        current_theta += np.deg2rad(360)

        # Preparing next pass
        ######################

        # Shifting for next pass
        #####current_shift += pass_shift
        # Updating theta
        current_theta += np.deg2rad(pass_shift)

    plt.axvline(x=cfg.top_margin, color='red', linestyle=':')
    plt.axvline(x=L, color='red', linestyle=':')

    #plt.axis('equal')
    plt.legend()
    plt.grid()

    plt.show()

    # Returns list of angular speeds for the spindle (basicaly ω(x) in rad/s) for each x
    def get_Lomega(Lr, arbitrary_tan_speed_cst) : # TODO c'est omega(t), pas de x ; arbitrary_tan_speed_cst(t) = a*arbitrary_tan_speed_cst(x) 
    # on veut omega(x(t))
        return arbitrary_tan_speed_cst / Lr 

    ## Returns a list of angles matching the equally spaced x-es (rad)
    #def get_Ltheta(Lomega) : # TODO c'est aussi fonction de t, pas de x
    #
    #    theta = 0
    #    Ltheta = []
    #    for omega in Lomega :
    #        Ltheta.append(theta)
    #        theta += omega
    #        
    #    return np.array(Ltheta)
    #
    #
    #
    ## rapport entre x et t à inejcter dans 
    #
    #Lz = get_Lz(arbitrary_tan_speed_cst, cfg.top_margin, bot_margin, step, L)
    #Lr = get_Lr(Lz, C, L, R, cfg.top_margin, bot_margin)
    #Lomega = get_Lomega(Lr, arbitrary_tan_speed_cst)
    #Ltheta = get_Ltheta(Lomega)
    #
    #plt.plot(Lz, Lr, label='C = '+str(C)+', y(x) = R(x) (mm)', color='blue')
    #plt.plot(Lz, Lomega, label='C = '+str(C)+', ω(x) (rad/s)', color='green')
    ##plt.plot(Lz, Ltheta, label='C = '+str(C)+', θ(x) (deg)', color='purple')
    #plt.plot(Lz, Lr*np.cos(Ltheta))
    #
    ##step = .001
    ##Lz_acc = np.concatenate((
    ##    np.arange(1,cfg.top_margin,step), 
    ##    np.arange(cfg.top_margin,L,step),
    ##    np.arange(L,L+bot_margin,step),
    ##))
    ##
    ##Lproj_acc = np.interp(Lz_acc, Lz, Lr*np.cos(Ltheta))
    ##
    ##plt.plot(Lz_acc, Lproj_acc)
    #
    #
    #
    #
    #plt.axvline(x=cfg.top_margin, color='red')
    #plt.axvline(x=L, color='red')
    #plt.grid()
    #
    #plt.axis('equal')
    #plt.legend()
    #plt.show()
    #
    #
    #
    #
    #
    ## structure de la commande :
    #
