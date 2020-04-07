import os, sys,datetime,time

import numpy as np
# import scipy.special
from scipy.optimize import curve_fit



#BOKEH - library for visual presentation of data
from bokeh.layouts import gridplot
from bokeh.plotting import figure, output_file, show,save
from bokeh.models import SingleIntervalTicker, LinearAxis,Range1d,Title
from bokeh.layouts import gridplot


#Path to lib folder
libpath = os.path.realpath(__file__).split("plotter.")[0] + os.sep

#Path to data folder
datap = libpath.split("lib")[0]+ os.sep  + "data DK" + os.sep

# import data
global hosp,ita,resp,deaths,week,weekday,yearday,latest,dater

hosp = []
ita = []
resp = []
deaths = []

week = []
weekday = []
yearday = []

dater = []

latest = np.zeros([4,1])

def sigmoid(x, L ,x0, k, b):
    y = L / (1 + np.exp(-k*(x-x0)))+b
    return (y)

def expfunc_old(x, a, b, c):
    return a * np.exp(-b * x) + c

def expfunc(x, x0, k, b):
    y = np.exp(-k*(x-x0))+b
    return (y)


numbers = {"ita":ita,"hosp": hosp,"resp":resp,"deaths":deaths}
colorshex = {"ita":"#FF847c","hosp": "#FECEA8","resp":"#E84A5F","deaths":"#2A363B"}

def getdata(fileofinterest,getweek):
    global hosp,ita,resp,deaths,week,weekday,numbers,yearday,latest,dater

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
                    dater.append(str(d) + "." + str(m))
                    dayofyear = mydate.timetuple().tm_yday
                    yearday.append(dayofyear)

        # Date and time for latest datapoint
        latest[0] = int(data[-3][:4]) #Year
        latest[1] = int(data[-3][4:6]) # Month
        latest[2] = int(data[-3][6:8]) # Day
        latest[3] = int(data[2]) # Time



getdata("ita",False)
getdata("resp",False)
getdata("deaths",False)
getdata("hosp",True) # Call hospitalizations at the end as data is more recent than deaths


print(latest)

#Conversion to numpy
ita = np.array(ita)
hosp = np.array(hosp)
resp = np.array(resp)
deaths = np.array(deaths)
weekday = np.array(weekday)
yearday = np.array(yearday)

maxy = np.max(hosp) + 25

## Creating x-axis.

tickdict = {72:"12.3", 74:"14.3"} # Dict for displaying dates instead of days. Hardcoded some dates from beginning
dayinterval = 3 # Interval between dates shown


for i,dd in enumerate(dater):
    print(i,dd)
    tickdict[int(yearday[i])] = dater[i] #index in tickdect must be forced INT due to some JSON thing. https://github.com/bokeh/bokeh/issues/8166

#Add XX days for x axis for regressions.
for ik in range(1,4):
    mydtt = datetime.timedelta(days=ik) + datetime.datetime(2020, int(dater[-1].split(".")[-1]) , int(dater[-1].split(".")[0]), 12, 00, 00)
    tickdict[int(yearday[-1] +ik)] = str(mydtt.day) + "." +str(mydtt.month)






#Regressions
xdata = (yearday - yearday[0]) + .1
ydata = hosp

p0 = [max(ydata), np.median(xdata),1,min(ydata)] # this is an mandatory initial guess
popt, pcov = curve_fit(sigmoid, xdata[:-1], ydata[:-1],p0, method='dogbox')
print("SIGM SUCCES",popt,pcov)
try:
    poptexp, pcovexp = curve_fit(expfunc, xdata[:-1], ydata[:-1],p0=[1,1,1],method='dogbox', maxfev=5000)
    print("EXP SUCCES",poptexp,pcovexp)
except RuntimeError:
    poptexp = popt[1:]

#If exponents zero use the sigmoid exp part
if pcovexp[0][0] == 0:
    poptexp = popt[1:]

daysforward = 2
fakex = np.linspace(0,np.max(xdata) - xdata[0] - 1,150) #week 1. 16.3.2020.
fakex_forward = np.linspace(np.max(xdata) - xdata[0] -1,np.max(xdata) - xdata[0] + daysforward,50) #Fremskriver seneste situation med 3 dage

y = sigmoid(fakex, *popt)
yexp = expfunc(fakex,*poptexp)

