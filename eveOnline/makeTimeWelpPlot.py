import MySQLdb
import urllib2
import xml.etree.cElementTree as ET
import time
import datetime
import matplotlib.pyplot as plt
import colorsys
import matplotlib.dates as mdates

f = open("timewelp.txt",'r')
data = dict()
for line in f.readlines():
	ls = line.split()
	thedate = ls[0]
	n3st = float(ls[2])
	cfc = float(ls[3])
	data[thedate] = (n3st,cfc)

dataN3st = []
dates = []
dataCFC = []

for i in range(0,54):
	starttime = datetime.datetime(2013,6,6)
	endtime = datetime.datetime(2013,6,7)
	timedelta = datetime.timedelta(i)
	starttime += timedelta
	endtime += timedelta
	if data[endtime.strftime("%Y-%m-%d")][0] == 0 or data[endtime.strftime("%Y-%m-%d")][1] == 0: continue
	dates.append(endtime)
	dataN3st.append(data[endtime.strftime("%Y-%m-%d")][0])
	dataCFC.append(data[endtime.strftime("%Y-%m-%d")][1])

fig,ax = plt.subplots()
label = 'ISK lost (billions)'
fig.subplots_adjust(right=0.86,bottom=0.2)
	
ax.plot(dates,dataN3st,'-',color='Red',label='N3ST')
ax.plot(dates,dataCFC,'-',color='Blue',label='CFC')
ax.plot
ax.set_ylabel(label)
ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),title='Coalition',prop={'size':10})
#ax.tick_params(axis='y', colors=colors[i])
dmax = max(max(dataCFC),max(dataN3st))
ax.set_ylim((0,max(dmax*1.2,1.2)))
ax.set_xlabel('Date')
ax.set_xticks(dates)
#ax.set_xticklabels([date.strftime("%Y-%m-%d") for date in dates],rotation=45)
ax.set_xticklabels([dates[i].strftime("%Y-%m-%d") if i % 2 ==0 else "" for i in range(0,len(dates))],rotation=45)
filename="fountainWelpVsTime.png"
fig.autofmt_xdate()
ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
plt.title('Comparison of CFC and N3ST ISK losses over time')
fig.savefig(filename)
plt.close()
print filename

