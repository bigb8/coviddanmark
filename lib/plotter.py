import os, sys,datetime

import numpy as np
# import scipy.special
from scipy.optimize import curve_fit




from bokeh.layouts import gridplot
from bokeh.plotting import figure, output_file, show,save
from bokeh.models import SingleIntervalTicker, LinearAxis,Range1d

#Path to lib folder
libpath = os.path.realpath(__file__).split("plotter.")[0] + os.sep

#Path to data folder
datap = libpath.split("lib")[0]+ os.sep  + "data DK" + os.sep

# import data
global hosp,ita,resp,deaths,week,weekday,yearday

hosp = []
ita = []
resp = []
deaths = []

week = []
weekday = []
yearday = []

def sigmoid(x, L ,x0, k, b):
    y = L / (1 + np.exp(-k*(x-x0)))+b
    return (y)

def expfunc(x, a, b, c):
    return a * np.exp(-b * x) + c


numbers = {"ita":ita,"hosp": hosp,"resp":resp,"deaths":deaths}
colorshex = {"ita":"#FF847c","hosp": "#FECEA8","resp":"#E84A5F","deaths":"#2A363B"}

def getdata(fileofinterest,getweek):
    global hosp,ita,resp,deaths,week,weekday,numbers,yearday

    with open(datap + fileofinterest + ".txt",'r') as f:
        for i,l in enumerate(f.readlines()):

            if i == 0:
                pass #Header
            else:
                data = l.split(";")
                numbers[fileofinterest].append(int(data[0]))

                #run only if requested
                if getweek:
                    week.append(int(data[3]))
                    weekday.append(float(data[3]+"."+data[4]))
                    # mydatetime_unix.append()

                    y = int(data[1][:4])
                    m = int(data[1][4:6])
                    d = int(data[1][6:8])

                    # print(y,m,d,data[1],data[1][7:8])
                    mydate = datetime.datetime(y, m, d, 12, 00, 00)
                    dayofyear = mydate.timetuple().tm_yday
                    yearday.append(dayofyear)



getdata("ita",False)
getdata("hosp",True)
getdata("resp",False)
getdata("deaths",False)


#Conversion to numpy
ita = np.array(ita)
hosp = np.array(hosp)
resp = np.array(resp)
deaths = np.array(deaths)
weekday = np.array(weekday)
yearday = np.array(yearday)

maxy = np.max(hosp) + 25

##
tickdict = {70: '10.3', 77: '17.3', 84: '23.3', 91: '30.3'}



##
p = figure(title="Antal indlagte på intensiv - COVID19", tools='', background_fill_color="#fafafa")
output_file('ita.html', title="Intensiv DK")
p.quad(top=ita, bottom=0, left=yearday -.2, right=yearday+.2,fill_color=colorshex["ita"], line_color="white", alpha=1)

p.xaxis.axis_label = 'Dato'
p.yaxis.axis_label = 'Antal'
p.xaxis.ticker =  SingleIntervalTicker(interval=.1, num_minor_ticks=0)
p.y_range=Range1d(0, maxy)

save(p)


xdata = (yearday - yearday[0]) + .1
ydata = hosp

p0 = [max(ydata), np.median(xdata),1,min(ydata)] # this is an mandatory initial guess
popt, pcov = curve_fit(sigmoid, xdata, ydata,p0, method='dogbox')
poptexp, pcovexp = curve_fit(expfunc, xdata, ydata,method='dogbox')

# popt, pcov = curve_fit(sigmoid, weekday, hosp, method='dogbox')

print(popt,pcov)

fakex = np.linspace(0,np.max(xdata) - xdata[0] + 3,150) #week 1. 16.3.2020. Fremskriver seneste situation med 3 dage

y = sigmoid(fakex, *popt)
yexp = expfunc(fakex,*poptexp)

p1 = figure(title="Antal indlagte - COVID19", tools='', background_fill_color="#fafafa")
output_file('hosp.html', title="Indlagte DK")
# p1.quad(top=hosp, bottom=0, left=weekday -.015, right=weekday+.015,fill_color=colorshex["hosp"], line_color="white", alpha=1)

p1.quad(top=hosp, bottom=0, left=yearday -.2, right=yearday+.2,fill_color=colorshex["hosp"], line_color="white", alpha=1)


