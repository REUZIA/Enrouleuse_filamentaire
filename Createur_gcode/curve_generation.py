import cfg

import numpy as np

# Von Haack function
def von_haack(z) :
    theta = np.arccos(1-(2*z)/cfg.L)

    expr1 = cfg.R/np.sqrt(np.pi)
    expr2 = theta - (np.sin(2*theta)/2) + cfg.C*(np.sin(theta))**3

    rs = (expr1*np.sqrt(expr2))

    return rs

def cylinder(z) : 
    return cfg.R

# Compute a curve taking top and bottom margins into account
def curve(z) :

    # cast to np types
    if(type(z) == int ) :
        z = np.astype('float')
    if(type(z) == list ) :
        z = np.array(z).astype('float')

    z_conditions = [z < cfg.top_margin, (cfg.top_margin <= z) & (z < cfg.L), z >= cfg.L]
    # for fairing
    #z_func = [von_haack(cfg.top_margin), von_haack, von_haack(cfg.L)]
    # for cylinder
    z_func = [cylinder(cfg.top_margin), cylinder, cylinder(cfg.L)]
    

    # z NEEDS to be a float or an array of floats
    rs = np.piecewise(z, z_conditions, z_func) 

    return rs
