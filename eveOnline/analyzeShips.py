import MySQLdb
import urllib2
import xml.etree.cElementTree as ET
import operator
import matplotlib.pyplot as plt
import colorsys

locations = dict()
#locations[30002187] = "Amarr"
locations[30000142] = "Jita"
#locations[10000002] = "Forge"

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
		self.me = 0
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
	if len(thisResource.ingredients) == 0:
		if results.has_key(resourceID):
			results[resourceID] += volume 
		else:
			results[resourceID] = volume 
	else:
		for ing in thisResource.ingredients:
			printList(ing[0],resources,(volume)*ing[1]/float(thisResource.nProduced),results)
	return

def printListOld(resourceID,resources,volume,results,mecorr=0):
	thisResource = resources[resourceID]
	if thisResource.getCheapest() != thisResource.produceCost:
		if results.has_key(resourceID):
			results[resourceID] += volume + round(volume*mecorr)
		else:
			results[resourceID] = volume + round(volume*mecorr)
	else:
		newmecorr = 0
		if thisResource.me < 0:
			newmecorr = 0.1*(1.0-float(thisResource.me))
		for ing in thisResource.ingredients:
			printListOld(ing[0],resources,volume*ing[1]/float(thisResource.nProduced),results,newmecorr)
	return

def findItems(cursor,item):
	sqlName = "SELECT types.typeNAME,types.groupID,types.published,types.typeID FROM invTypes as types WHERE types.groupID="+str(item)+";"
	cursor.execute(sqlName)
	results = cursor.fetchall()
	retItems = set()
	for row in results:
		name = row[0]
		grpID = int(row[1])
		published = int(row[2])
		typeid = int(row[3])
		if published == 0: continue
		if "Ishukone" in name: continue
		productNames[typeid] = name
		#print name
		sqlBluePrint = "SELECT typeID,published FROM invTypes WHERE typeName=\""+name+" Blueprint\";"
		cursor.execute(sqlBluePrint)
		bpResults = cursor.fetchall()
		if len(bpResults) != 1: continue
		if int(bpResults[0][1]) == 0: continue
		retItems.add(typeid)
	return retItems	

def getIngredients(cursor,item):
	pname = productNames[item]
	pname += " Blueprint"
	moreStuff = set()
	ingredients = []
	#if item == 12005: print pname, blueprintIDs[pname]
	if blueprintIDs.has_key(pname):
		pid = blueprintIDs[pname]
		sql="SELECT ram.requiredTypeID,ram.quantity,types.groupID,types.published,types.typeName,ram.activityID FROM ramTypeRequirements as ram INNER JOIN invTypes as types ON types.typeID=ram.requiredTypeID WHERE ram.typeID="+str(pid)+";"
		cursor.execute(sql)
		results=cursor.fetchall()
		#print item,len(results)
		for row in results:
			reqID = int(row[0])
			reqQU = int(row[1])
			groupID = int(row[2])
			published = int(row[3])
			activityID = int(row[5])
			nname = row[4]
			activityID = int(row[5])
			if activityID != 1: continue
			productNames[reqID] = nname
			groupIDs[reqID] = groupID
			if activityID != 1: continue
			if published == 0: continue
			if groupID == 268: continue
			if groupID == 1041: continue
			if groupID == 1048: continue
			if groupID == 526: continue
			if groupID == 270: continue
			if groupID in badGroups: continue
			ingredients.append((reqID,reqQU))
			moreStuff.add(reqID)
	sql = "SELECT mat.materialTypeID,mat.quantity FROM invTypeMaterials as mat WHERE mat.typeID="+str(item)+";"
	cursor.execute(sql)
	results=cursor.fetchall()
	for row in results:
		quantity = int(row[1])
		reqID = int(row[0])
		sql = "SELECT types.typeNAME,types.groupID,types.published FROM invTypes as types WHERE types.typeID="+str(reqID)+";"
		cursor.execute(sql)
		row2 = cursor.fetchone()
		if not row2:
			#print name,name2
			continue
		groupID = int(row2[1])
		published = int(row2[2])
		nname = row2[0]
		productNames[reqID] = nname
		groupIDs[reqID] = groupID
		if groupID in badGroups or published == 0: continue
		ingredients.append((reqID,quantity))
		moreStuff.add(reqID)
	return ingredients,moreStuff
	
def finalItemProcessCost(item):
	print "----------------------"
	print productNames[item]+" "+str(resources[item].getCheapest())+" "+str(resources[item].sellCost)
	print "----------------------"
	results = dict()
	mecorr = 0
	if resources[item].me < 0:
		mecorr = 0.1*(1.0-float(resources[item].me))
	printListOld(item,resources,1,results,mecorr)
	totalCost = 0
	for k,v in results.iteritems():
		line = productNames[k]+" "+str(k)+" "+str(resources[k].getCheapest())+" "
		if resources[k].getCheapest() == resources[k].sellCost:
			line += locations[resources[k].sellCostLocation]
		else:
			line += locations[resources[k].buyCostLocation]
		line += " "+str(v)
		print line
	return

	
