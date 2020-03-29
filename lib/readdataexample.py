import os
import sys
import datetime

import numpy as np



#Example of reading data. Hospitalized patients in DK.


# Initiation
#Path to lib folder
libpath = os.path.realpath(__file__).split("plotter.")[0] + os.sep

#Path to data folder
datap = libpath.split("lib")[0]+ os.sep  + "data DK" + os.sep



#List for reading data
hosp = [] # Hospitalized
yearday = [] #Day of year


with open(datap +  "hosp.txt",'r') as f: # Open file
    for i,l in enumerate(f.readlines()): # Loop file
        if i == 0:
            pass #Header - skip it
        else:

            data = l.split(";") #Split line using ";" delimiter
            hosp.append(int(data[0])) # Append datapoint to list

            #Get date for x axis
            y = int(data[1][:4])
            m = int(data[1][4:6])
            d = int(data[1][6:8])

            mydate = datetime.datetime(y, m, d, 12, 00, 00)
            dayofyear = mydate.timetuple().tm_yday
            yearday.append(dayofyear)




#convert to Numpy
hosp = np.array(hosp)
yearday = np.array(yearday)




print(hosp,yearday)
