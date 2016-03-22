import MySQLdb
import datetime

db = MySQLdb.connect(host="localhost",user="root",port=3306,db="TESTKB",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()
allianceSQL = "SELECT * FROM kb3_alliances;"
cursor.execute(allianceSQL)
allianceRES = cursor.fetchall()
TESTid=499

corpDICT= dict()
corpSET = set()


#get TEST corps
corpSQL = "SELECT crp_id,crp_name FROM kb3_corps WHERE crp_all_id=499;"
cursor.execute(corpSQL)
corpRES = cursor.fetchall()
corpKILLS=dict()
corpDEATH=dict()
corpSIZE=dict()
corpREVERSE=dict()
for row in corpRES:
	#print int(row[0]),row[1]
	corpDICT[int(row[0])] = row[1]
	corpREVERSE[row[1]] = int(row[0])
	corpSET.add(int(row[0]))
	corpKILLS[int(row[0])] = [0]*12
	corpDEATH[int(row[0])] = [0]*12
	corpSIZE[int(row[0])] = [0]*12


corpREALSIZE=dict()
f = open('list.out')
for line in f.readlines():
	linesplit = line.split()
	name=""
	for i in range(0,len(linesplit)-1):
		name += linesplit[i]+" "
	name = name.strip()
	if name == "STAHLSTURM": name = "Stahlsturm"
	num = int(linesplit[i+1])
	#print name
	#print corpREVERSE[name]
	if not corpREVERSE.has_key(name):continue
	corpREALSIZE[corpREVERSE[name]]= [num,0]
	#print name,num

PACSET = set()
fPAC = open("PACS.txt",'r')
for line in fPAC.readlines():
	name=line.strip()
	if not corpREVERSE.has_key(name): continue
	#print name,corpREVERSE[name]
	PACSET.add(corpREVERSE[name])

for corpID in PACSET:
	corpSET.remove(corpID)
for corpID in corpSET:
	countSQL = "SELECT COUNT(plt_id) FROM kb3_pilots WHERE plt_crp_id = "+str(corpID)+";"
	if corpID in PACSET:
		continue
	cursor.execute(countSQL)
	row = cursor.fetchone()
	nPilots = int(row[0])
	if corpREALSIZE.has_key(corpID): corpREALSIZE[corpID][1]=nPilots
	else: corpREALSIZE[corpID] = [0,nPilots]

print len(corpSET)
print corpSET
for i in range(1,12):
	startdate = datetime.datetime.combine(datetime.date(2012,i,1),datetime.time(0,0,0))
	if i != 12: enddate = datetime.datetime.combine(datetime.date(2012,i+1,1),datetime.time(0,0,0))
	else: enddate = datetime.datetime.combine(datetime.date(2013,1,1),datetime.time(0,0,0))
	for corpID in corpSET:

		memSQL = "SELECT COUNT(plt_id) FROM kb3_pilots WHERE plt_crp_id = "+str(corpID)+" AND plt_updated < \""+str(startdate)+"\";";
		
		cursor.execute(memSQL)
		memRES = cursor.fetchone()
		nPilots = int(memRES[0])
		corpSIZE[corpID][i] = nPilots
		#print memSQL,corpID,nPilots

		lossSQL = "SELECT COUNT(kll_victim_id) FROM kb3_kills WHERE kll_timestamp > \""+str(startdate)+"\" AND kll_timestamp < \""+str(enddate)+"\" AND kll_all_id=499 AND kll_crp_id = "+str(corpID)+";"
		cursor.execute(lossSQL)
		lossRES = cursor.fetchall()
		for row in lossRES:
			nKills = int(row[0])
			#corpID = int(row[1])
			corpDEATH[corpID][i]=nKills


		killSQL = "SELECT COUNT(ind_plt_id) FROM kb3_inv_detail WHERE ind_timestamp > \""+str(startdate)+"\" AND ind_timestamp < \""+str(enddate)+"\" AND ind_all_id = 499 AND ind_crp_id = "+str(corpID)+";"
		cursor.execute(killSQL)
		killRES = cursor.fetchall()
		for row in killRES:
			nKills = int(row[0])
			#corpID = int(row[1])
			corpKILLS[corpID][i]=nKills
		

outfile = open("outfile.out",'w')
for corpID in corpSET:
	outline = str(corpID)+" "+str(corpREALSIZE[corpID][0])+" "+str(corpREALSIZE[corpID][1])+" "
	for i in range(1,12):
		outline += str(corpDEATH[corpID][i])+" "
	for i in range(1,12):
		outline += str(corpKILLS[corpID][i])+" "
	for i in range(1,12):
		outline += str(corpSIZE[corpID][i])+" "
	outfile.write(outline+"\n")
	
outfile.close()