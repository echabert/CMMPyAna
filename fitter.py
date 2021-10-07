import numpy as np
import scipy.optimize
import math as m

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


############################################
# Compute the geometrical barycenter
# of 3D points (list of [x,y,z])
# NB: still to be tested
############################################


def Barycenter(points):
    npts = len(points)
    if npts == 0: return None
    xg = sum(p[0] for p in points)/npts
    yg = sum(p[1] for p in points)/npts
    zg = sum(p[2] for p in points)/npts
    return [xg,yg,zg]


############################################
# Function to find distance 
# point = coordinate of point in 3D space [x,y,z]
# plane = plane coordinate [a,b,c,d]
# ref https://www.geeksforgeeks.org/distance-between-a-point-and-a-plane-in-3-d/
# NB: still to be validated
############################################
def PointPlaneDistance(point, plane):
    d = abs((plane[0] * point[0] + plane[1] * point[1] + plane[2] * point[2] + plane[3]))  
    nn = m.sqrt(sum(i**2 for i in plane[:-1]))
    return d/nn

############################################
# Function to find distance 
# NB: still to be validated
############################################
def PPD(point, plane):
    return (point[1]*plane[1]+point[2]*plane[2]+plane[3]-point[0])


############################################
# Function to fit a plane with a list of points
# based on least square method
# NB: issues observed - deprecated
############################################
def fitPlaneLTSQ(XYZ, verbosity = 0):
    (rows, cols) = XYZ.shape
    G = np.ones((rows, 3))
    #G[:, 0] = XYZ[:, 0]  #X
    #G[:, 1] = XYZ[:, 1]  #Y
    #Z = XYZ[:, 2]
    G[:, 0] = XYZ[:, 1]  #Y
    G[:, 1] = XYZ[:, 2]  #Z
    X = XYZ[:, 0]
    #(a, b, d),resid,rank,s = np.linalg.lstsq(G, Z)
    (b, c, d),resid,rank,s = np.linalg.lstsq(G, X,rcond=None)
    #plane = (a,b,0,d)
    plane = (0,b,c,d)
    if verbosity > 0: print("Plane coord: ",plane)
    distances = []
    for point in XYZ:
        #distances.append(PointPlaneDistance(point,plane))
        distances.append(PPD(point,plane))
    if verbosity > 1: print ("Distances: ",distances)
    #print(a,b,d,resid,rank,s)
    angles = [m.atan(abs(b)), m.atan(abs(c))]
    if verbosity > 2: 
        print("Angles (radians): ", angles)
        print("Angles (degrees): ", str([m.degrees(a) for a in angles]))
    #normal = (a, b, -1)
    #normal = (-1, a, b)
    normal = (-1, b, c)
    #normal = (-1, b, c)
    nn = np.linalg.norm(normal)
    normal = normal / nn
    #return (d, normal)
    return plane, angles, distances, normal


################################################
# Function to fit a plane with a list of points
# data: np.array of points (list of [x,y,z])
# plan: reference plane ('x','y' or 'z')
#   --> used for angle computation
# display: (True/False) - use to generate histos
# verbosity: (0,1) - print messages
# NB: validation ongoing
#     still issues with the angle computation
################################################
def fitv2(data, plan, display, verbosity=0):
    #retrieve coordinates from data
    xs = data[:, 0]
    ys = data[:, 1]
    zs = data[:, 2]
    
    # plot raw data
    if display:
        plt.figure()
        ax = plt.subplot(111, projection='3d')
        ax.scatter(xs, ys, zs, color='b')

    # do fit
    tmp_A = []
    tmp_b = []
    for i in range(len(xs)):
        #LAST CHANGES _ ERIC - TEST
        if plan=='x':
            tmp_A.append([1, ys[i], zs[i]])
            tmp_b.append(xs[i])
        if plan=='y':
            tmp_A.append([xs[i], 1, zs[i]])
            tmp_b.append(ys[i])
        if plan=='z':
            tmp_A.append([xs[i], ys[i], 1])
            tmp_b.append(zs[i])
    b = np.matrix(tmp_b).T
    A = np.matrix(tmp_A)
    """
    print(b)
    print(A)
    print("A.T")
    print((A.T*A))
    print("done")
    """
    fit = (A.T * A).I * A.T * b
    errors = b - A * fit
    residual = np.linalg.norm(errors)

    #from https://stackoverflow.com/questions/1400213/3d-least-squares-plane
    if verbosity>0:
        print("solution:")
        print ("%f x + %f y + %f = z" % (fit[0], fit[1], fit[2]))
    #trial to get fit[0]x+fit[1]y+fit[2]=constant
    #fit[2]=-1
    param = fit[:]
    ## Correction
    #param[2]=-1
    param[2]=-param[2]
    #norm = m.sqrt(fit[0]**2+fit[1]**2+fit[2]**2)
    norm = m.sqrt(param[0]**2+param[1]**2+param[2]**2)
    # the computation of the angle depends on the reference plane which is caracterized by its vector normal to it
    indices = {'x':0,'y':1,'z':2}
    angle = m.degrees(m.acos(param[indices.get(plan,2)]/norm))
    if abs(angle-180)<angle: angle = angle-180
    if verbosity>0:
        print("3-D angle to horizontal plan {:.3f}".format(angle))
        #angle1 = 
        print ("errors:")
        print (errors)
        print ("residual:")
        print (residual)
    #angles = [m.atan(abs(b)), m.atan(abs(c))]
    #if verbosity > 2: 
    #    print("Angles (radians): ", angles)

    # plot plane
    if display:
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        X,Y = np.meshgrid(np.arange(xlim[0], xlim[1]),
                          np.arange(ylim[0], ylim[1]))
        Z = np.zeros(X.shape)
        for r in range(X.shape[0]):
            for c in range(X.shape[1]):
                Z[r,c] = fit[0] * X[r,c] + fit[1] * Y[r,c] + fit[2]
        ax.plot_wireframe(X,Y,Z, color='k')

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        plt.show()

    return angle, residual