y_forward = sigmoid(fakex_forward, *popt)
yexp_forward = expfunc(fakex_forward,*poptexp)

midway = (y_forward + yexp_forward)*.5


#Graph with regressions
p1 = figure(title="Antal indlagte - COVID19 - Danmark", tools='', background_fill_color="#fafafa")
p1.add_layout(Title(text="Data kilde: Sundhedsstyrelsen", text_font_style="italic",text_font_size="8pt"), 'below')
p1.add_layout(Title(text= "Regressionerne (fit) repræsenterer kun eksisterende data, pas på ved fremskrivning. Data fra kl:" + str(int(latest[-1][0])) + " " + str(int(latest[-2][0])) + "." + str(int(latest[-3][0])) + "." + str(int(latest[0][0])), text_font_style="italic",text_font_size="8pt"), 'above')
p1.add_layout(Title(text="Visuel præsentation: bigb8.github.io/coviddanmark/ - refenceliste på adressen", text_font_style="italic",text_font_size="8pt"), 'below')

output_file('hosp.html', title="Indlagte DK")

p1.quad(top=hosp, bottom=0, left=yearday -.2, right=yearday+.2,fill_color=colorshex["hosp"], line_color="white", alpha=1)
p1.line(fakex+yearday[0],y,line_color="#59c25d", line_width=4, alpha=0.8, legend_label="Sigmoid regression")
# p1.line(fakex+yearday[0],yexp,line_color="#ff8888", line_width=4, alpha=0.8, legend_label="Exponentiel regression")
p1.line(fakex_forward+yearday[0],y_forward,line_color="#59c25d", line_width=4, alpha=0.4,line_dash=[2,2], legend_label="Sigmoid regression")
# p1.line(fakex_forward+yearday[0],yexp_forward,line_color="#ff8888", line_width=4, alpha=0.4,line_dash=[2,2], legend_label="Exponentiel regression")
# p1.line(fakex_forward+yearday[0],midway,line_color="#696969", line_width=4, alpha=0.4,line_dash=[2,2], legend_label="Gennemsnit af regressioner")


p1.xaxis.axis_label = 'Dato'
p1.yaxis.axis_label = 'Antal'
p1.xaxis.ticker =  SingleIntervalTicker(interval=dayinterval, num_minor_ticks=dayinterval)
p1.y_range=Range1d(0, np.max(hosp)+125)
p1.legend.location = 'top_left'
p1.xaxis.major_label_overrides =tickdict
save(p1)




##Summary plot of hospitalized
p4 = figure(title="Oversigt indlagte - COVID19 - Danmark", tools='', background_fill_color="#fafafa")
output_file('stacked.html', title="Oversigt DK")

p4.quad(top=hosp, bottom=0, left=yearday -.4, right=yearday+.1,fill_color=colorshex["hosp"], line_color="white", alpha=1,legend_label="Indlagt")
p4.quad(top=ita, bottom=0, left=yearday -.2, right=yearday+.1,fill_color=colorshex["ita"], line_color="white", alpha=1,legend_label="på intensiv")
p4.quad(top=resp, bottom=0, left=yearday -.10, right=yearday+.1,fill_color=colorshex["resp"], line_color="white", alpha=1,legend_label="i respirator")
p4.quad(top=deaths, bottom=0, left=yearday +.10, right=yearday+.3,fill_color=colorshex["deaths"], line_color="white", alpha=1,legend_label="Død - akkumuleret")

p4.add_layout(Title(text="Data kilde: Sundhedsstyrelsen", text_font_style="italic",text_font_size="8pt"), 'below')
p4.add_layout(Title(text="Data fra kl:" + str(int(latest[-1][0])) + " " + str(int(latest[-2][0])) + "." + str(int(latest[-3][0])) + "." + str(int(latest[0][0])) , text_font_style="italic",text_font_size="8pt"), 'above')
p4.add_layout(Title(text="Visuel præsentation: bigb8.github.io/coviddanmark/ - refenceliste på adressen", text_font_style="italic",text_font_size="8pt"), 'below')

p4.xaxis.axis_label = 'Dato'
p4.yaxis.axis_label = 'Antal'
p4.xaxis.ticker =  SingleIntervalTicker(interval=dayinterval, num_minor_ticks=dayinterval)
p4.y_range=Range1d(0, maxy)
p4.legend.location = 'top_left'
p4.xaxis.major_label_overrides =tickdict
save(p4)


