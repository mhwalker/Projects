import MySQLdb
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import colorsys
import matplotlib.dates as mdates

db = MySQLdb.connect(host="localhost",user="hnAnalysis",passwd="hnhnhn",db="hnAnalysis")
cursor = db.cursor()

query="SELECT * FROM submissions;"
cursor.execute(query)
results=cursor.fetchall()

dates = []
data = []
dataWeek = []
dataEnd = []
datesWeek = []
datesEnd = []
dates7day = []
data7day = []
ind = 1
tot7 = 0
ticks = []
ticklabels = []
for row in results:
	thedate = row[0]
	if thedate.year < 2007: continue
	submissions = int(row[1])
	dates.append(thedate)
	data.append(submissions)
	if thedate.weekday() == 5 or thedate.weekday() == 6:
		datesEnd.append(thedate)
		dataEnd.append(submissions)
	else:
		datesWeek.append(thedate)
		dataWeek.append(submissions)
	tot7 += submissions
	if ind % 7 == 0:
		data7day.append(float(tot7)/7)
		dates7day.append(thedate)
		ind = 0
		tot7 = 0
	ind += 1
	if thedate.day == 1 and thedate.month % 2 == 1:
		ticks.append(thedate)
		ticklabels.append(thedate.strftime("%Y-%m-%d"))
fig,ax = plt.subplots()
label = 'Submissions per Day'
fig.subplots_adjust(right=0.86,bottom=0.2)
fig.set_size_inches(18,10)	
ax.plot(datesWeek,dataWeek,'.',color='Black',label='Weekday Submissions')
ax.plot(datesEnd,dataEnd,'.',color='Red',label='Weekend Submissions')
ax.plot(dates7day,data7day,'-',color='Blue',label='7-day average',linewidth=2)
ax.plot
ax.set_ylabel(label)
ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),prop={'size':10})
#ax.tick_params(axis='y', colors=colors[i])
dmax = max(data)
ax.set_ylim((0,max(dmax*1.2,1.2)))
ax.set_xlabel('Date')
#ax.set_xticks(dates)
#ax.set_xticklabels([dates[i].strftime("%Y-%m-%d") if dates[i].day == 1 and dates[i].month % 2 == 1 else "" for i in range(0,len(dates))],rotation=45)
ax.set_xticks(ticks)
ax.set_xticklabels(ticklabels)
filename="submissionsPerDay.png"
fig.autofmt_xdate()
ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
plt.title('Submissions Per Day')
fig.savefig(filename)
plt.close()