def finalItemProcess(item):
	#print "----------------------"
	#print productNames[item]#+" "+str(item)#+" "+str(resources[item].getCheapest())+" "+str(resources[item].sellCost)
	#print "----------------------"
	results = dict()
	mecorr = 0
	printList(item,resources,1,results)
	#print productNames[item]+","+str(prices[item][30000142][0])+","+str(prices[item][30000142][2])+","+str(prices[item][30000142][4])+","+str(prices[item][30000142][6])+","+str(prices[item][30000142][1])+","+str(prices[item][30000142][3])+","+str(prices[item][30000142][5])+","+str(prices[item][30000142][7])
	#print resources[item].ingredients
	totalCost = 0
	for k,v in results.iteritems():
		line = "%s - %0.2f" % (productNames[k],v,)
		#print line
		totalCost += v 
		if k in listOfRaw:
			totalVolume[k] += v * float(prices[item])
		#print productNames[item]+","+productNames[k]+","+str(v)+","+str(prices[k][30000142][0])+","+str(prices[k][30000142][2])+","+str(prices[k][30000142][1])+","+str(prices[k][30000142][3])
	#if results.has_key(16646) and results[16646]*prices[16646][30000142][1] / totalCost > 0.2: print productNames[item],totalCost,results[16646]*prices[16646][30000142][1] / totalCost
	productIngredients[item] = results
	return

def getPrices(locations,requestStr):
	prices = dict()
	#print requestStr
	for location,name in locations.iteritems():	
		#print name,requestStr,location
		jitaRequest = urllib2.Request('http://api.eve-central.com/api/marketstat?sethours=1&usesystem='+str(location)+requestStr)
		jitaResult = urllib2.urlopen(jitaRequest)
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


blueprintIDs = dict()
resources = dict()

allColors = dict()

productNames = dict()

allThings = set()

thingsToMake = set()
thingsToMakeReqs = dict()
otherThingsToBuy = set()
productsToMake = set()
groupIDs = dict()

badGroups = set((314,353,526,1194,332))

groupsOfInterest = [25,26,419,27,420]

db = MySQLdb.connect(host="localhost",user="root",port=3306,db="eve_static",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()

for group in groupsOfInterest:
	productsToMake.update(findItems(cursor,group))

allThings.update(productsToMake)

ingredientsDict = dict()
for item in productsToMake:
	ingredients,moreStuff = getIngredients(cursor,item)
	allThings.update(moreStuff)
	ingredientsDict[item] = ingredients


prices = dict()
requestStr = ""
nThings = len(allThings)
for index,item in enumerate(allThings):
	prices[item] = dict()
	requestStr += "&typeid="+str(item)
	sqlName = "SELECT types.typeNAME FROM invTypes as types WHERE types.typeID="+str(item)+";"
	cursor.execute(sqlName)
	nameRes = cursor.fetchone()
	#print item
	name=nameRes[0]
	productNames[item] = name
	if index % 100 == 0:
		theprices = getPrices(locations,requestStr)
		prices.update(theprices)
		requestStr = ""

theprices = getPrices(locations,requestStr)
prices.update(theprices)

for k in productsToMake:
	nproduct = 1
	name = productNames[k]
	newr = Resource(k,productNames[k],ingredientsDict[k],nproduct)
	newr.sellCost = prices[k][30000142][0]
	newr.buyCost = prices[k][30000142][1]
	resources[k] = newr

for k in allThings:
	if resources.has_key(k): continue
	ingredients = ingredientsDict[k] if ingredientsDict.has_key(k) else []
	newr = Resource(item,productNames[k],ingredients,1)
	newr.sellCost = prices[k][30000142][0]
	newr.buyCost = prices[k][30000142][1]
	resources[k] = newr


for item in productsToMake:
	r = resources[item]
	pc = 0
	pcs = 0
	totalVol = 0
	for v in r.ingredients:
		pc += v[1]*resources[v[0]].getCheapest()
		pcs += v[1]*resources[v[0]].sellCost
		totalVol += v[1]
	r.produceCost = pc/float(r.nProduced)
	r.produceCostSell = pcs/float(r.nProduced)

profitDict = dict()

for item in productsToMake:
	if resources[item].getCheapest() >= resources[item].buyCost: continue
	if item > 17000: continue
	if "Issue" in productNames[item]: continue
	if "Navy" in productNames[item]: continue
	if "Shipping" in productNames[item]: continue
	if "Quafe" in productNames[item]: continue
	if "Sukuuvestaa" in productNames[item]: continue
	profit = resources[item].sellCost-resources[item].getCheapest()
	profitDict[item] = profit
	#print productNames[item]+" "+str(item)+" "+str(resources[item].getCheapest())+" "+str(resources[item].sellCost)+" "+str(profit)+" "+str(profit/resources[item].getCheapest())
#	print "----------------------"
#	print productNames[item]+" "+str(item)+" "+str(resources[item].getCheapest())+" "+str(resources[item].sellCost)
#	print "----------------------"
#	results = dict()
#	printList(item,resources,1,results)
#	for k,v in results.iteritems():
#		line = productNames[k]+" "+str(k)+" "+str(resources[k].getCheapest())+" "
#		if resources[k].getCheapest() == resources[k].sellCost:
#			line += locations[resources[k].sellCostLocation]
#		else:
#			line += locations[resources[k].buyCostLocation]
#		line += " "+str(v)
#		print line

sorted_profit = sorted(profitDict.iteritems(), key=operator.itemgetter(1),reverse=True)

for kv in sorted_profit:
	if kv[1] < 0: continue
	item = kv[0]
	profit = kv[1]
	print productNames[item]+" "+str(item)+" "+str(resources[item].getCheapest())+" "+str(resources[item].sellCost)+" "+str(profit)+" "+str(profit/resources[item].getCheapest())
	