## Percentages on ITA

avg_days = 5
avg_DK = np.average((ita[-avg_days:]/hosp[-avg_days:])*100)
avg_DK_ri = np.average((resp[-avg_days:]/ita[-avg_days:])*100)



p5 = figure(title="Procent indlagte på intensiv - COVID19 - Danmark", tools='', background_fill_color="#fafafa")
p5.add_layout(Title(text="Data kilde: Sundhedsstyrelsen, JAMA", text_font_style="italic",text_font_size="8pt"), 'below')
p5.add_layout(Title(text="Data fra kl:" + str(int(latest[-1][0])) + " " + str(int(latest[-2][0])) + "." + str(int(latest[-3][0])) + "." + str(int(latest[0][0])), text_font_style="italic",text_font_size="8pt"), 'above')
p5.add_layout(Title(text="Visuel præsentation og gennemsnit: bigb8.github.io/coviddanmark/ - refenceliste på adressen", text_font_style="italic",text_font_size="8pt"), 'below')
output_file('percent.html', title="Intensiv i procent DK")

# p5.quad(top=(resp/hosp)*100, bottom=0, left=yearday, right=yearday+.35,fill_color=colorshex["resp"], line_color="white", alpha=1,legend_label="% af indlagte i respirator")

p5.quad(top=(ita/hosp)*100, bottom=0, left=yearday -.2, right=yearday+.2,fill_color=colorshex["ita"], line_color="white", alpha=1,legend_label="% af indlagte på intensiv")
p5.line([yearday[0], yearday[-1]+1],[16,16],line_color="#3b73a8", line_width=3, alpha=0.8, legend_label="% på intensiv, Italien, 7.3.2020")
p5.line([yearday[-5], yearday[-1]+1],[avg_DK,avg_DK],line_color="#535955", line_width=3, alpha=0.8, legend_label="% på intensiv, Gns. DK, "+str(avg_days)+" dage")

p5.xaxis.axis_label = 'Dato'
p5.yaxis.axis_label = '%'
p5.xaxis.ticker =  SingleIntervalTicker(interval=dayinterval+5, num_minor_ticks=dayinterval+5)
p5.yaxis.ticker =  SingleIntervalTicker(interval=5, num_minor_ticks=5)
p5.y_range=Range1d(0, 30)
p5.legend.location = 'top_left'
p5.xaxis.major_label_overrides =tickdict

save(p5)


p5_ri = figure(title="Procent på intensiv i respirator - COVID19 - Danmark", tools='', background_fill_color="#fafafa")
p5_ri.quad(top=(resp[7:]/ita[7:])*100, bottom=0, left=yearday[7:] -.2, right=yearday[7:]+.2,fill_color=colorshex["ita"], line_color="white", alpha=1,legend_label="% af indlagte på intensiv")
p5_ri.line([yearday[7], yearday[-1]+1],[80,80],line_color="#3b73a8", line_width=3, alpha=0.8, legend_label="% SST antagelse 22.03.2020")
p5_ri.line([yearday[-5], yearday[-1]+1],[avg_DK_ri,avg_DK_ri],line_color="#535955", line_width=3, alpha=0.8, legend_label="%, Gns. DK, "+str(avg_days)+" dage")

p5_ri.add_layout(Title(text="Data kilde: Sundhedsstyrelsen", text_font_style="italic",text_font_size="8pt"), 'below')
p5_ri.add_layout(Title(text="Data fra kl:" + str(int(latest[-1][0])) + " " + str(int(latest[-2][0])) + "." + str(int(latest[-3][0])) + "." + str(int(latest[0][0])), text_font_style="italic",text_font_size="8pt"), 'above')
p5_ri.add_layout(Title(text="Visuel præsentation og gennemsnit: bigb8.github.io/coviddanmark/ - refenceliste på adressen", text_font_style="italic",text_font_size="8pt"), 'below')

