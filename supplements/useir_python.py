from scipy.stats import gamma
# import matplotlib
# import matplotlib.pyplot as plt
# matplotlib.use('Agg')
# from matplotlib.pyplot import imshow
# plt.rcParams["figure.figsize"] = 10, 8
# plt.rcParams["font.size"     ] = 14
# plt.rcParams['savefig.format'] = 'png'
import numpy as np
import pandas as pd


# def plot_useir(dfs, lbls, T = 'uSEIR', figsize=(10,10)):
#     
#     fig = plt.figure(figsize=figsize)
#     
#     ax=plt.subplot(1,2,1)
#     for i, df in enumerate(dfs):
#         df.head()
#         ls = f'S-{lbls[i]}'
#         lr = f'R-{lbls[i]}'
#         plt.plot(df.t, df.S, lw=2, label=ls)
#         plt.plot(df.t, df.R, lw=2, label=lr)
# 
# 
#     plt.xlabel('time (days)')
#     plt.ylabel('Fraction of population')
#     plt.legend()
#     plt.title(T)
#     
#     ax=plt.subplot(1,2,2)
#     for i, df in enumerate(dfs):
#         le = f'E-{lbls[i]}'
#         li = f'I-{lbls[i]}'
#         plt.plot(df.t, df.E, lw=2, label=le)
#         plt.plot(df.t, df.I, lw=2, label=li)
# 
#     plt.xlabel('time (days)')
#     plt.ylabel('Fraction of population')
#     plt.legend()
#     
#     plt.title(T)
#     plt.tight_layout()
#     plt.show()

def solve_uSeir(ti_shape     = 5.5,  
                   ti_scale     = 1, 
                   tr_shape     = 6.5,  
                   tr_scale     = 1,
                   R0           = 3.5):
    """
    The pure python version only uses the gamma distribution and fine grain.
    It's sole purpose is benchmarking the cython version
    """
    
    # This function is similar to calcTransitionProb in denim
    def compute_gamma_pde(t_shape, t_scale, eps, tol):
        # compute dwell time steps unit
        ne = int(gamma.ppf(tol, a=t_shape, scale=t_scale) / eps)
        # transition rate per timestep 
        pdE = np.zeros(ne)
        cd1 = 0
        for i in np.arange(ne):
            # equivalent to computing sum(pi_i) in denim
            cd2    = gamma.cdf(i*eps, a=t_shape, scale=t_scale)
            pdE[i] = cd2-cd1 # equivalent compute current transition prob in denim
            cd1    = cd2
        
        # return values
        # ne: equivalent of dwell time in time steps
        # pdE: equivalent to p_i in denim paper
        return ne, pdE

    N       = 1e+6
    Smin    = 1e-10 
    Emin    = 1e-10
    nmax    = 21000 # max time steps
    eps     = 0.01
    tr = tr_shape*tr_scale
    prob    = R0 / tr 
    pn      = prob * eps
    tol     = 0.9999 # similar to the error tolerance in denim

    nE, pdE = compute_gamma_pde(ti_shape, ti_scale, eps, tol)
    nI, pdI = compute_gamma_pde(tr_shape, tr_scale, eps, tol)

    print(f' Function solve_uSeir: time epsilon = {eps}')
    print(f' statistical distribution is Gamma , ti = {ti_shape*ti_scale}, tr = {tr_shape*tr_scale}')
    print(f' number of exposed compartments = {nE}, infected compartments = {nI}')
    print(f' R0 = {R0}, prob = {prob}, pn = {pn}')
     
    I   = np.zeros(nI)
    E   = np.zeros(nE)
    S    = 1 - 1/N
    E[0] = 1 / N
    
    R    = 0
    sI   = 0

    TT = []
    SS = []
    EE = []
    II = []
    RR = []
    n    = 0
    
    while True:
        
        # update R compartment  
        # I[0] here is equivalent to population that will move to R at t + 0 (i.e. current time step) 
        R += I[0]

        # ----- Simulate for S-I first -----
        end = nI - 1 # compute dwell time
        # update population for I_k where I_k is the population that will move to R at time t + k (in time step)
        for k in np.arange(end):
            I[k] = I[k+1] + pdI[k] * E[0] 
            # pdI[k] * E[0] is just contact rate
            # where I[k+1] is value computed from previous timestep (i.e. shift I[k+1] from old iteration to I[k] in current iteration)
        I[end] = pdI[end] * E[0]
        
        #print(I)

        # ----- Simulate I-E transition -----
        end = nE - 1
        for k in np.arange(end):
            E[k] = E[k+1] + pn * pdE[k] * sI * S
        E[end]   = pn * pdE[end] * sI * S

        #print(E)
        
        # pn * sI * S equivalent to probs * epsilon * S * I/N
        S  = S - pn * sI * S
        
        sI = np.sum(I)
        sE = np.sum(E)
        
        #print(sI)
        #print(sE)
        TT.append(n * eps)
        SS.append(S)
        EE.append(sE)
        II.append(sI)
        RR.append(R)
        
        #print(f't = {n*eps} S = {S} E ={sE} I ={sI} R = {R}')
        n+=1
        if (sE < Smin and sI < Emin) or n > nmax:
            break
    
    df = pd.DataFrame(list(zip(TT, SS, EE, II, RR)), 
               columns =['t', 'S', 'E', 'I', 'R']) 
    
    return df
