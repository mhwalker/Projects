import MySQLdb
import urllib2
import xml.etree.cElementTree as ET

#locationNOL = 30004712
locationNOL = 30004306 #Karan
locationJita = 30000142

def getPrices(locations,requestStr):
	prices = dict()
	print requestStr
	for location,name in locations.iteritems():	
		jitaRequest = urllib2.Request('http://api.eve-central.com/api/marketstat?sethours=12&usesystem='+str(location)+requestStr)
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
			prices[itemID][location] = (jitaSellMin,jitaBuyMax,jitaSellVolume)
	return prices
		#print prices,itemID,location,jitaSellMax,jitaBuyMin

def processItem(prices,thingName,thingVolume):
	bestSell2Sell = (0,0,0)
	bestBuy2Sell = (0,0,0)
	bestSell2Buy = (0,0,0)
	bestStation = (0,0)
	line0 = thingName+" "+str(thingVolume)+"-----------------------------"
	linestat = ""
	importCost = thingVolume*250.0
	if prices[locationNOL][2] == 0:
		#print line0
		return
	buyFromSellCost = prices[locationJita][0] + importCost
	buyFromBuyCost = prices[locationJita][1] + importCost
	sellValue = prices[locationNOL][0]
	if sellValue < buyFromBuyCost: return
	if (sellValue - buyFromBuyCost - importCost*thingVolume)/buyFromBuyCost < 0.2: return
	#if (sellValue - buyFromBuyCost) > 100000 or (sellValue - buyFromBuyCost)/buyFromBuyCost > 0.2: 
	#	line0 = "\033[1m\033[95m"+line0
	#	linestat = linestat+"\033[0m"
	print line0
	print "buy from Jita buy cost:",buyFromBuyCost,sellValue-importCost*thingVolume,prices[locationNOL][2],sellValue-buyFromBuyCost-importCost*thingVolume,(sellValue-buyFromBuyCost-importCost*thingVolume)/buyFromBuyCost
	#print "buy from Jita sell cost:",buyFromSellCost,sellValue,prices[locationNOL][2],sellValue-buyFromSellCost,(sellValue-buyFromSellCost)/buyFromSellCost
	#print linestat
	
	
	return
		
locations = dict()
#locations[30002187] = "Amarr"
locations[30000142] = "Jita"
#locations[30002510] = "Rens"
#locations[30002659] = "Dodixie"
#locations[30002053] = "Hek"
#locations[30004712] = "NOL-M9"
locations[30004306] = "Karan"
#locations[30001978] = "X-7OMU"

importCost =400

thingNames = dict()
thingVolumes = dict()
allThings = []
ships = [32878,24688,621,642,4306,4302,12034] #ships
modules = [1952,2048,10190,11616, 6295,5945,3841,2281,2303,2024,3090,7453, 1541,2301,8641,16487,1353,5975, 1447,12058,20224,8585,2032, 8529,527,3244, 519, 1999,2969,9457, 2897, 12267, 19952, 19946, 21096, 11578, 2605,2364, 11269, 11644, 20353, 3057, 5051, 11648, 11644, 11642, 2262, 16447, 16455,27914, 8117,3831] #modules
ammo = [12620,12801,12803,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,27912,27916,27918,27920,27924, 27359, 21740, 22993] #ammo
rigs = [26084,26088,31360,31790,31802,25948,31370,31372,31324,31718,31730,31742,31754, 25894, 25972, 26388, 31059,31360]
implants = []
drones = [23707,2488]

allThings.extend(modules)
allThings.extend(rigs)
allThings.extend(ships)
allThings.extend(drones)
allThings.extend(ammo)

db = MySQLdb.connect(host="localhost",user="root",port=3306,db="eve_static",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()

prices = dict()
requestStr = ""
for index,item in enumerate(allThings):
	prices[item] = dict()
	requestStr += "&typeid="+str(item)
	sqlName = "SELECT types.typeNAME,types.volume FROM invTypes as types WHERE types.typeID="+str(item)+";"
	cursor.execute(sqlName)
	nameRes = cursor.fetchone()
	name=nameRes[0]
	volume = float(nameRes[1])
	thingNames[item] = name
	thingVolumes[item] = volume
	if index % 30 == 0:
		theprices = getPrices(locations,requestStr)
		prices.update(theprices)
		requestStr = ""

thingVolumes[32878] = 5000 #talwar
thingVolumes[24688] = 50000 #Rokh
thingVolumes[621] = 10000 #caracal
thingVolumes[642] = 50000 #apoc
thingVolumes[4306] = 15000 #naga
thingVolumes[4302] = 15000 #oracle
thingVolumes[12034] = 2500 #hound

theprices = getPrices(locations,requestStr)
prices.update(theprices)

print "====================================="
print "===============Ships================="
print "====================================="

for item in ships: print item,thingNames[item]

print "====================================="
print "===============Rigs=================="
print "====================================="

for item in rigs: print item,thingNames[item]

print "====================================="
print "===============Ammo=================="
print "====================================="

for item in ammo: print item,thingNames[item]

print "====================================="
print "===============Mods=================="
print "====================================="

for item in modules: print item,thingNames[item]

print "====================================="
print "====================================="
print "====================================="

for item in allThings:
	processItem(prices[item],thingNames[item],thingVolumes[item])