#######################################################
# Perform a fit of all points with a plane 
#  label is a descriptif of the plane (module, face)
#  points are a collections of [x,y,z]
#  plan refer to the vector normal to the reference plane
#######################################################

def Fitter(points, label, plan='z', report=False, ofile = None, display=False,verbosity=3):
    print("##########################")
    print("### Report for module",label)
    print("##########################")

    #data transformation
    data = np.array(points)
    ##########################
    # perform the fit
    ##########################
    #c, normal = fitPlaneLTSQ(data)
    #plane, angles, distances, normal = fitPlaneLTSQ(data, verbosity)
    angle, residual = fitv2(data, plan, display)

    #planarity
    """
    planarity = max([abs(a) for a in distances])
    planarity_2 = max(distances)-min(distances)
    pout = data[distances.index(max(distances))]
    print("Planarity = ", planarity)
    print("--> driven by point :", pout)
    print("Planarity(2) = ", planarity_2)
    if report:
        ofile.write("##########################\n")
        ofile.write("### Report for module "+label+"\n")
        ofile.write("##########################\n")
        ofile.write("Planarity = "+str(planarity)+"\n")
        ofile.write("Planarity(2) = "+str(planarity_2)+"\n")
        ofile.write("Angles = "+str([m.degrees(a) for a in angles])+"\n")
    """
    if report:
        """
        ofile.write("##########################\n")
        ofile.write("### Report for module "+label+"\n")
        ofile.write("##########################\n")
        ofile.write("Angle = {:.3f}\n".format(angle))
        ofile.write("Residual = {:.4f}\n".format(residual))
        """
        ofile.write(label+",")
        ofile.write("{:.5f},".format(angle))
        ofile.write("{:.5f}\n".format(residual))

    #determine the angles
    #xvec = [1,0,0]
    #yvec = [0,1,0]
    #zvec = [0,0,1]
    #np.dot()

    ##########################
    # prepare the display
    ##########################
    """
    if display:
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        # plot fitted plane
        maxx = np.max(data[:,0])
        maxy = np.max(data[:,1])
        maxz = np.max(data[:,2])
        minx = np.min(data[:,0])
        miny = np.min(data[:,1])
        minz = np.min(data[:,2])

        point = np.array([0.0, 0.0, plane[3]])
        d = -point.dot(normal)


        # plot original points
        ax.scatter(data[:, 0], data[:, 1], data[:, 2])

        # compute needed points for plane plotting
        #xx, yy = np.meshgrid([minx, maxx], [miny, maxy])
        yy, zz = np.meshgrid([miny, maxy], [minz, maxz])
        #z = (-normal[0]*xx - normal[1]*yy - d)*1. / normal[2]
        xx = (plane[1]*yy + plane[2]*zz + plane[3])

        # plot plane
        ax.plot_surface(xx, yy, zz, alpha=0.2)

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        plt.show()
      """
