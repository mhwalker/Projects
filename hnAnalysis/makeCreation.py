import MySQLdb
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import colorsys
import matplotlib.dates as mdates
import urllib2
import json

url="http://api.thriftdb.com/api.hnsearch.com/users/_search?pretty_print=true&facet[fields][create_ts][include]=1&facet[fields][create_ts][limit]=1000000"
request = urllib2.Request(url)
try: 
	result = urllib2.urlopen(request)
except urllib2.HTTPError,err:
	print "ERROR:",url,err.code
except urllib2.URLError, err:
	print "ERROR URL",url,err.reason

try:            
	jsondata = json.load(result)
except ValueError:
	print "Decoding Failed",url

initdata=dict()
for facet in jsondata["facet_results"]["fields"]["create_ts"]["facets"]:
	createts = datetime.datetime.strptime(facet["value"],"%Y-%m-%dT%H:%M:%SZ")
	n = int(facet["count"])
	initdata[createts] = n

daydata = dict()
for k,v in initdata.iteritems():
	thedate = k.date()
	if not daydata.has_key(thedate): daydata[thedate] = 0
	daydata[thedate] += v

tot = 0
data = []
dates = []
ticks = []
ticklabels = []
deriv7day = []
dates7day = []
ind = 0
ndays = 0
tot7 = 0
for k in sorted(daydata.keys()):
	ind += 1
	v = daydata[k]
	tot += v
	tot7 += v
	ndays += 1
	data.append(tot)
	dates.append(k)
        if k.day == 1 and k.month % 2 == 1:
                ticks.append(k)
                ticklabels.append(k.strftime("%Y-%m-%d"))
	if ind % 7 == 0:
		deriv7day.append(float(tot7)/float(ndays))
		dates7day.append(k)
		ind = 0
		tot7 = 0
		ndays = 0

fig,ax = plt.subplots()
fig.subplots_adjust(right=0.86,bottom=0.2)
fig.set_size_inches(18,10)	
ax.plot(dates,data,'-',color='Red',label='Total Users')
#ax.plot
ax.set_ylabel("Users")
ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),prop={'size':10})
#ax.tick_params(axis='y', colors=colors[i])
dmax = max(data)
ax.set_ylim((0,max(dmax*1.2,1.2)))
ax.set_xlabel('Date')
#ax.set_xticks(dates)
#ax.set_xticklabels([dates[i].strftime("%Y-%m-%d") if dates[i].day == 1 and dates[i].month % 2 == 1 else "" for i in range(0,len(dates))],rotation=45)
ax.set_xticks(ticks)
ax.set_xticklabels(ticklabels)
filename="totalUsers.png"
fig.autofmt_xdate()
ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
plt.title('Total Users')
fig.savefig(filename)

plt.clf()

fig,ax = plt.subplots()
fig.subplots_adjust(right=0.86,bottom=0.2)
fig.set_size_inches(18,10)	
ax.plot(dates7day,deriv7day,'-',color='Blue',label='User Growth per day (avg)')
ax.set_ylabel("Users/day")
ax.legend(loc='center left',bbox_to_anchor=(1.01,0.5),prop={'size':10})
dmax = max(deriv7day)
ax.set_ylim(0,max(dmax*1.2,1.2))
ax.set_xlabel('Date')
ax.set_xticks(ticks)
ax.set_xticklabels(ticklabels)
filename="userGrowth.png"
fig.autofmt_xdate()
ax.fmt_xdata=mdates.DateFormatter('%Y-%m-%d')
plt.title('User Growth')
fig.savefig(filename)


plt.close()

