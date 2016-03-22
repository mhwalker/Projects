import MySQLdb
import datetime
import operator
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import matplotlib.dates as mdates
import colorsys
import header

db = MySQLdb.connect(host="localhost",user="root",port=3306,db="TESTKB",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()

corpSQL = "SELECT crp_id,crp_name FROM kb3_corps WHERE crp_all_id=499;"
cursor.execute(corpSQL)
corpRES = cursor.fetchall()
corpREVERSE=dict()
corpDICT = dict()
corpREALSIZE=dict()
for row in corpRES:
	corpDICT[int(row[0])] = row[1]
	corpREVERSE[row[1]] = int(row[0])

f = open('list.out')
for line in f.readlines():
	linesplit = line.split()
	name=""
	for i in range(0,len(linesplit)-1):
		name += linesplit[i]+" "
	name = name.strip()
	num = int(linesplit[i+1])
	if name == "STAHLSTURM": name = "Stahlsturm"
	if not corpREVERSE.has_key(name):
		continue
	corpREALSIZE[corpREVERSE[name]]= num


dmgSQL = "SELECT SUM(detail.ind_dmgdone),detail.ind_crp_id FROM kb3_kills as kills,kb3_inv_detail as detail where kills.kll_victim_id = 44799 and kills.kll_id = detail.ind_kll_id and detail.ind_all_id = 499 AND kills.kll_timestamp > \"2012-01-01 00:00:00\" GROUP BY detail.ind_crp_id;"

cursor.execute(dmgSQL)
dmgRES = cursor.fetchall()
corpDMG = dict()
for row in dmgRES:
	#print int(row[0])
	corpDMG[int(row[1])] = int(row[0])

sorted_DMG = sorted(corpDMG.iteritems(), key=operator.itemgetter(1))
sorted_DMG.reverse()
fig,ax = plt.subplots(figsize=(15,12),dpi=80)
data = []
data2 = []
labels = []
xvals = []
colors = []
i = 0
for pair in sorted_DMG:
	corpID = pair[0]
	dmg = pair[1]
	if dmg == 0: continue
	if not corpDICT.has_key(corpID):continue
	if not corpREALSIZE.has_key(corpID):continue
	name = corpDICT[corpID]
	data.append(dmg)
	data2.append(float(dmg)/float(corpREALSIZE[corpID]))
	if corpID == 8275: print float(dmg)/float(corpREALSIZE[corpID])
	colors.append(colorsys.hls_to_rgb(float(i)/43.0,0.5,0.5))
	#print name,dmg
	labels.append(name)
	i+=1
	#print corpID,dmg
ax.bar(range(len(data)),data,color=colors,align='center')
ax.set_ylabel("Damage")
ax.set_xlabel("Corporation")
ax.set_xlim(-1,36)
#print labels
#print len(data),len(labels)
ax.set_xticks(range(len(data)))
ax.set_xticklabels(labels,rotation=90,size=12)
fig.subplots_adjust(bottom=0.35)
plt.title("Damage to Makalu")
fig.savefig("makaluAbs.png")
plt.close()
fig,ax = plt.subplots(figsize=(15,12),dpi=80)
ax.bar(range(len(data2)),data2,color=colors,align='center')
ax.set_ylabel("Damage / Members")
ax.set_xlabel("Corporation")
ax.set_xlim(-1,36)
#print labels
#print len(data),len(labels)
ax.set_xticks(range(len(data)))
ax.set_xticklabels(labels,rotation=90,size=12)
fig.subplots_adjust(bottom=0.35)
plt.title("Damage to Makalu")
fig.savefig("makaluRel.png")
plt.close()