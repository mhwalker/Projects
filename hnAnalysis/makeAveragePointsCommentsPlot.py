import MySQLdb
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import colorsys
import matplotlib.dates as mdates
import sys

topN=30

if len(sys.argv) < 2:
	print "Need at least 1 argument"
	sys.exit(0)

topN=int(sys.argv[1])

db = MySQLdb.connect(host="localhost",user="hnAnalysis",passwd="hnhnhn",db="hnAnalysis")
cursor = db.cursor()

thetime=datetime.datetime(2007,1,1)
deltatime=datetime.timedelta(1)
endtime=datetime.datetime(2013,10,1)

avgPoints = []
avgComments = []
avgPoC = []
dates = []
dates7day = []
avgPoints7day = []
avgComments7day = []
avgPoC7day = []
ticks = []
ticklabels = []
ind = 0
ndays = 0
totp7 = 0
totc7 = 0
totpc7 = 0

while thetime < endtime:
	query="SELECT points,num_comments FROM submissionMetaData WHERE date(create_ts) = \""+thetime.strftime("%Y-%m-%d")+"\" ORDER BY points DESC limit "+str(topN)+";"
	#print query
	cursor.execute(query)
	results = cursor.fetchall()
	ind += 1
	if len(results) == 0 or len(results[0]) == 0:
		thetime += deltatime
		continue
	points = 0
	comments = 0
	poc = 0
	for row in results:
		#print row
		rpoints = float(row[0])
		rcomments = float(row[1])
		rpoc = rpoints/rcomments if rcomments > 0 else 0
		points += rpoints
		comments += rcomments
		poc += rpoc
	points /= len(results)
	comments /= len(results)
	poc /= len(results)
	avgPoints.append(points)
	avgComments.append(comments)
	avgPoC.append(poc)
	dates.append(thetime)

	ndays += 1
	totp7 += points
	totc7 += comments
	totpc7 += poc
	if ind % 7 == 0:
		avgPoints7day.append(totp7/ndays)
		avgComments7day.append(totc7/ndays)
		avgPoC7day.append(totpc7/ndays)
		dates7day.append(thetime)
		ndays = 0
		totp7 = 0
		totc7 = 0
		totpc7 = 0
		ind = 0

	if thetime.day == 1 and thetime.month % 2 == 1:
		ticks.append(thetime)
		ticklabels.append(thetime.strftime("%Y-%m-%d"))
	thetime += deltatime

fig,ax = plt.subplots()
fig.subplots_adjust(right=0.8,bottom=0.05,left=0.05)
fig.set_size_inches(18,10)	
ax.plot(dates,avgPoints,'.',color='Blue',label='Daily Average Points',alpha=0.15)
ax.plot(dates7day,avgPoints7day,'-',color='Blue',label='7 day Average Points',linewidth=2)
ax.set_ylabel('Points')
ax.legend(loc='center left', bbox_to_anchor=(1.05, 0.5),prop={'size':10})
#ax.tick_params(axis='y', colors=colors[i])
dmax = max(avgPoints)
cmax = max(avgComments)
ax.set_ylim((0,max(dmax*1.2,1.2)))
ax.set_xlabel('Date')
#ax.set_xticks(dates)
#ax.set_xticklabels([dates[i].strftime("%Y-%m-%d") if dates[i].day == 1 and dates[i].month % 2 == 1 else "" for i in range(0,len(dates))],rotation=45)
ax.set_xticklabels(ticklabels)
for t1 in ax.get_yticklabels():
	t1.set_color('Blue')

ax2 = ax.twinx()
ax2.plot(dates,avgComments,'.',color='Red',label='Daily Average Comments',alpha=0.15)
ax2.plot(dates7day,avgComments7day,'-',color='Red',label='7 day Average Comments',linewidth=2)
ax2.set_ylabel("Comments")
ax2.set_ylim((0,max(cmax*1.2,1.2)))
ax2.legend(loc='center left', bbox_to_anchor=(1.05,0.4),prop={'size':10})
for t1 in ax2.get_yticklabels():
	t1.set_color('Red')

filename="avgQuantities_"+str(topN)+".png"
fig.autofmt_xdate()
ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
plt.title('Average for top '+str(topN)+' submissions')
fig.savefig(filename)
plt.close()

