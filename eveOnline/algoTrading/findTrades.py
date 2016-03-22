import MySQLdb
import urllib2
import xml.etree.cElementTree as ET
import operator
import matplotlib.pyplot as plt
import colorsys

locations = dict()
locations[30002187] = "Amarr"
locations[30000142] = "Jita"
#locations[30002510] = "Rens"
locations[30002659] = "Dodixie"
#locations[30002053] = "Hek"

def getPrices(locations,requestStr):
	prices = dict()
	#print requestStr
	for location,name in locations.iteritems():	
		jitaRequest = urllib2.Request('http://api.eve-central.com/api/marketstat?sethours=1&usesystem='+str(location)+requestStr)
		jitaResult = urllib2.urlopen(jitaRequest)
		#print name,requestStr
		jitaRoot = ET.fromstring(jitaResult.read())
		for item in jitaRoot[0].iter('type'):
			itemID = int(item.attrib['id'])
			if not prices.has_key(itemID): prices[itemID] = dict()
			jitaBuyVolume = int(item.find('buy').find('volume').text)
			jitaBuyMax = float(item.find('buy').find('max').text)
			jitaBuyMin = float(item.find('buy').find('min').text)
			jitaSellVolume = int(item.find('sell').find('volume').text)
			jitaSellMax = float(item.find('sell').find('max').text)
			jitaSellMin = float(item.find('sell').find('min').text)
			if jitaSellMin == 0 and jitaBuyMax == 0:
				jitaSellMin = 1000000
				jitaBuyMax = 1000000
			elif jitaSellMin == 0:
				jitaSellMin = jitaBuyMax
			elif jitaBuyMax == 0:
				jitaBuyMax = jitaSellMin
			prices[itemID][location] = (jitaSellMin,jitaBuyMax)
	return prices
		#print prices,itemID,location,jitaSellMax,jitaBuyMin

def getNames(cursor,items):
	names = dict()
	for item in items:
		querysimple = "SELECT typeName FROM invTypes WHERE typeID=%i;" % (item,)
		cursor.execute(querysimple)
		results = cursor.fetchall()
		for row in results:
			name = row[0]
			names[item] = name
	return names


db = MySQLdb.connect(host="localhost",user="testmetrics",passwd="t3stm3trics",db="MARKETHISTORY")
cursor = db.cursor()



query = "SELECT typeID,AVG(quantity*average) as avgmove,AVG((high-low)/low) as avgspread FROM history WHERE day > '2014-05-31 23:59:59' AND regionID=10000002 GROUP BY typeID ORDER BY avgmove DESC;"
cursor.execute(query)
rows = cursor.fetchall()

things = dict()

for row in rows:
    typeID = int(row[0])
    avgmove = float(row[1])
    avgspread = float(row[2])
    if avgmove < 200000000: break
    things[typeID] = dict()
    nquery = "SELECT low,average,high FROM history WHERE regionID=10000002 AND typeID="+str(typeID)+" ORDER BY day DESC limit 1;"
    cursor.execute(nquery)
    prices=cursor.fetchone()
    if prices is None: continue
    things[typeID][30000142] = (avgmove,avgspread,float(prices[0]),float(prices[1]),float(prices[2]))

query = "SELECT typeID,AVG(quantity*average) as avgmove,AVG((high-low)/low) as avgspread FROM history WHERE day > '2014-05-31 23:59:59' AND regionID=10000043 GROUP BY typeID ORDER BY avgmove DESC;"
cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    typeID = int(row[0])
    avgmove = float(row[1])
    avgspread = float(row[2])
    if not things.has_key(typeID): continue
    if avgmove < 100000000: break
    nquery = "SELECT low,average,high FROM history WHERE regionID=10000043 AND typeID="+str(typeID)+" ORDER BY day DESC limit 1;"
    cursor.execute(nquery)
    prices=cursor.fetchone()
    if prices is None: continue
    things[typeID][30002187] = (avgmove,avgspread,float(prices[0]),float(prices[1]),float(prices[2]))
    #things[typeID][30002187] = (avgmove,avgspread)

query = "SELECT typeID,AVG(quantity*average) as avgmove,AVG((high-low)/low) as avgspread FROM history WHERE day > '2014-05-31 23:59:59' AND regionID=10000032 GROUP BY typeID ORDER BY avgmove DESC;"
cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    typeID = int(row[0])
    avgmove = float(row[1])
    avgspread = float(row[2])
    if not things.has_key(typeID): continue
    if avgmove < 100000000: break
    nquery = "SELECT low,average,high FROM history WHERE regionID=10000032 AND typeID="+str(typeID)+" ORDER BY day DESC limit 1;"
    cursor.execute(nquery)
    prices=cursor.fetchone()
    if prices is None: continue
    things[typeID][30002659] = (avgmove,avgspread,float(prices[0]),float(prices[1]),float(prices[2]))
    #things[typeID][30002659] = (avgmove,avgspread)


db2 = MySQLdb.connect(host="localhost",user="testmetrics",passwd="t3stm3trics",db="eve_static")
cursor2 = db2.cursor()

#goodItems = []

prices = dict()
typeNames = dict()

requestStr = ""
for index,itemID in enumerate(things.keys()):
	prices[itemID] = dict()
	requestStr += "&typeid="+str(itemID)
	sqlName = "SELECT types.typeNAME FROM invTypes as types WHERE types.typeID="+str(itemID)+";"
	cursor2.execute(sqlName)
	nameRes = cursor2.fetchone()
	name=nameRes[0]
	typeNames[itemID] = name
	if index % 30 == 0:
		theprices = getPrices(locations,requestStr)
		prices.update(theprices)
		requestStr = ""

theprices = getPrices(locations,requestStr)
prices.update(theprices)

mostrecent = dict()

for item,info in things.iteritems():
    show = False
    goodspread = False
    bestspread = 0
    bestlocationpair = (0,0)
    for location,locname in locations.iteritems():
        if not info.has_key(location): continue
        spread = info[location][1]
        if spread > 0.08: goodspread = True
        for location2,locname2 in locations.iteritems():
            if not info.has_key(location2):continue
            diff = (prices[item][location][0] - prices[item][location2][1])/prices[item][location2][1]
            if diff > bestspread:
                bestspread = diff
                bestlocationpair = (location2,location)
    if bestspread > 0.2 and goodspread: show = True
    if show:
        print "========================================="
        print typeNames[item],item,"Best trade (%0.3f): %s to %s - buy %0.2f sell %0.2f" % (bestspread,locations[bestlocationpair[0]],locations[bestlocationpair[1]],prices[item][bestlocationpair[0]][1],prices[item][bestlocationpair[1]][0],)
        for location,locname in locations.iteritems():
            if not info.has_key(location): continue
            print "   %s average(%0.0f) spread(%0.3f) low(%0.2f) avg(%0.2f) high(%0.2f) - buy %0.2f sell %0.2f" % (locname,info[location][0],info[location][1],info[location][2],info[location][3],info[location][4],prices[item][location][1],prices[item][location][0])
