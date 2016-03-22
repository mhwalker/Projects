import MySQLdb
import datetime
import urllib2
import xml.etree.cElementTree as ET

packagedVolumes = dict()
packagedVolumes[25] = 2500 #Frigate
packagedVolumes[420] = 5000 #Destroyer
packagedVolumes[419] = 15000 #battlecruiser
packagedVolumes[834] = 2500 #stealth bomber
packagedVolumes[541] = 5000 #interdictor
packagedVolumes[324] = 2500 #assaultships
packagedVolumes[831] = 2500 #interceptor
packagedVolumes[26] = 10000 #cruiser
packagedVolumes[832] = 10000 #logistics
packagedVolumes[963] = 5000 #strategic cruiser
packagedVolumes[830] = 2500 #covops
packagedVolumes[28] = 20000 #industrial
packagedVolumes[27] = 50000 #battleship
packagedVolumes[833] = 10000 #force recon 
packagedVolumes[358] = 10000 #heavy assault ship
packagedVolumes[906] = 10000 #combat recon ship
packagedVolumes[31] = 500 #shuttle
packagedVolumes[543] = 3750 #exhumer

db = MySQLdb.connect(host="localhost",user="root",port=3306,db="TESTKB",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()

sql="SELECT COUNT(kills.kll_id) as total,ships.typeName,ships.typeID,ships.groupID FROM kb3_constellations as constellations, kb3_systems as systems, kb3_kills as kills, kb3_invtypes as ships WHERE kills.kll_timestamp > \"2012-11-01 00:00:00\" AND kills.kll_system_id = systems.sys_id AND systems.sys_con_id = constellations.con_id AND constellations.con_reg_id = 10000058 AND ships.typeID = kills.kll_ship_id AND kills.kll_all_id = 499 AND ships.groupID != 237 AND ships.groupID != 29 AND ships.groupID != 25 AND ships.groupID != 31 GROUP BY ships.typeID ORDER BY total DESC;"

cursor.execute(sql)
results = cursor.fetchall()
for row in results:
	total = int(row[0])
	if total < 19: continue
	name = row[1]
	shipid = int(row[2])
	shipClass = int(row[3])
	fountainRequest = urllib2.Request('http://api.eve-central.com/api/marketstat?sethours=28800&regionlimit=10000058&typeid='+str(shipid))
	jitaRequest = urllib2.Request('http://api.eve-central.com/api/marketstat?sethours=28800&usesystem=30000142&typeid='+str(shipid))
	fountainResult = urllib2.urlopen(fountainRequest)
	jitaResult = urllib2.urlopen(jitaRequest)
	fountainRoot = ET.fromstring(fountainResult.read())
	jitaRoot = ET.fromstring(jitaResult.read())
	fountainBuyVolume = int(fountainRoot[0][0].find('buy').find('volume').text)
	fountainBuyMax = float(fountainRoot[0][0].find('buy').find('max').text)
	fountainBuyMin = float(fountainRoot[0][0].find('buy').find('min').text)
	fountainSellVolume = int(fountainRoot[0][0].find('sell').find('volume').text)
	fountainSellMax = float(fountainRoot[0][0].find('sell').find('max').text)
	fountainSellMin = float(fountainRoot[0][0].find('sell').find('min').text)
	jitaBuyVolume = int(jitaRoot[0][0].find('buy').find('volume').text)
	jitaBuyMax = float(jitaRoot[0][0].find('buy').find('max').text)
	jitaBuyMin = float(jitaRoot[0][0].find('buy').find('min').text)
	jitaSellVolume = int(jitaRoot[0][0].find('sell').find('volume').text)
	jitaSellMax = float(jitaRoot[0][0].find('sell').find('max').text)
	jitaSellMin = float(jitaRoot[0][0].find('sell').find('min').text)
	importCost = packagedVolumes[shipClass]*300
	bestCaseProfit = round(float(fountainSellMax)*0.97-float(importCost)-float(jitaBuyMin)*1.03)
	worstCaseProfit = round(float(fountainSellMin)*0.97-float(importCost)-float(jitaSellMin)*1.03)
	if fountainSellVolume == 0:
		bestCaseProfit = round(float(jitaSellMax*1.5)*0.97-float(importCost)-float(jitaBuyMin)*1.03)
		worstCaseProfit = round(float(jitaSellMax*1.5)*0.97-float(importCost)-float(jitaSellMin)*1.03)
	print name+" "+str(total)+" import cost:"+str(importCost)+" best case profit: "+str(bestCaseProfit)+" worst case profit: "+str(worstCaseProfit)
	print "--Fountain buy:  volume: "+str(fountainBuyVolume)+" min: "+str(fountainBuyMin)+" max: "+str(fountainBuyMax)
	print "--Fountain sell: volume: "+str(fountainSellVolume)+" min: "+str(fountainSellMin)+" max: "+str(fountainSellMax)
	print "====--Jita buy:  volume: "+str(jitaBuyVolume)+" min: "+str(jitaBuyMin)+" max: "+str(jitaBuyMax)
	print "====--Jita sell: volume: "+str(jitaSellVolume)+" min: "+str(jitaSellMin)+" max: "+str(jitaSellMax)