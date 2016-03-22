import MySQLdb
import urllib2
import xml.etree.cElementTree as ET

locations = dict()
#locations[30002187] = "Amarr"
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
				jitaSellMin = 100000
				jitaBuyMax = 1000000000
			elif jitaSellMin == 0:
				jitaSellMin = jitaBuyMax
			elif jitaBuyMax == 0:
				jitaBuyMax = jitaSellMin
			prices[itemID][location] = (jitaSellMin,jitaBuyMax)
	return prices
		#print prices,itemID,location,jitaSellMax,jitaBuyMin

def findAllProducts(cursor,item):
	sqlName = "SELECT types.typeNAME,types.groupID,types.published FROM invTypes as types WHERE types.typeID="+str(item)+";"
	cursor.execute(sqlName)
	row1 = cursor.fetchone()
	productNames[item] = row1[0]
	outProducts = set()
	sql= "SELECT typeID FROM ramTypeRequirements WHERE requiredTypeID="+str(item)+";"
	cursor.execute(sql)
	results=cursor.fetchall()
	for row in results:
		pid = int(row[0])
		sqlName = "SELECT types.typeNAME,types.groupID,types.published FROM invTypes as types WHERE types.typeID="+str(pid)+";"
		cursor.execute(sqlName)
		row = cursor.fetchone()
		name = row[0]
		productNames[pid] = name
		blueprintIDs[name] = pid
		name2 = name.replace(" Blueprint","")
		sqlID = "SELECT types.typeID,types.groupID,types.published FROM invTypes as types WHERE typeNAME=\""+name2+"\";"
		cursor.execute(sqlID)
		row2 = cursor.fetchone()
		if not row2:
			#print name,name2
			continue
		newid = int(row2[0])
		groupID = int(row2[1])
		groupIDs[newid] = groupID
		published = int(row2[2])
		productNames[newid] = name2
		#if groupID in badGroups or published == 0 or newid in listOfSimple or newid in listOfComplex or newid in listOfT2: continue
		if published == 0: continue
		outProducts.add(newid)
	sql= "SELECT typeID,quantity FROM invTypeMaterials WHERE materialTypeID="+str(item)+";"
	cursor.execute(sql)
	results=cursor.fetchall()
	for row in results:
		newID = int(row[0])
		outProducts.add(int(row[0]))
	removeProducts = set()
	for pid in outProducts:
		sqlName = "SELECT types.typeNAME,types.groupID,types.published FROM invTypes as types WHERE types.typeID="+str(pid)+";"
		cursor.execute(sqlName)
		row = cursor.fetchone()
		name = row[0]
		published = int(row[2])
		groupID = int(row[1])
		groupIDs[pid] = groupID
		productNames[pid] = name
		#if groupID in badGroups or published == 0 or pid in listOfSimple or pid in listOfComplex or pid in listOfT2:
		if published == 0:
			removeProducts.add(pid)
			continue
	outProducts -= removeProducts
	return outProducts

def getIngredients(cursor,item):
	pname = productNames[item]
	pname += " Blueprint"
	moreStuff = set()
	ingredients = []
	#if item == 12005: print pname, blueprintIDs[pname]
	if blueprintIDs.has_key(pname):
		pid = blueprintIDs[pname]
		sql="SELECT ram.requiredTypeID,ram.quantity,types.groupID,types.published,types.typeName FROM ramTypeRequirements as ram INNER JOIN invTypes as types ON types.typeID=ram.requiredTypeID WHERE ram.typeID="+str(pid)+";"
		cursor.execute(sql)
		results=cursor.fetchall()
		#print item,len(results)
		for row in results:
			reqID = int(row[0])
			reqQU = int(row[1])
			groupID = int(row[2])
			published = int(row[3])
			nname = row[4]
			productNames[reqID] = nname
			groupIDs[reqID] = groupID
			if published == 0: continue
			if groupID == 268: continue
			if groupID == 1041: continue
			if groupID == 1048: continue
			if groupID == 526: continue
			#if groupID in badGroups: continue
			ingredients.append((reqID,reqQU))
			if  reqID in listOfSimple or reqID in listOfComplex or reqID in listOfT2: continue
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
		#if groupID in badGroups or published == 0: continue
		if published == 0: continue
		ingredients.append((reqID,quantity))
		#if  reqID in listOfSimple or reqID in listOfComplex or reqID in listOfT2: continue
		moreStuff.add(reqID)
	return ingredients,moreStuff


def printList(resourceID,resources,volume,results):
	thisResource = resources[resourceID]
	if len(thisResource.ingredients) == 0:
		if results.has_key(resourceID):
			results[resourceID] += volume 
		else:
			results[resourceID] = volume
	else:
		for ing in thisResource.ingredients:
			printList(ing[0],resources,volume*ing[1]/float(thisResource.nProduced),results)
	return




resources = dict()

thingNames = dict()

listOfT2Salvage = [i for i in range(25607,25626)]

#print len(listOfP1),len(listOfP2),len(listOfP3),len(listOfP4)

blueprintIDs = dict()



db = MySQLdb.connect(host="localhost",user="root",port=3306,db="eve_static",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()

allThings = set()

thingsToMake = set()
thingsToMakeReqs = dict()
otherThingsToBuy = set()
productsToMake = set()
productNames = dict()
groupIDs = dict()


for item in listOfT2Salvage:
	allThings.add(item)
	productsToMake.update(findAllProducts(cursor,item))

allThings.update(productsToMake)
ingredientsDict = dict()
for item in productsToMake:
	ingredients,moreStuff = getIngredients(cursor,item)
	allThings.update(moreStuff)
	ingredientsDict[item] = ingredients

nThings = len(allThings)
while True:
	moreThings = set()
	for item in allThings:
		if ingredientsDict.has_key(item): continue
		ingredients,moreStuff = getIngredients(cursor,item)
		moreThings.update(moreStuff)
		ingredientsDict[item] = ingredients
	allThings.update(moreThings)
	if nThings == len(allThings):break
	else: nThings = len(allThings)

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


productIngredients = dict()

for k in allThings:
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
	results = dict()
	printList(item,resources,1,results)
	totalCost = 0
	productIngredients[item] = results
	if max(r.sellCost,r.buyCost) < r.produceCostSell:
		print "----------------------"
		print productNames[item]+" produce: "+str(resources[item].produceCostSell)+" buy: "+str(resources[item].sellCost)
		print "----------------------"
		for k,v in results.iteritems():
			print productNames[k],v,prices[k][30000142][1]