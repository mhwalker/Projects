import MySQLdb
import datetime as DT
import operator
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import matplotlib.dates as mdates
import colorsys
from header import *

db = MySQLdb.connect(host="localhost",user="root",port=3306,db="TESTKB",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()



corpDMG = dict()
corpMEM = dict()
for k,v in corpREALSIZE.iteritems():
	corpMEM[k] = [0]*12
data = []
data2 = []
labels = []
xvals = []
colors = []
i = 0
dates = []
for i in range(1,12):
	dates.append(DT.date(2012,i,1))
for corpID in goodCORP:
	for i in range(1,12):
		startdate = DT.datetime.combine(DT.date(2012,i,1),DT.time(0,0,0))
		if i != 12: enddate = DT.datetime.combine(DT.date(2012,i+1,1),DT.time(0,0,0))
		else: enddate = DT.datetime.combine(DT.date(2013,1,1),DT.time(0,0,0))

		memSQL1 = "SELECT DISTINCT kills.kll_victim_id FROM kb3_kills as kills WHERE (kills.kll_timestamp > \""+str(startdate)+"\" AND kills.kll_timestamp < \""+str(enddate)+"\" AND kills.kll_crp_id = "+str(corpID)+");"
		memSQL2 = "SELECT DISTINCT details.ind_plt_id FROM kb3_inv_detail as details WHERE  (details.ind_timestamp > \""+str(startdate)+"\" and details.ind_timestamp < \""+str(enddate)+"\" AND details.ind_crp_id = "+str(corpID)+");"
		
		cursor.execute(memSQL1)
		memRES = cursor.fetchall()
		cmSET = set()
		for row in memRES:
			pilotID = int(row[0])
			cmSET.add(pilotID)
		cursor.execute(memSQL2)
		memRES = cursor.fetchall()
		cmSET = set()
		for row in memRES:
			pilotID = int(row[0])
			cmSET.add(pilotID)		
		nPilots = len(cmSET)
		corpMEM[corpID][i] = nPilots

dataDREDDIT = []
dredditID = 8275
for j in range(1,12):
	dataDREDDIT.append(float(corpMEM[dredditID][j])/float(corpREALSIZE[dredditID]))

for corpID in goodCORP:
	fig,ax = plt.subplots()
	color = 'Green'
	label = 'Active Members'
	fig.subplots_adjust(right=0.9,bottom=0.2)
	data = []
	for j in range(1,12):
		data.append(corpMEM[corpID][j])
	#print data
	#print corpMEM[corpID]
	ax.plot(dates,data,'-',color=color)
	ax.plot
	ax.set_ylabel(label)
	#ax.tick_params(axis='y', colors=colors[i])
	dmax = max(data)
	ax.set_ylim((0,max(dmax*1.2,1.2)))
	ax.set_xlabel('Date')
	ax.set_xticks(dates)
	ax.set_xticklabels([date.strftime("%Y-%m-%d") for date in dates],rotation=45)
	filename="otherPlots/active_"+corpDICT[corpID].replace(" ","_")+".png"
	fig.autofmt_xdate()
	ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
	plt.title(corpDICT[corpID])
	fig.savefig(filename)
	plt.close()
	print filename

	fig,ax = plt.subplots()
	color = 'Green'
	label = 'Active Fraction'
	fig.subplots_adjust(right=0.9,bottom=0.2)
	data = []
	for j in range(1,12):
		data.append(float(corpMEM[corpID][j])/float(corpREALSIZE[corpID]))
	ax.plot(dates,data,'-',color=color,lw=3,label=corpDICT[corpID])
	ax.plot(dates,dataDREDDIT,'-',label='Dreddit',color='Black')
	ax.set_ylabel(label)
	#ax.tick_params(axis='y', colors=colors[i])
	ax.set_ylim((0,1.1))
	ax.set_xlabel('Date')
	ax.set_xticks(dates)
	ax.set_xticklabels([date.strftime("%Y-%m-%d") for date in dates],rotation=45)
	filename="otherPlots/activeFraction_"+corpDICT[corpID].replace(" ","_")+".png"
	fig.autofmt_xdate()
	ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
	plt.title(corpDICT[corpID])
	fig.savefig(filename)
	plt.close()
	
			

dredditID = 8275
#fig.set_size_inches(20,16)
index = 0.0
pindex = 0
#print corpREALSIZE
dredditSIZE = corpREALSIZE[dredditID]
fig,ax = plt.subplots(figsize=(15,12),dpi=80)
for k in sorted(corpREALSIZE.iterkeys()):
	if abs(index-1.0) < 0.01:
		index = 0.0
		box1 = ax.get_position()
		ax.set_position([box1.x0, box1.y0, box1.width * 0.8, box1.height])
		ax.set_xlabel('Date')
		ax.set_ylabel('Active Members / member normalized to B0RT')
		ax.set_xticks(dates)
		#ax.set_ylim((0,14))
		ax.set_xticklabels([date.strftime("%Y-%m-%d") for date in dates],rotation=45)
		ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),title='Corp',prop={'size':10})
		plt.title("Corp Comparison")
		fig.subplots_adjust(right=0.75,bottom=0.2,left=0.1)
		l = plt.axhline(y=1,linewidth=2,color='Black')
		fig.savefig("activeComparison_"+str(pindex)+".png")
		plt.close()	
		pindex += 1
		fig,ax = plt.subplots(figsize=(15,12),dpi=80)

	realMembers = corpREALSIZE[k]
	#print k,v
	corpID = k
	corpNAME = corpDICT[corpID]
	data = []
	for j in range(1,12):
		data.append(float(corpMEM[corpID][j])/float(realMembers)*float(dredditSIZE)/float(corpMEM[dredditID][j]))
	ax.plot(dates,data,'-',color=colorsys.hls_to_rgb(index,0.5,0.5),label=corpNAME,lw=1.5)
	index += 0.1
	

box1 = ax.get_position()
ax.set_position([box1.x0, box1.y0, box1.width * 0.8, box1.height])
ax.set_xlabel('Date')
ax.set_ylabel('Active Members / member normalized to B0RT')
ax.set_xticks(dates)
#ax.set_ylim((0,14))
ax.set_xticklabels([date.strftime("%Y-%m-%d") for date in dates],rotation=45)
ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),title='Corp',prop={'size':10})
plt.title("Corp Comparison")
fig.subplots_adjust(right=0.75,bottom=0.2,left=0.1)
l = plt.axhline(y=1,linewidth=2,color='Black')
fig.savefig("activeComparison_"+str(pindex)+".png")
plt.close()	