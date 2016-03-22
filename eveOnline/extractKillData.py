import MySQLdb
import urllib2
import xml.etree.cElementTree as ET
import time
import datetime
import json

locations = dict()
locations[30002187] = "Amarr"
locations[30000142] = "Jita"

db = MySQLdb.connect(host="localhost",user="root",port=3306,db="zkb_skim",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()

allianceNames = dict()
allianceMembers = dict()
TESTfriends = set([498125261,1463354890,99002275,99001779,1727758877,99000819,99001471,1147488332,99002084,99000153,99001954,99002234,99000614,1399057309, 99001904,99001698,99000964,807486236,99002678,99001003,99002525,99003253,386292982])
CFC = set([1354830081,741557221,1220174199,99000211,1006830534,150097440,131511956,679584932,1695357456,99001443,151380924,1411711376])

allAlliances = TESTfriends | CFC
"""
allAlliances.discard(1354830081)
allAlliances.discard(99000964)
allAlliances.discard(386292982)
allAlliances.discard(1006830534)
allAlliances.discard(1463354890)
allAlliances.discard(1147488332)
allAlliances.discard(498125261)
allAlliances.discard(679584932)
allAlliances.discard(99000819)
allAlliances.discard(1695357456)
allAlliances.discard(99001443)
allAlliances.discard(99000211)
allAlliances.discard(99000153)
allAlliances.discard(807486236)
allAlliances.discard(1399057309)
allAlliances.discard(150097440)
allAlliances.discard(1411711376)
allAlliances.discard(99001698)
allAlliances.discard(99002275)
allAlliances.discard(99002084)
allAlliances.discard(741557221)
"""

print len(allAlliances)
for alliance in allAlliances:
	pagenumber = 1
	startTime="201307221100"
	now = datetime.datetime.utcnow()
	endTime = now.strftime("%Y%m%d%H%M")
	endTime = "201307291100"
	#print endTime
	#if alliance == 1354830081: pagenumber = 999
	#if alliance == 741557221: endTime = "201306081219"
	print alliance
	keepGoing = True
	while keepGoing:
	#	if pagenumber == 25:
	#		pagenumber=1
	#		timequery="SELECT killTime FROM kills WHERE allianceID="+str(alliance)+" ORDER BY killTime ASC LIMIT 1;"
	#		cursor.execute(timequery)
	#		row = cursor.fetchone()
	#		#print row[0]
	#		ntime = datetime.datetime.strptime(str(row[0]),"%Y-%m-%d %H:%M:%S")
	#		ntime = ntime + datetime.timedelta(0,60)
	#		endTime = ntime.strftime("%Y%m%d%H%M")
	#		#print endTime
		url="http://www.zkillboard.com/api/losses/allianceID/"+str(alliance)+"/startTime/"+startTime+"/endTime/"+endTime+"/page/"+str(pagenumber)+"/"
		#print url
		request = urllib2.Request(url)
		try:
			result = urllib2.urlopen(request)
		except urllib2.HTTPError,err:
			print "ERROR:",url,err.code
			if err.code == 403 or err.code == 500:
				time.sleep(8)
				continue
			else: break
		except urllib2.URLError, err:
			print "ERROR URL",url,err.reason
	
		try:		
			data = json.load(result)
		except ValueError:
			print "Decoding Failed",url
			time.sleep(8)
			continue			
		#print len(data)
		if len(data) == 0: keepGoing = False
		#xmlRoot = ET.fromstring(result.read())
		#if xmlRoot.find("result").find("error") is not None: break
		#if len(xmlRoot.find("result").iter("error")) > 0: break
		#kills = xmlRoot.find("result").find('rowset[@name="kills"]')
		#for kill in kills.iterfind('row[@killID]'):
		for kill in data:
			if kill is None: continue
			#killID = kill['killID']
			killID = kill['killID']
			if killID < 0: continue
			#print killID
			solarSystemID = kill['solarSystemID']
			killTime = kill['killTime']
			moonID = kill['moonID']

			victim = kill['victim']
			
			victimID = victim['characterID']
			victimName = str(victim['characterName'])
			corporationID = victim['corporationID']
			corporationName = str(victim['corporationName'])
			allianceID = victim['allianceID']
			allianceName = str(victim['allianceName'])
			factionID = victim['factionID']
			factionName = str(victim['factionName'])
			damageTaken = victim['damageTaken']
			shipType = victim['shipTypeID']
			
			#print killID,solarSystemID,killTime,moonID,victimID,victimName,corporationID,corporationName
			
			query1 = "INSERT INTO kills (killID, solarSystemID, killTime, moonID, victimID, victimName, corporationID, corporationName, allianceID, allianceName, factionID, factionName, damageTaken, shipTypeID) VALUES("
			query1 += str(killID)+","+str(solarSystemID)+",\""+killTime+"\","+str(moonID)+","+str(victimID)+",\""+victimName+"\","+str(corporationID)+",\""+corporationName+"\","
			query1 += str(allianceID)+",\""+allianceName+"\","+str(factionID)+",\""+factionName+"\","+str(damageTaken)+","+str(shipType)+") ON DUPLICATE KEY UPDATE victimID=victimID;"
			cursor.execute(query1)
			cursor.execute("commit")
			
			attackers = kill['attackers']
			for attacker in attackers:
				attackerID = attacker['characterID']
				attackerName = str(attacker['characterName'])
				aCorpID = attacker['corporationID']
				aCorpName = str(attacker['corporationName'])
				aAllianceID = attacker['allianceID']
				aAllianceName = str(attacker['allianceName'])
				aFactionID = attacker['factionID']
				aFactionName = str(attacker['factionName'])
				securityStatus = attacker['securityStatus']
				damageDone = attacker['damageDone']
				finalBlow = attacker['finalBlow']
				weaponType = attacker['weaponTypeID']
				shipTypeID = attacker['shipTypeID']

				query2 = "INSERT INTO attackers (killID, attackerID, attackerName, corporationID, corporationName, allianceID, allianceName, factionID, factionName, securityStatus, damageDone, finalBlow, weaponTypeID, shipTypeID) VALUES ("
				query2 += str(killID)+","+str(attackerID)+",\""+attackerName+"\","+str(aCorpID)+",\""+aCorpName+"\","+str(aAllianceID)+",\""+aAllianceName+"\","+str(aFactionID)+",\""+aFactionName+"\","+str(securityStatus)+","+str(damageDone)+","+str(finalBlow)+","+str(weaponType)+","+str(shipTypeID)
				query2 += ") ON DUPLICATE KEY UPDATE killID=killID;"
				cursor.execute(query2)
				cursor.execute("commit")
				
			items = kill['items']
			for item in items:
				itemID = item['typeID']
				flag = item['flag']
				qtyDestroyed = item['qtyDestroyed']
				qtyDropped = item['qtyDropped']
				query3 = "INSERT INTO items (killID, typeID, flag, qtyDropped, qtyDestroyed) VALUES ("
				query3 += str(killID)+","+str(itemID)+","+str(flag)+","+str(qtyDropped)+","+str(qtyDestroyed)
				query3 += ") ON DUPLICATE KEY UPDATE killID=killID;"
				cursor.execute(query3)
				cursor.execute("commit")
		
		pagenumber += 1
		time.sleep(8)