p1.line(fakex+yearday[0],y,line_color="#59c25d", line_width=2, alpha=0.7, legend_label="Sigmoid fit")
p1.line(fakex+yearday[0],yexp,line_color="#ff8888", line_width=4, alpha=0.7, legend_label="Exponentielt fit")


p1.xaxis.axis_label = 'Dato'
p1.yaxis.axis_label = 'Antal'
p1.xaxis.ticker =  SingleIntervalTicker(interval=7, num_minor_ticks=7)
p1.y_range=Range1d(0, np.max(y)+50)
p1.legend.location = 'top_left'
p1.xaxis.major_label_overrides =tickdict
save(p1)


p2 = figure(title="Antal i respirator - COVID19", tools='', background_fill_color="#fafafa")
output_file('resp.html', title="i respirator DK")
p2.quad(top=resp, bottom=0, left=yearday -.2, right=yearday+.2,fill_color=colorshex["resp"], line_color="white", alpha=1)

p2.xaxis.axis_label = 'Dato'
p2.yaxis.axis_label = 'Antal'
p2.xaxis.ticker =  SingleIntervalTicker(interval=7, num_minor_ticks=7)
p2.y_range=Range1d(0, maxy)
p2.xaxis.major_label_overrides =tickdict

save(p2)



p3 = figure(title="Antal døde - COVID19", tools='', background_fill_color="#fafafa")
output_file('deaths.html', title="Døde DK")
p3.quad(top=deaths, bottom=0, left=yearday -.2, right=yearday+.2,fill_color=colorshex["deaths"], line_color="white", alpha=1)

p3.xaxis.axis_label = 'Dato'
p3.yaxis.axis_label = 'Antal'
p3.xaxis.ticker =  SingleIntervalTicker(interval=7, num_minor_ticks=7)
p3.y_range=Range1d(0, maxy)
p3.xaxis.major_label_overrides =tickdict

save(p3)

p4 = figure(title="Oversigt indlagte - COVID19", tools='', background_fill_color="#fafafa")
output_file('stacked.html', title="Oversigt DK")
p4.quad(top=hosp, bottom=0, left=yearday -.2, right=yearday+.1,fill_color=colorshex["hosp"], line_color="white", alpha=1,legend_label="Indlagt")
p4.quad(top=ita, bottom=0, left=yearday -.15, right=yearday+.1,fill_color=colorshex["ita"], line_color="white", alpha=1,legend_label="på Intensiv")
p4.quad(top=resp, bottom=0, left=yearday -.10, right=yearday+.1,fill_color=colorshex["resp"], line_color="white", alpha=1,legend_label="i Respirator")
p4.quad(top=deaths, bottom=0, left=yearday +.10, right=yearday+.25,fill_color=colorshex["deaths"], line_color="white", alpha=1,legend_label="Død - akkumuleret")

p4.xaxis.axis_label = 'Dato'
p4.yaxis.axis_label = 'Antal'
p4.xaxis.ticker =  SingleIntervalTicker(interval=7, num_minor_ticks=7)
p4.y_range=Range1d(0, maxy)
p4.legend.location = 'top_left'
p4.xaxis.major_label_overrides =tickdict

save(p4)

p5 = figure(title="Oversigt procent indlagte - COVID19", tools='', background_fill_color="#fafafa")
output_file('percent.html', title="Intensiv i procent DK")

# p4.quad(top=hosp, bottom=0, left=weekday -.015, right=weekday+.010,fill_color=colorshex["hosp"], line_color="white", alpha=1,legend_label="Indlagt")
p5.quad(top=(ita/hosp)*100, bottom=0, left=yearday -.10, right=yearday,fill_color=colorshex["ita"], line_color="white", alpha=1,legend_label="% af indlagte på Intensiv")
p5.quad(top=(resp/hosp)*100, bottom=0, left=yearday, right=yearday+.1,fill_color=colorshex["resp"], line_color="white", alpha=1,legend_label="% af indlagte i Respirator")
p5.xaxis.axis_label = 'Dato'
p5.yaxis.axis_label = '%'
p5.xaxis.ticker =  SingleIntervalTicker(interval=7, num_minor_ticks=7)
p5.yaxis.ticker =  SingleIntervalTicker(interval=5, num_minor_ticks=5)
p5.y_range=Range1d(0, 30)
p5.legend.location = 'top_left'
p5.xaxis.major_label_overrides =tickdict

save(p5)
