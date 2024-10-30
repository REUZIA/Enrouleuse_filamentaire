import cfg
import curve_generation

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation

def plot_toolpath(plot_x, plot_y, plot_z, ax, pass_id) :
    if(cfg.plot_mode == '2d') :
        '''2D plotting projection of trajectory on 2D plane'''
        plt.plot(plot_x, plot_y, label='pass no. '+str(pass_id)+' fwd')
    else :
        '''3D plotting trajectory'''
        ax.plot3D(plot_y, plot_z, plot_x, label='pass no. '+str(pass_id))
def plot_margin_limits(ax) :

    xs = [-1.2*cfg.R, 1.2*cfg.R]
    ys = [-1.2*cfg.R, 1.2*cfg.R]

    X, Y = np.meshgrid(xs, ys)
    Z_top = Y*0 + cfg.top_margin
    Z_bot = Y*0 + cfg.L

    ax.plot_surface(X, Y, Z_top, color = 'red', shade = True, alpha=.1)
    ax.plot_surface(X, Y, Z_bot, color = 'red', shade = True, alpha=.1)

def plot_fairing(ax) :

    z_max = int(cfg.L + cfg.bot_margin)

    z = np.linspace(0, z_max, int(z_max/cfg.step))
    rho = curve_generation.curve(z)
    #print(rho)
    #print('len rho = ', len(rho))

    #steps around circle from 0 to 2*pi(360degrees)
    #reshape at the end is to be able to use np.dot properly
    # TODO fix that horsecrap, make it so theta step / resolution is independant from z resolution
    revolve_steps = np.linspace(0, np.pi*2, int(z_max/cfg.step)).reshape(1,int(z_max/cfg.step))

    theta = revolve_steps
    #convert rho to a column vector

    rho_column = rho.reshape(int(z_max/cfg.step),1)
    ##print('rho', rho)
    #print('type rho', np.shape(rho))
    ##print('rho_column', rho_column)
    #print('type rho_col', np.shape(rho_column))
    x = rho_column.dot(np.cos(theta))
    y = rho_column.dot(np.sin(theta))

    zs, rs = np.meshgrid(z, rho)
    
    ##plotting
    #fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
    #fig.tight_layout(pad = 0.0)
    #transpose zs or you get a helix not a revolve.
    # you could add rstride = int or cstride = int kwargs to control the mesh density
    #print(len(x))
    #print(len(y))
    #print(len(zs.T))
    ax.plot_surface(x, y, zs.T, color = 'blue', shade = True, alpha=.2)

global px, py, pz, sc

def toolpath_update(i):
    global sc, px, py, pz
    sc._offsets3d = (py[:i], pz[:i], px[:i])

def plot_toolpath_points(plot_x, plot_y, plot_z, ax, fig, pass_id) :
    global px, py, pz, sc
    px = plot_x
    py = plot_y
    pz = plot_z

    sc = ax.scatter([],[],[], c='darkblue', alpha=0.5)

