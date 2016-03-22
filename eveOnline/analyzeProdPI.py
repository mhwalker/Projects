import MySQLdb
import urllib2
import xml.etree.cElementTree as ET

locations = dict()
locations[30002187] = "Amarr"
locations[30000142] = "Jita"

class Resource:
	def __init__(self,uniqueid,entryname,sequence,nproduced):
		self.id = uniqueid
		self.name = entryname
		self.ingredients = sequence
		self.nProduced = nproduced
		self.sellCost = 0
		self.buyCost = 0
		self.produceCost = 0
		self.produceCostSell = 0
		self.sellCostLocation = 30000142
		self.buyCostLocation = 30000142
		return
	def getCheapest(self):
		if self.produceCost == 0: return min(self.sellCost,self.buyCost)
		else: return min(self.sellCost,self.buyCost,self.produceCost)
	def __str__(self):
		return str(self.name)+" "+str(self.id)+" sell location: "+locations[self.sellCostLocation]+" sell cost: "+str(self.sellCost)+" buy cost: "+str(self.buyCost)+" produce cost (buy): "+str(self.produceCost)+" produce cost (sell): "+str(self.produceCostSell)
	def __repr__(self):
		return str(self.name)+" "+str(self.id)+" sell location: "+locations[self.sellCostLocation]+" sell cost: "+str(self.sellCost)+" buy cost: "+str(self.buyCost)+" produce cost (buy): "+str(self.produceCost)+" produce cost (sell): "+str(self.produceCostSell)

def printList(resourceID,resources,volume,results):
	thisResource = resources[resourceID]
	if thisResource.getCheapest() != thisResource.produceCost:
		line0 = thisResource.name+" "+str(thisResource.id)+" "+str(thisResource.getCheapest())+" "+str(volume)
		#print line0
		if results.has_key(resourceID):
			results[resourceID] += volume
		else:
			results[resourceID] = volume
	else:
		for ing in thisResource.ingredients:
			printList(ing[0],resources,volume*ing[1]/float(thisResource.nProduced),results)
	return

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


locations = dict()
locations[30002187] = "Amarr"
locations[30000142] = "Jita"
#locations[30002510] = "Rens"
#locations[30002659] = "Dodixie"
#locations[30002053] = "Hek"

resources = dict()

thingNames = dict()

listOfP4 = [2867,2868,2869,2870,2871,2872,2875,2876]




allThings = []
allThings.extend(listOfP4)

thingsToMake = set()
thingsToMakeReqs = dict()
otherThingsToBuy = set()
productsToMake = set()
productNames = dict()
productionTimes = dict()

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
	sqlProdTime = "SELECT productionTime FROM invBlueprintTypes WHERe blueprintTypeID = "+str(item)+";"
	cursor.execute(sqlProdTime)
	prodTimeRes = cursor.fetchone()
	prodTime = prodTimeRes[0]

	sqlName = "SELECT types.typeNAME FROM invTypes as types WHERE types.typeID="+str(item)+";"
	cursor.execute(sqlName)
	nameRes = cursor.fetchone()
	name=nameRes[0]
	name = name.replace(" Blueprint","")
	#print name,prodTime
	#print name
	sqlID = "SELECT types.typeID FROM invTypes as types WHERE types.typeNAME=\""+name+"\";"
	cursor.execute(sqlID)
	realID = int(cursor.fetchone()[0])
	productsToMake.add(realID)
	productionTimes[realID] = prodTime
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


for item in listOfP4:
	nproduced = 1
	importCost = 0
	newr = Resource(item,productNames[item],[],nproduced)
	newr.sellCost = prices[item][30000142][0]
	newr.buyCost = prices[item][30000142][1]
	resources[item] = newr


productCosts = dict()		
for item in productsToMake:
	productCosts[item] = dict()
	tag = 1
	for location,name in locations.iteritems():
		productCosts[item][location] = 0
		totVol = 0
		oppCost = 0
		piVol = 0
		for ingredient in thingsToMakeReqs[item]:
			#print ingredient
			ingID = ingredient[0]
			ingVol = ingredient[1]
			totVol += ingVol
			if resources.has_key(ingID):
				productCosts[item][location] += ingVol*resources[ingID].getCheapest()
				oppCost += ingVol*(resources[ingID].sellCost - resources[ingID].getCheapest())
				piVol += ingVol
				if ingVol > 1: tag = 0
			else:
				productCosts[item][location] += ingVol*prices[ingID][location][0]
		fom = float((prices[item][location][0] - productCosts[item][location]-oppCost)/piVol)
		profit = prices[item][location][0] - productCosts[item][location]
		pph = profit * 3600 / productionTimes[item]
		if tag >-1 and name == "Jita" and pph > 300000: print productNames[item]+" "+name+" "+str(totVol)+" "+str(piVol)+" "+str(productCosts[item][location])+" "+str(prices[item][location][0])+" "+str(profit)+" "+str(productionTimes[item]/3600)+" "+str(pph)
		#if tag == 1: print productNames[item]+" "+name+" "+str(totVol)+" "+str(piVol)+" "+str(productCosts[item][location])+" "+str(prices[item][location][0])+" "+str(prices[item][location][0] - productCosts[item][location]),str(oppCost),str((prices[item][location][0] - productCosts[item][location]-oppCost)),str(fom)#,thingsToMakeReqs[item]
