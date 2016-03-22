import MySQLdb
import urllib2
import xml.etree.cElementTree as ET

def getPrices(locations,requestStr):
	prices = dict()
	#print requestStr
	for location,name in locations.iteritems():	
		jitaRequest = urllib2.Request('http://api.eve-central.com/api/marketstat?sethours=28800&usesystem='+str(location)+requestStr)
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


locations = dict()
locations[30002187] = "Amarr"
locations[30000142] = "Jita"
#locations[30002510] = "Rens"
#locations[30002659] = "Dodixie"
#locations[30002053] = "Hek"

thingNames = dict()

listOfP1 = [2389,2390,2392,2393,2395,2396,2397,2398,2399,2400,2401,3779,9828,3645,3683]
listOfP2 = [44,2312,2317,2319,2321,2327,2328,2329,2463,3689,3691,3693,3695,3697,3725,3775,3828,9830,9832,9836,9838,9840,9842,15317]
listOfP3 = [2344,2345,2346,2348,2349,2351,2352,2354,2358,2360,2361,2366,2367,9834,9846,9848,12836,17136,17392,17898,28974]
listOfP4 = [2867,2868,2869,2870,2871,2872,2875,2876]

easyP4 = [2869,2870,2875]
medP4 = [2867,2871,2872]
hardP4 = [2868,2876]

inputPA = dict()
inputPA[44] = [(2399,40),(2400,40)]
inputPA[2312] = [(3779,40),(3683,40)]
inputPA[2317] = [(2392,40),(3683,40)]
inputPA[2319] = [(2393,40),(3645,40)]
inputPA[2321] = [(2397,40),(2392,40)]
inputPA[2327] = [(9828,40),(2397,40)]
inputPA[2328] = [(3645,40),(2398,40)]
inputPA[2329] = [(2396,40),(2399,40)]
inputPA[2463] = [(2398,40),(2393,40)]
inputPA[3689] = [(2398,40),(2399,40)]
inputPA[3691] = [(2390,40),(3683,40)]
inputPA[3693] = [(2395,40),(2393,40)]
inputPA[3695] = [(2397,40),(2396,40)]
inputPA[3697] = [(2392,40),(9828,40)]
inputPA[3725] = [(2396,40),(2395,40)]
inputPA[3775] = [(2393,40),(3779,40)]
inputPA[3828] = [(2400,40),(2398,40)]
inputPA[9830] = [(2389,40),(2390,40)]
inputPA[9832] = [(3645,40),(2390,40)]
inputPA[9836] = [(2401,40),(2400,40)]
inputPA[9838] = [(2389,40),(3645,40)]
inputPA[9840] = [(2389,40),(2401,40)]
inputPA[9842] = [(9828,40),(2401,40)]
inputPA[15317] = [(2395,40),(3779,40)]

inputPA[2344] = [(9832,10),(2317,10)]
inputPA[2345] = [(3697,10),(9830,10)]
inputPA[2346] = [(2312,10),(2319,10)]
inputPA[2348] = [(9838,10),(2317,10),(2329,10)]
inputPA[2349] = [(2328,10),(9832,10),(9836,10)]
inputPA[2351] = [(9842,10),(3828,10)]
inputPA[2352] = [(2327,10),(44,10)]
inputPA[2354] = [(2329,10),(3697,10)]
inputPA[2358] = [(3828,10),(2463,10),(3725,10)]
inputPA[2360] = [(3693,10),(3695,10)]
inputPA[2361] = [(15317,10),(2321,10)]
inputPA[2366] = [(3695,10),(9840,10),(3775,10)]
inputPA[2367] = [(3693,10),(2319,10),(3691,10)]
inputPA[9834] = [(2328,10),(9840,10)]
inputPA[9846] = [(2312,10),(3689,10),(9842,10)]
inputPA[9848] = [(3689,10),(9836,10)]
inputPA[12836] = [(2329,10),(2463,10)]
inputPA[17136] = [(3691,10),(9838,10)]
inputPA[17392] = [(2327,10),(2312,10)]
inputPA[17898] = [(2321,10),(9840,10)]
inputPA[28974] = [(3725,10),(3775,10)]

inputPA[2867] = [(2354,6),(17392,6),(17898,6)]
inputPA[2868] = [(2348,6),(9846,6),(2366,6)]
inputPA[2869] = [(2360,6),(17136,6),(2398,40)]
inputPA[2870] = [(9848,6),(2344,6),(2393,40)]
inputPA[2871] = [(2346,6),(9834,6),(12836,6)]
inputPA[2872] = [(2344,6),(2352,6),(2361,6)]
inputPA[2875] = [(2351,6),(28974,6),(3645,40)]
inputPA[2876] = [(2349,6),(2358,6),(2367,6)]

#print len(listOfP1),len(listOfP2),len(listOfP3),len(listOfP4)

allThings = []
allThings.extend(listOfP1)
allThings.extend(listOfP2)
allThings.extend(listOfP3)
allThings.extend(listOfP4)

thingsToMake = set()
thingsToMakeReqs = dict()
otherThingsToBuy = set()
productsToMake = set()
productNames = dict()

