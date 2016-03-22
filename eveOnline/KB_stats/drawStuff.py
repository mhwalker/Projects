import MySQLdb
import datetime as DT
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import matplotlib.dates as mdates
import colorsys

def readLine(line):
	linesplit = line.split()
	corpID = int(linesplit[0])
	realMembers  = int(linesplit[1])
	dbMembers = int(linesplit[2])
	kills = [0]
	deaths = [0]
	members = [0]
	for i in range(1,12):
		kills.append(int(linesplit[13+i]))
		deaths.append(int(linesplit[2+i]))
		members.append(int(linesplit[24+i]))
	#print corpID,realMembers,dbMembers,kills,deaths,members
	return corpID,realMembers,dbMembers,kills,deaths,members

TESTid=499

corpDICT= dict()
corpSET = set()

PACSET = set()
fPAC = open("PACS.txt",'r')
for line in fPAC.readlines():
	name=line

#get TEST corps
db = MySQLdb.connect(host="localhost",user="root",port=3306,db="TESTKB",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()
corpSQL = "SELECT crp_id,crp_name FROM kb3_corps WHERE crp_all_id=499;"
cursor.execute(corpSQL)
corpRES = cursor.fetchall()
corpKILLS=dict()
corpDEATH=dict()
corpSIZE=dict()
corpREVERSE=dict()
corpREALSIZE=dict()
for row in corpRES:
	#print int(row[0]),row[1]
	corpDICT[int(row[0])] = row[1]
	corpREVERSE[row[1]] = int(row[0])
	corpSET.add(int(row[0]))
	corpKILLS[int(row[0])] = []
	corpDEATH[int(row[0])] = []
	corpSIZE[int(row[0])] = []

PACSET = set()
fPAC = open("PACS.txt",'r')
for line in fPAC.readlines():
	name=line.strip()
	if not corpREVERSE.has_key(name): continue
	#print name,corpREVERSE[name]
	PACSET.add(corpREVERSE[name])
	
dates = []
for i in range(1,12):
	dates.append(DT.date(2012,i,1))
	
f = open('outfile.out','r')
for line in f.readlines():
	corpID,realMembers,dbMembers,kills,deaths,members=readLine(line)
	if realMembers == 0: continue
	if corpID in PACSET: continue
	corpKILLS[corpID].extend(kills)
	corpDEATH[corpID].extend(deaths)
	corpSIZE[corpID].extend(members)
	corpREALSIZE[corpID] = [realMembers,dbMembers]
	fig,ax = plt.subplots()
	axes = [ax,ax.twinx()]
	datas = [kills,deaths]
	colors = ['Green','Red']
	labels = ['Kills / member','Deaths / member']
	fig.subplots_adjust(right=0.9,bottom=0.2)
	for i,ax in enumerate(axes):
		data = []
		for j in range(1,12):
			data.append(float(datas[i][j])/float(realMembers))
		ax.plot(dates,data,'-',color=colors[i])
		ax.set_ylabel(labels[i],color=colors[i])
		ax.tick_params(axis='y', colors=colors[i])
		dmax = max(data)
		ax.set_ylim((0,max(dmax*1.2,1.2)))
	axes[0].set_xlabel('Date')
	axes[0].set_xticks(dates)
	axes[0].set_xticklabels([date.strftime("%Y-%m-%d") for date in dates],rotation=45)
	filename="plots/"+corpDICT[corpID].replace(" ","_")+".png"
	fig.autofmt_xdate()
	axes[0].fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
	plt.title(corpDICT[corpID])
	fig.savefig(filename)
	plt.close()

f = open('outfile.out','r')
for line in f.readlines():
	corpID,realMembers,dbMembers,kills,deaths,members=readLine(line)
	if realMembers == 0: continue
	if corpID in PACSET: continue
	corpKILLS[corpID].extend(kills)
	corpDEATH[corpID].extend(deaths)
	corpSIZE[corpID].extend(members)
	corpREALSIZE[corpID] = [realMembers,dbMembers]
	fig,ax = plt.subplots()
	axes = [ax]
	datas = [kills,deaths]
	colors = ['Green']
	labels = ['(Kills + deaths)/ member']
	fig.subplots_adjust(right=0.9,bottom=0.2)
	for i,ax in enumerate(axes):
		data = []
		for j in range(1,12):
			data.append(float(kills[j]+deaths[j])/float(realMembers))
		ax.plot(dates,data,'-',color=colors[i])
		ax.set_ylabel(labels[i],color=colors[i])
		ax.tick_params(axis='y', colors=colors[i])
		dmax = max(data)
		ax.set_ylim((0,max(dmax*1.2,1.2)))
	axes[0].set_xlabel('Date')
	axes[0].set_xticks(dates)
	axes[0].set_xticklabels([date.strftime("%Y-%m-%d") for date in dates],rotation=45)
	filename="otherPlots/"+corpDICT[corpID].replace(" ","_")+".png"
	fig.autofmt_xdate()
	axes[0].fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
	plt.title(corpDICT[corpID])
	fig.savefig(filename)
	plt.close()

dredditID = 8275
#fig.set_size_inches(20,16)
index = 0.0
pindex = 0
#print corpREALSIZE
dredditSIZE = corpREALSIZE[dredditID][0]
fig,ax = plt.subplots(figsize=(15,12),dpi=80)
for k in sorted(corpREALSIZE.iterkeys()):
	if abs(index-1.0) < 0.01:
		index = 0.0
		box1 = ax.get_position()
		ax.set_position([box1.x0, box1.y0, box1.width * 0.8, box1.height])
		ax.set_xlabel('Date')
		ax.set_ylabel('(Kills + Deaths)/ member normalized to B0RT')
		ax.set_xticks(dates)
		#ax.set_ylim((0,14))
		ax.set_xticklabels([date.strftime("%Y-%m-%d") for date in dates],rotation=45)
		ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),title='Corp',prop={'size':10})
		plt.title("Corp Comparison")
		fig.subplots_adjust(right=0.75,bottom=0.2,left=0.1)
		l = plt.axhline(y=1,linewidth=2,color='Black')
		fig.savefig("comparison_"+str(pindex)+".png")
		plt.close()	
		pindex += 1
		fig,ax = plt.subplots(figsize=(15,12),dpi=80)

	v = corpREALSIZE[k]
	#print k,v
	corpID = k
	if corpID in PACSET: continue
	corpNAME = corpDICT[corpID]
	realMembers = v[0]
	data = []
	for j in range(1,12):
		data.append(float(corpKILLS[corpID][j]+corpDEATH[corpID][j])/float(realMembers)*float(dredditSIZE)/float(corpKILLS[dredditID][j]+corpDEATH[dredditID][j]))
	ax.plot(dates,data,'-',color=colorsys.hls_to_rgb(index,0.5,0.5),label=corpNAME,lw=1.5)
	index += 0.1
	

box1 = ax.get_position()
ax.set_position([box1.x0, box1.y0, box1.width * 0.8, box1.height])
ax.set_xlabel('Date')
ax.set_ylabel('(Kills + Deaths)/ member normalized to B0RT')
ax.set_xticks(dates)
#ax.set_ylim((0,14))
ax.set_xticklabels([date.strftime("%Y-%m-%d") for date in dates],rotation=45)
ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),title='Corp',prop={'size':10})
plt.title("Corp Comparison")
fig.subplots_adjust(right=0.75,bottom=0.2,left=0.1)
l = plt.axhline(y=1,linewidth=2,color='Black')
fig.savefig("comparison_"+str(pindex)+".png")
plt.close()	