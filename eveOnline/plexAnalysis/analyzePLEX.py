import MySQLdb
import urllib2
import xml.etree.cElementTree as ET
import operator
import matplotlib.pyplot as plt
import colorsys
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec

db = MySQLdb.connect(host="localhost",user="testmetrics",passwd="t3stm3trics",db="MARKETHISTORY")
cursor = db.cursor()



query = "SELECT day,low,average,high,quantity FROM history WHERE regionID=10000002 AND typeID=29668 AND day > '2013-04-30 23:49:00' ORDER BY day;"
cursor.execute(query)
rows = cursor.fetchall()

things = dict()

days = []
lows = []
avgs = []
highs = []
quantities = []

lowpercents = []
avgones = []
highpercents = []

for row in rows:
	day = row[0]
	low = float(row[1])
	avg = float(row[2])
	high = float(row[3])
	quantity = int(row[4])
	days.append(day)
	lows.append(low)
	avgs.append(avg/1e6)
	highs.append(high)
	quantities.append(quantity)
	lowpercents.append((low-avg)/avg)
	highpercents.append((high-avg)/avg)
	avgones.append(0.0)

fig = plt.figure(figsize=(15,15),dpi=80)
gs1 = gridspec.GridSpec(5,3)
gs1.update(top=0.99,bottom=0.08,left=0.12,right=0.99,hspace=0.05)
ax1 = plt.subplot(gs1[0:3,:])
ax2 = plt.subplot(gs1[3,:])
ax3 = plt.subplot(gs1[4,:])
#fig,(ax1,ax2,ax3) = plt.subplots(3,sharex=True,sharey=False,figsize=(15,15),dpi=80)
#plt.subplots_adjust(top=0.95,bottom=0.01,left=0.1,right=0.99,hspace=0.0)
ax1.plot(days,avgs,'r-',linewidth=4)
ax1.set_ylim((0,850))
ax1.set_ylabel('Average PLEX price (M ISK)',fontsize=18)
ax1.xaxis.grid(b=True)
ax1.yaxis.grid(b=True)
ax2.plot(days,avgones,'k-')
ax2.fill_between(days,lowpercents,highpercents,facecolor='blue',alpha=0.5)
#ax2.plot(days,lowpercents,'b--',label="Low Prices")
#ax2.plot(days,highpercents,'b-',label="High Prices")
ax2.set_ylim((-0.035,0.035))
ax2.set_ylabel('Fractional Envelope\nof Low/High Price\nAround Average',fontsize=18,multialignment='center')
ax2.xaxis.grid(b=True)
ax3.bar(days,quantities,color=(0.05,0.5,0.25),edgecolor=(0.05,0.5,0.25),width=0.001)
ax3.set_xlabel('Date',fontsize=18)
ax3.set_ylabel('Quantity traded',fontsize=18)
ax3.xaxis.grid(b=True)

xticks = []
for i,date in enumerate(days):
	if date.day == 1:
		xticks.append(date)

ax1.set_xticks(xticks)
ax2.set_xticks(xticks)
ax3.set_xticks(xticks)
ax3.set_xticklabels([date.strftime("%Y-%m-%d") for date in xticks],rotation=45)
fig.autofmt_xdate()
ax3.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

fig.savefig("plex.pdf")