p5_ri.xaxis.axis_label = 'Dato'
p5_ri.yaxis.axis_label = '%'
p5_ri.xaxis.ticker =  SingleIntervalTicker(interval=dayinterval+5, num_minor_ticks=dayinterval+5)
p5_ri.yaxis.ticker =  SingleIntervalTicker(interval=5, num_minor_ticks=5)
p5_ri.y_range=Range1d(0,100)
p5_ri.legend.location = 'bottom_left'
p5_ri.xaxis.major_label_overrides =tickdict
output_file('percent_ri.html', title="Respirator på ITA i procent DK")
save(p5_ri)


# p = gridplot([[p5], [p5_ri]],plot_width=600, plot_height=800)














##Summary plot of hospitalized
p51 = figure(title="Oversigt ændring indlagte - COVID19 - Danmark", tools='', background_fill_color="#fafafa")
p52 = figure(title="Oversigt ændring intenstiv indlagte - COVID19 - Danmark", tools='', background_fill_color="#fafafa")
p53 = figure(title="Oversigt ændring intensiv + respirator - COVID19 - Danmark", tools='', background_fill_color="#fafafa")
p54 = figure(title="Oversigt ændring døde - COVID19 - Danmark", tools='', background_fill_color="#fafafa")


output_file('delta_1.html', title="Oversigt DK")

p51.quad(top=np.diff(hosp), bottom=0, left=yearday -.4, right=yearday+.1,fill_color=colorshex["hosp"], line_color="white", alpha=1,legend_label="Indlagt")

p51.add_layout(Title(text="Data kilde: Sundhedsstyrelsen", text_font_style="italic",text_font_size="8pt"), 'below')
p51.add_layout(Title(text="Data fra kl:" + str(int(latest[-1][0])) + " " + str(int(latest[-2][0])) + "." + str(int(latest[-3][0])) + "." + str(int(latest[0][0])) , text_font_style="italic",text_font_size="8pt"), 'above')
p51.add_layout(Title(text="Visuel præsentation og beregning: bigb8.github.io/coviddanmark/ - refenceliste på adressen", text_font_style="italic",text_font_size="8pt"), 'below')

p51.xaxis.axis_label = 'Dato'
p51.yaxis.axis_label = 'Antal'
p51.xaxis.ticker =  SingleIntervalTicker(interval=dayinterval+5, num_minor_ticks=dayinterval+5)
p51.y_range=Range1d(np.diff(hosp).min()-5, np.diff(hosp).max()+5)
p51.legend.location = 'top_left'
p51.xaxis.major_label_overrides =tickdict




p52.quad(top=np.diff(ita), bottom=0, left=yearday -.2, right=yearday+.1,fill_color=colorshex["ita"], line_color="white", alpha=1,legend_label="på intensiv")

p52.xaxis.axis_label = 'Dato'
p52.yaxis.axis_label = 'Antal'
p52.xaxis.ticker =  SingleIntervalTicker(interval=dayinterval+5, num_minor_ticks=dayinterval+5)
p52.y_range=Range1d(np.diff(ita).min()-5, np.diff(ita).max()+5)
p52.legend.location = 'top_left'
p52.xaxis.major_label_overrides =tickdict


p53.quad(top=np.diff(resp), bottom=0, left=yearday -.10, right=yearday+.1,fill_color=colorshex["resp"], line_color="white", alpha=1,legend_label="i respirator")

p53.xaxis.axis_label = 'Dato'
p53.yaxis.axis_label = 'Antal'
p53.xaxis.ticker =  SingleIntervalTicker(interval=dayinterval+5, num_minor_ticks=dayinterval+5)
p53.y_range=Range1d(np.diff(resp).min()-5, np.diff(resp).max()+5)
p53.legend.location = 'top_left'
p53.xaxis.major_label_overrides =tickdict



p54.quad(top=np.diff(deaths), bottom=0, left=yearday +.10, right=yearday+.3,fill_color=colorshex["deaths"], line_color="white", alpha=1,legend_label="døde")

p54.xaxis.axis_label = 'Dato'
p54.yaxis.axis_label = 'Antal'
p54.xaxis.ticker =  SingleIntervalTicker(interval=dayinterval+5, num_minor_ticks=dayinterval+5)
p54.y_range=Range1d(0, np.diff(deaths).max()+5)
p54.legend.location = 'top_left'
p54.xaxis.major_label_overrides =tickdict


p = gridplot([[p51, p52], [p53, p54]],plot_width=400, plot_height=250)


save(p)
