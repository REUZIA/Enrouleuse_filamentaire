from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

def plot_fairing() :

    z_max = top_margin + L + bot_margin

    z = np.linspace(0, z_max, z_max/step)
    rho = test.curve(z)

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
