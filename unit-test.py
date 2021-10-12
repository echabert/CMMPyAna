import fitter as fit
import statistics as stat
import numpy as np
import matplotlib.pyplot as plt

###############################
# test the surface fit: fitv2
# plane equation: ax+by+cz = d
# generate pseudo values
# solution should be exact 
# (except numerical effect)
###############################

# option: z,y or z to generate specific plan and check angles
# option: random to generate random planes (angles invalid)
def test_fitv2(npseudo = 10, option='z',plot = True):

    #range of parameters a,b,c
    pmean = 0
    psigma = 100
    #range for nb points per plane
    npmin = 3
    npmax = 20
    #range for coord in the plane
    cmean = 0
    csigma = 1000

    a = np.zeros(npseudo)
    b = np.zeros(npseudo)
    c = np.zeros(npseudo)
    d = np.random.default_rng().normal(pmean,psigma,npseudo)

    if option=='random':
        a = np.random.default_rng().normal(pmean,psigma,npseudo)
        b = np.random.default_rng().normal(pmean,psigma,npseudo)
        c = np.random.default_rng().normal(pmean,psigma,npseudo)
    if option=='x':
        a = np.ones(npseudo)
    if option=='y':
        b = np.ones(npseudo)
    if option=='z':
        c = np.ones(npseudo)

    # generate random npoints per plane
    npoints = np.random.default_rng().uniform(3,20,npseudo)
    npoints = [int(i) for i in npoints]

    #results
    angles = []
    residuals = []
    for exp in range(npseudo):
        for i in npoints:
            # generate x,y,z coordinate
            x = np.zeros(i)
            y = np.zeros(i)
            z = np.zeros(i)
            if option=='x':
                y = np.random.default_rng().normal(cmean,csigma,i)
                z = np.random.default_rng().normal(cmean,csigma,i)
                # x calculated from the plane equation
                #x = (b[exp]*y+c[exp]*z-d[exp])/(-a[exp])
                x = np.ones(i)
            if option=='y':
                x = np.random.default_rng().normal(cmean,csigma,i)
                z = np.random.default_rng().normal(cmean,csigma,i)
                # z calculated from the plane equation
                #y = (a[exp]*x+c[exp]*z-d[exp])/(-b[exp])
                y = np.ones(i)
            if option=='z' or option=='random':
                x = np.random.default_rng().normal(cmean,csigma,i)
                y = np.random.default_rng().normal(cmean,csigma,i)
                # z calculated from the plane equation
                z = (a[exp]*x+b[exp]*y-d[exp])/(-c[exp])
            points = zip(x,y,z)
            points = [list(i) for i in points]
            points = np.array(points)
            #print(points)
            #Fitter(points, "", plan='z')
            axis = 'z' if option == 'random' else option
            angle, residual = fit.fitv2(points, axis, False)
            angles.append(angle)
            residuals.append(residual)
            #print(angle,residual)
    #print (angles)
    #print(residuals)

    if plot:
        fig, axs = plt.subplots(1, 2, tight_layout=True)
        axs[0].hist(angles,bins = 10)
        axs[0].set_title("angles")
        axs[1].hist(residuals,bins = 10)
        axs[1].set_title("residuals")
        plt.show()
    mean_angles = stat.mean(angles)
    mean_residuals = stat.mean(residuals)
    print("mean angles:",mean_angles)
    print("mean residual:", mean_residuals)
    
    if mean_angles<1 and mean_residuals<1e-5: return True
    return False


if __name__ == "__main__":
    #test_fitv2(100,'x',True)
    #test_fitv2(100,'y',True)
    test_fitv2(100,'z',True)
