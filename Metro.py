import fitter
import numpy as np

##################################################################################
#  Goal: compute angle and planarity of 3 planes of inserts 
#  12 modules/ladder
#  5-6 inserts/module
#  3 planes /inserts
#  3-6 points per plane
#
# To-do:
#  - config file to choice input files
#  - choose list of modules
#  - choose granularity
#  - create a debug option
##################################################################################


##################################################################################
# extract a coordinate (distance to gabarit plane) from the result file - y coord
#   return None if not found
# resfilename: input file name
# point: string indicating the formatted searched point
##################################################################################
def getMeasure(resfilename,point):
        resfile = open(resfilename,encoding="ISO-8859-1")
        content = resfile.read()
        #modification of content due to missing space
        content = content.replace("Xmoy","Xmo")
        content = content.replace("Xmo","Xmo ")
        content = content.replace("Zmoy.","Zmoy")
        content = content.replace("Zmoy","Zmoy ")
        # new modifications
        content = content.replace("Ymoy.","Ymoy")
        content = content.replace("Ymoy","Ymoy ")
        lines = content.split('\n')
        out = [lines[lines.index(line)+1] for line in lines if line.find(point)>0]
        measure = None
        if len(out)==1:
            measure = float(out[0].split()[2])
        return measure

##################################################################################
# extract coordinates of a point from the dmi files
#   return an empty list if not found
# dmifilename: input file name
# point: string indicating the fomatted searched point
##################################################################################
def getCoordFromDmi(dmifilename,point):
        dmifile = open(dmifilename,encoding="ISO-8859-1")
        content = dmifile.read()
        lines = content.split('\n')
        out = [lines[lines.index(line)+3] for line in lines if (line.find(point)>0 and line.find("MEAS_POINT")>0)]
        measures = []
        if len(out)==1:
            measures.append(float(out[0].split(',')[1]))
            measures.append(float(out[0].split(',')[2]))
            measures.append(float(out[0].split(',')[3]))
        #print(measures)
        return measures

# filenames 
# NB: could be configured later one
#resfilename = "python_test.RES"
#dmifilename = "python_test.dmi"
#resfilename = "Proto2/proto2-v3.RES"
#resfilename = "Proto2/proto2-v2.RES"
#dmifilename = "Proto2/proto2.dmi"
resfilename = "Proto2/proto2-v4.res"
dmifilename = "Proto2/proto2-v4.dmi"


#print(getCoordFromDmi(dmifilename,"E02F5"))

#coord = getCoordFromDmi(dmifilename,"PNTA02F2")
#ymeas = getMeasure(resfilename,"PNTA02F2")
#print(coord,ymeas)

#letters used to define an insert on the module
#letters=["A","B","C","D","E"]
letters=["A","B","C","D","E"]
#letters=["A","C","D","E"]

#numbers used to define a module on the ladder
numbers=["02","04","06","08","10"]
#numbers=["01","02","03","04","05","06","07","08","09","10","11"]
#pb with 04S and 06S, 08S, 10S
#pb B02E

#position used to define a serie of point passing by a plane of the insert
positions={"F":(5,"y"),"H":(6,"y"),"S":(3,"x"),"E":(3,"z")}
#positions={"F":(5,"y"),"H":(6,"y")}
#positions={"F":(5,"y"),"H":(6,"y")}
#positions={"H":(6,"y"),"S":(3,"x"),"E":(3,"z")}
#positions={"S":(3,"x"),"H":(6,"y"),"E":(3,"z")}
#positions={"F":(5,"y"),"H":(6,"y"),"S":(3,"x")}

excluded = """
A03F5
A05F1
A05F5
B03F2
B03F3
B03H2
B03H3
C01F2
C03F1
C05F1
E03H2
E03H3
E03F1
E03F2
E03F3
E03F4
E03F5
"""
excluded = ["PNT"+i for i in excluded.split()]

# format of point
point="PNT{letter}{number}{position}"
# format of insert
insert="{letter}{number}{plane}"

# output files
ofileInsert = open("reportInserts.csv","w")
ofileModule = open("reportModule.csv","w")
ofilePoints = open("points.csv","w")

ofileInsert.write("label,angle,planeity\n")
ofileModule.write("label,angle,planeity\n")
ofilePoints.write("letter,module,face,x,y,z\n")


fitModule = True #True
verbosity = 1

######################################
# loops over all points of interest
######################################
for nb in numbers: #define a module
    insertBary = [] #compute an observed geometrical barycenter per F-plane of inserts
    for l in letters: #define an insert on the module
        for position in positions: #define a plane on the insert
            points=[]
            for el in range(1,positions[position][0]+1):
                 #p = point.format(letter="A",number="02",position="F"+str(el))
                 p = point.format(letter=l,number=nb,position=position+str(el))
                 if p  in excluded: 
                     if verbosity>0: print("excluded: ",p)
                     continue
                 if verbosity>3: print("p = ",p)
                 #points.append(point.format(letter="A",number="01",position="F"+str(el)))
                 coord = getCoordFromDmi(dmifilename,p)
                 meas = getMeasure(resfilename,p)
                 if verbosity>3: print(p,coord,meas,positions[position][1])
                 if coord and meas: 
                     if positions[position][1]=='x': points.append([meas,coord[1],coord[2]])
                     if positions[position][1]=='y': points.append([coord[0],meas,coord[2]])
                     if positions[position][1]=='z': points.append([coord[0],coord[1],meas])
                     if verbosity>2: print(points)
                     if verbosity>2: print(position+str(el))
                     out = f"{l},{str(int(nb))},{position+str(el)},{points[-1][0]},{points[-1][1]},{points[-1][2]}\n"
                     #out=l+str(int(nb))
                     ofilePoints.write(out)
                 #points.append([coord[0],coord[2],ymeas])

            if verbosity>2: print("points",l,position,points)

            if len(points)>0:
                display = False
                if position=="H":
                    if verbosity>2: print ("bary",l,position)
                    #display = True
                    #points.append(fitter.Barycenter(points))
                    insertBary.append(fitter.Barycenter(points))
                #fitter.Fitter(points,p,insert.format(letter=l,number=nb,position=position),True, ofile)
                axis = positions[position][1]
                label = insert.format(letter=l,number=nb,plane=position)
                #print(label)
                #require at least 3 points to constrain a plane
                if len(points)>3:
                   fitter.Fitter(points, label, axis, True, ofileInsert, display)
                #fitter.Fitter(points,p,positions[position][1],True, ofile)
                yval = np.array([p[1] for p in points])
                if verbosity>2: print(yval.mean(), yval.std(),yval.max()-yval.min())

    # Perform fit for all inserts in a module based on barycenters of measured points
    if verbosity>2: print(insertBary)
    if fitModule:
        # bug fix: it has to be the 'y'-axis (not the z-axis)
        fitter.Fitter(insertBary, l+nb, 'y', True, ofileModule, False, verbosity=1)