db = MySQLdb.connect(host="localhost",user="root",port=3306,db="eve_static",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()
for item in listOfP4:
	sql= "SELECT typeID FROM ramTypeRequirements WHERE requiredTypeID="+str(item)+";"
	cursor.execute(sql)
	results=cursor.fetchall()
	for row in results:
		thingsToMake.add(int(row[0]))

otherGroups = set()
itemsToNotMake = set()
for item in thingsToMake:
	sql="SELECT ram.requiredTypeID FROM ramTypeRequirements as ram,invTypes as types WHERE types.typeID=ram.requiredTypeID AND types.groupID=18 AND ram.typeID="+str(item)+";"
	cursor.execute(sql)
	results=cursor.fetchall()
	if len(results) > 0:
		itemsToNotMake.add(item)
		continue
	sqlName = "SELECT types.typeNAME FROM invTypes as types WHERE types.typeID="+str(item)+";"
	cursor.execute(sqlName)
	nameRes = cursor.fetchone()
	name=nameRes[0]
	name = name.replace(" Blueprint","")
	#print name
	sqlID = "SELECT types.typeID FROM invTypes as types WHERE types.typeNAME=\""+name+"\";"
	cursor.execute(sqlID)
	realID = int(cursor.fetchone()[0])
	productsToMake.add(realID)
	thingsToMakeReqs[realID] = []
	productNames[realID] = name
	sql="SELECT ram.requiredTypeID,ram.quantity,types.groupID FROM ramTypeRequirements as ram INNER JOIN invTypes as types ON types.typeID=ram.requiredTypeID WHERE ram.typeID="+str(item)+";"
	cursor.execute(sql)
	results=cursor.fetchall()
	#print item,len(results)
	for row in results:
		reqID = int(row[0])
		reqQU = int(row[1])
		groupID = int(row[2])
		if groupID == 268: continue
		thingsToMakeReqs[realID].append((reqID,reqQU))
		if groupID == 1041: continue
		if groupID == 1048: continue
		otherThingsToBuy.add(reqID)
		otherGroups.add(groupID)

#print otherGroups
thingsToMake -= itemsToNotMake
print len(productsToMake),len(otherThingsToBuy)
allThings.extend(otherThingsToBuy)
allThings.extend(productsToMake)
print len(allThings)

prices = dict()
requestStr = ""
for index,item in enumerate(allThings):
	prices[item] = dict()
	requestStr += "&typeid="+str(item)
	sqlName = "SELECT types.typeNAME FROM invTypes as types WHERE types.typeID="+str(item)+";"
	cursor.execute(sqlName)
	nameRes = cursor.fetchone()
	name=nameRes[0]
	productNames[item] = name
	if index % 30 == 0:
		theprices = getPrices(locations,requestStr)
		prices.update(theprices)
		requestStr = ""

theprices = getPrices(locations,requestStr)
prices.update(theprices)

for item in listOfP1:
	pname = productNames[item]
	jitabuy = prices[item][30000142][1]
	jitasell = prices[item][30000142][0]
	amarrbuy = prices[item][30002187][1]
	amarrsell = prices[item][30002187][0]
	line = pname+" "+str(item)+" jita buy: "+str(jitabuy)+" jita sell: "+str(jitasell)+" amarr buy: "+str(amarrbuy)+" amarr sell: "+str(amarrsell)
	if amarrsell < jitasell: line = "\033[1m\033[95m"+line+"\033[0m"
	print line
print "---------------------------"
print "---------------------------"
print "---------------------------"
print "---------------------------"
for item in listOfP3:
	pname = productNames[item]
	jitabuy = prices[item][30000142][1]
	jitasell = prices[item][30000142][0]
	amarrbuy = prices[item][30002187][1]
	amarrsell = prices[item][30002187][0]
	line = pname+" "+str(item)+" jita buy: "+str(jitabuy)+" jita sell: "+str(jitasell)+" amarr buy: "+str(amarrbuy)+" amarr sell: "+str(amarrsell)
	if amarrsell < jitasell: line = "\033[1m\033[95m"+line+"\033[0m"
	print line
print "---------------------------"
print "---------------------------"
print "---------------------------"
print "---------------------------"
for item in listOfP2:
	pname = productNames[item]
	jitabuy = prices[item][30000142][1]
	jitasell = prices[item][30000142][0]
	amarrbuy = prices[item][30002187][1]
	amarrsell = prices[item][30002187][0]
	line = pname+" "+str(item)+" jita buy: "+str(jitabuy)+" jita sell: "+str(jitasell)+" amarr buy: "+str(amarrbuy)+" amarr sell: "+str(amarrsell)
	if amarrsell < jitasell: line = "\033[1m\033[95m"+line+"\033[0m"
	print line
print "---------------------------"
print "---------------------------"
print "---------------------------"
print "---------------------------"
for item in listOfP4:
	pname = productNames[item]
	jitabuy = prices[item][30000142][1]
	jitasell = prices[item][30000142][0]
	amarrbuy = prices[item][30002187][1]
	amarrsell = prices[item][30002187][0]
	line = pname+" "+str(item)+" jita buy: "+str(jitabuy)+" jita sell: "+str(jitasell)+" amarr buy: "+str(amarrbuy)+" amarr sell: "+str(amarrsell)
	if amarrsell > jitasell: line = "\033[1m\033[95m"+line+"\033[0m"
	print line
print "---------------------------"
print "---------------------------"
print "---------------------------"
print "---------------------------"
for item in productsToMake:
	pname = productNames[item]
	jitabuy = prices[item][30000142][1]
	jitasell = prices[item][30000142][0]
	amarrbuy = prices[item][30002187][1]
	amarrsell = prices[item][30002187][0]
	line = pname+" "+str(item)+" jita buy: "+str(jitabuy)+" jita sell: "+str(jitasell)+" amarr buy: "+str(amarrbuy)+" amarr sell: "+str(amarrsell)
	if amarrsell > jitasell: line = "\033[1m\033[95m"+line+"\033[0m"
	print line