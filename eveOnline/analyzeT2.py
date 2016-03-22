import MySQLdb
import urllib2
import xml.etree.cElementTree as ET
import operator
import matplotlib.pyplot as plt
import colorsys

locations = dict()
#locations[30002187] = "Amarr"
#locations[30000142] = "Jita"
locations[10000002] = "Forge"

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
		self.sellCostLocation = 10000002
		self.buyCostLocation = 10000002
		self.me = 0
		return
	def getCheapest(self):
		if self.produceCost == 0: return min(self.sellCost,self.buyCost)
		else: return min(self.sellCost,self.buyCost,self.produceCost)
	def __str__(self):
		return str(self.name)+" "+str(self.id)+" sell location: "+locations[self.sellCostLocation]+" sell cost: "+str(self.sellCost)+" buy cost: "+str(self.buyCost)+" produce cost (buy): "+str(self.produceCost)+" produce cost (sell): "+str(self.produceCostSell)
	def __repr__(self):
		return str(self.name)+" "+str(self.id)+" sell location: "+locations[self.sellCostLocation]+" sell cost: "+str(self.sellCost)+" buy cost: "+str(self.buyCost)+" produce cost (buy): "+str(self.produceCost)+" produce cost (sell): "+str(self.produceCostSell)

def printList(resourceID,resources,volume,results,mecorr=0):
	thisResource = resources[resourceID]
	if len(thisResource.ingredients) == 0:
		if results.has_key(resourceID):
			results[resourceID] += volume + round(volume*mecorr)
		else:
			results[resourceID] = volume + round(volume*mecorr)
	else:
		newmecorr = 0
		if thisResource.me < 0:
			newmecorr = 0.1*(1.0-float(thisResource.me))
		for ing in thisResource.ingredients:
			printList(ing[0],resources,(volume+round(volume*mecorr))*ing[1]/float(thisResource.nProduced),results,newmecorr)
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
		if groupID in badGroups or published == 0 or newid in listOfSimple or newid in listOfComplex or newid in listOfT2: continue
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
		if groupID in badGroups or published == 0 or pid in listOfSimple or pid in listOfComplex or pid in listOfT2:
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
			if groupID in badGroups: continue
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
		if groupID in badGroups or published == 0: continue
		ingredients.append((reqID,quantity))
		if  reqID in listOfSimple or reqID in listOfComplex or reqID in listOfT2: continue
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
	if resources[item].me < 0:
		mecorr = 0.1*(1.0-float(resources[item].me))
	printList(item,resources,1,results,mecorr)
	#print productNames[item]+","+str(prices[item][30000142][0])+","+str(prices[item][30000142][2])+","+str(prices[item][30000142][4])+","+str(prices[item][30000142][6])+","+str(prices[item][30000142][1])+","+str(prices[item][30000142][3])+","+str(prices[item][30000142][5])+","+str(prices[item][30000142][7])
	#print resources[item].ingredients
	totalCost = 0
	for k,v in results.iteritems():
		line = "%s - %0.2f" % (productNames[k],v,)
		#print line
		totalCost += v * prices[k][10000002][1]
		if k in listOfRaw:
			totalVolume[k] += v * prices[item][10000002][8]
		#print productNames[item]+","+productNames[k]+","+str(v)+","+str(prices[k][30000142][0])+","+str(prices[k][30000142][2])+","+str(prices[k][30000142][1])+","+str(prices[k][30000142][3])
	#if results.has_key(16646) and results[16646]*prices[16646][30000142][1] / totalCost > 0.2: print productNames[item],totalCost,results[16646]*prices[16646][30000142][1] / totalCost
	productIngredients[item] = results
	if item == 28844:
		makePricePieChart(item,results)
		makeMoonPieChart(item,results)
		makeComparisonChart(item,results)
	mercuryUse[item] = results[16646]* prices[item][10000002][8] if results.has_key(16646) else 0
	hafniumUse[item] = results[16648]* prices[item][10000002][8] if results.has_key(16648) else 0
	caesiumUse[item] = results[16647]* prices[item][10000002][8] if results.has_key(16647) else 0
	#mercuryUse[item] = results[16646] if results.has_key(16646) else 0
	#hafniumUse[item] = results[16648] if results.has_key(16648) else 0
	#caesiumUse[item] = results[16647] if results.has_key(16647) else 0
	return

def getPrices(locations,requestStr):
	prices = dict()
	#print requestStr
	for location,name in locations.iteritems():	
		#print name,requestStr
		#jitaRequest = urllib2.Request('http://api.eve-central.com/api/marketstat?sethours=1&usesystem='+str(location)+requestStr)
		jitaRequest = urllib2.Request('http://element-43.com/market/api/marketstat/?regionlimit='+str(location)+requestStr)
		jitaResult = urllib2.urlopen(jitaRequest)
		#print name,requestStr
		jitaRoot = ET.fromstring(jitaResult.read())
		for item in jitaRoot[0].iter('type'):
			itemID = int(item.attrib['id'])
			#print itemID
			if not prices.has_key(itemID): prices[itemID] = dict()
			jitaBuyVolume = int(item.find('buy').find('volume').text)
			tempjbmax = item.find('buy').find('max').text
			if tempjbmax.strip() == "None": tempjbmax = 0
			jitaBuyMax = float(tempjbmax)
			tempjbmin = item.find('buy').find('min').text
			if tempjbmin.strip() == "None": tempjbmin = 0
			jitaBuyMin = float(tempjbmin)
			jitaBuyMedian = float(item.find('buy').find('median').text)
			jitaBuyAvg = float(item.find('buy').find('avg').text)
			jitaSellVolume = int(item.find('sell').find('volume').text)
			tempjsmax = item.find('sell').find('max').text
			if tempjsmax.strip() == "None": tempjsmax = 0
			jitaSellMax = float(tempjsmax)
			tempjsmin = item.find('sell').find('min').text
			if tempjsmin.strip() == "None": tempjsmin = 0
			jitaSellMin = float(tempjsmin)
			jitaSellMedian = float(item.find('sell').find('median').text)
			jitaSellAvg = float(item.find('sell').find('avg').text)
			temptraded7 = item.find('traded_last_7').text
			if temptraded7.strip() == "None": temptraded7 = 0
			tradedLast7 = int(temptraded7)
			if jitaSellMin == 0 and jitaBuyMax == 0:
				jitaSellMin = 1000000
				jitaBuyMax = 1000000
			elif jitaSellMin == 0:
				jitaSellMin = jitaBuyMax
			elif jitaBuyMax == 0:
				jitaBuyMax = jitaSellMin
			prices[itemID][location] = (jitaSellMin,jitaBuyMax,jitaSellVolume,jitaBuyVolume,jitaSellAvg,jitaBuyAvg,jitaSellMedian,jitaBuyMedian,tradedLast7)
	return prices
		#print prices,itemID,location,jitaSellMax,jitaBuyMin

def makeMoonPieChart(item,ingredients):
	plt.figure()
	values = []
	labels = []
	explode = []
	colors = []
	totalValue = 0
	for k,v in ingredients.iteritems():
		if k not in listOfRaw: continue
		values.append(v)
		labels.append(productNames[k])
		colors.append(allColors[k])
		totalValue += v
	
	line = "{p:.2f}%  ({v:.2f})"

	plt.pie(values,labels=labels,colors=colors,autopct=lambda( p ): line.format(p=p,v=p*totalValue/100.0))
	name = productNames[item]
	plt.title(name)
	name2 = name.replace(" ","")
	plt.savefig("moonGooFigures/pieMoonVol_"+name2+".png")
	plt.close()
	
	return


def makePricePieChart(item,ingredients):
	plt.figure()
	values = []
	labels = []
	explode = []
	colors = []
	totalValue = 0
	for k,v in ingredients.iteritems():
		values.append(v*prices[k][10000002][1])
		labels.append(productNames[k])
		colors.append(allColors[k])
		if k in listOfRaw:
			explode.append(0.05)
		else:
			explode.append(0.0)
		totalValue += v*prices[k][10000002][1]
	
	line = "{p:.2f}%  ({v:.2f}M)"
	if totalValue < 1000000: line = "{p:.2f}%  ({v:.2f}K)"

	if totalValue < 1000000: plt.pie(values,explode=explode,labels=labels,colors=colors,autopct=lambda( p ): line.format(p=p,v=p*totalValue/100.0/1000.0))
	else: plt.pie(values,explode=explode,labels=labels,colors=colors,autopct=lambda( p ): line.format(p=p,v=p*totalValue/100.0/1000000.0))
	name = productNames[item]
	if totalValue < 1000000: plt.title("%s total: %0.2fK" %(productNames[item],totalValue/1000.0,))
	else: plt.title("%s total: %0.2fM" %(productNames[item],totalValue/1000000.0,))
	name2 = name.replace(" ","")
	plt.savefig("moonGooFigures/piePrice_"+name2+".png")
	plt.close()
	
	return

def makeComparisonChart(item,ingredients):
	fig = plt.figure(figsize=(12,6))
	valuesCost = []
	valuesUnits = []
	labels = []
	colors = []
	totalCost = 0
	for k,v in ingredients.iteritems():
		if k in listOfInterest:
			valuesCost.append(v*prices[k][10000002][1])
			valuesUnits.append(v)
			labels.append(productNames[k])
			colors.append(allColors[k])
		totalCost += v*prices[k][10000002][1]
	name = productNames[item]	
	name2 = (name.replace(" ","")).replace("'","")
	for i in range(0,len(valuesCost)): valuesCost[i] /= totalCost
	ax1 = fig.add_subplot(121)
	ax1.bar(range(len(labels)),valuesCost,color=colors)
	ax1.set_ylabel("Fraction of Cost")
	ax1.set_xlabel("Ingredient")
	ax1.set_xlim(-1,len(labels)+1)
	ax1.set_xticks([i + 0.4 for i in range(len(labels))])
	ax1.set_xticklabels(labels,rotation=90,size=12)
	ax2 = fig.add_subplot(122)
	ax2.bar(range(len(labels)),valuesUnits,color=colors)
	ax2.set_ylabel("Units")
	ax2.set_xlabel("Ingredient")
	ax2.set_xlim(-1,len(labels)+1)
	ax2.set_xticks([i + 0.4 for i in range(len(labels))])
	ax2.set_xticklabels(labels,rotation=90,size=12)
	fig.subplots_adjust(bottom=0.3)
	fig.subplots_adjust(right=0.9)
	fig.subplots_adjust(left=0.1)
	fig.subplots_adjust(wspace=0.5)
	plt.title(name)
	plt.savefig("moonGooFigures/comparison_"+name2+".png")
	plt.close()
	



blueprintIDs = dict()
resources = dict()

allColors = dict()

thingNames = dict()

badGroups = set((314,353,526,1194,332))

listOfInterest = [16646,16644,16647,16648,16649,16650,16651]

listOfRaw = [16633,16634,16635,16636,16637,16638,16639,16640,16641,16642,16643,16644,16646,16647,16648,16649,16650,16651,16652,16653]
listOfSimple = [16654,16655,16656,16657,16658,16659,16660,16661,16662,16663,16664,16665,16666,16667,16668,16669,17769,17959,17960]
listOfComplex = [16670,16671,16672,16673,16678,16679,16680,16681,16682,16683,17317]

listOfT2 = [11530,11531,11532,11533,11534,11535,11536,11537,11538,11539,11540,11541,11542,11543,11544,11545,11547,11548,11549,11550,11551,11552,11554,11554,11555,11556,11557,11558,11688,11689,11690,11691,11692,11693,11694,11695,29039,29041,29043,29045,29047,29049,29051,29053,29055,29057,29059,29061,29063,29065,29067,29069, 29071,29073,29075,29077,29079,29081,29083,29085,29087,29091,29093,29095,29097,29099,29101,29103,29105,29107,29109]

inputRA = dict()
#Simple
inputRA[16661] = [((16634,100),(16635,100)),200]
inputRA[16658] = [((16635,100),(16636,100)),200]
inputRA[16660] = [((16635,100),(16636,100)),200]
inputRA[16659] = [((16633,100),(16636,100)),200]
inputRA[16655] = [((16640,100),(16643,100)),200]
inputRA[16656] = [((16639,100),(16642,100)),200]
inputRA[16654] = [((16638,100),(16641,100)),200]
inputRA[16657] = [((16637,100),(16644,100)),200]
inputRA[16665] = [((16641,100),(16644,100)),200]
inputRA[16663] = [((16643,100),(16647,100)),200]
inputRA[16664] = [((16641,100),(16647,100)),200]
inputRA[16662] = [((16644,100),(16649,100)),200]
inputRA[17959] = [((16642,100),(16648,100)),200]
inputRA[17960] = [((16643,100),(16652,100)),200]
inputRA[16666] = [((16642,100),(16652,100)),200]
inputRA[16669] = [((16648,100),(16650,100)),200]
inputRA[16668] = [((16646,100),(16650,100)),200]
inputRA[16667] = [((16646,100),(16651,100)),200]
inputRA[17769] = [((16651,100),(16653,100)),200]

#Complex
inputRA[16672] = [((16661,100),(16657,100)),10000]
inputRA[16671] = [((16658,100),(16654,100)),10000]
inputRA[16673] = [((16660,100),(16656,100)),10000]
inputRA[16670] = [((16659,100),(16655,100)),10000]
inputRA[16678] = [((16660,100),(16665,100)),6000]
inputRA[16679] = [((16659,100),(16662,100)),3000]
inputRA[16680] = [((16658,100),(16663,100),(17959,100)),2200]
inputRA[16681] = [((16661,100),(16662,100),(16667,100)),1500]
inputRA[16682] = [((16664,100),(17959,100),(16668,100)),750]
inputRA[16683] = [((16665,100),(17960,100),(16666,100),(16669,100)),400]
inputRA[17317] = [((16663,100),(17960,100),(16668,100),(17769,100)),200]

"""
#Amarr
inputRA[11543] = [((16672,40),(16678,30)),1]
inputRA[11557] = [((16672,28),(16678,11),(16683,1)),1]
inputRA[11554] = [((16672,24),(16679,15),(16681,1)),1]
inputRA[11689] = [((16672,39),(16679,14),(16682,1)),1]
inputRA[11538] = [((16672,17),(16680,1),(16681,7)),1]
inputRA[11694] = [((16672,28),(16680,8),(16681,3)),1]
inputRA[11532] = [((16672,17),(16680,4),(16683,1)),1]
inputRA[11537] = [((16672,20),(16681,1),(16682,2)),1]
inputRA[11549] = [((16672,11),(16683,1),(17317,1)),1]

#Caldari
inputRA[11544] = [((16671,46),(16678,35)),1]
inputRA[11558] = [((16671,23),(16678,9),(16683,1)),1]
inputRA[11552] = [((16671,28),(16679,17),(16681,1)),1]
inputRA[11690] = [((16671,32),(16679,12),(16682,1)),1]
inputRA[11540] = [((16671,14),(16680,1),(16681,6)),1]
inputRA[11693] = [((16671,23),(16680,7),(16681,2)),1]
inputRA[11533] = [((16671,14),(16680,3),(16683,1)),1]
inputRA[11534] = [((16671,23),(16681,1),(16682,2)),1]
inputRA[11550] = [((16671,9),(16683,1),(17317,1)),1]

#Minmatar
inputRA[11542] = [((16673,46),(16678,35)),1]
inputRA[11555] = [((16673,23),(16678,9),(16683,1)),1]
inputRA[11551] = [((16673,28),(16679,17),(16681,1)),1]
inputRA[11691] = [((16673,32),(16679,12),(16682,1)),1]
inputRA[11539] = [((16673,14),(16680,1),(16681,6)),1]
inputRA[11692] = [((16673,23),(16680,7),(16681,2)),1]
inputRA[11530] = [((16673,14),(16680,3),(16683,1)),1]
inputRA[11536] = [((16673,23),(16681,1),(16682,2)),1]
inputRA[11548] = [((16673,9),(16683,1),(17317,1)),1]

#Gallente
inputRA[11545] = [((16670,46),(16678,35)),1]
inputRA[11556] = [((16670,23),(16678,9),(16683,1)),1]
inputRA[11553] = [((16670,28),(16679,17),(16681,1)),1]
inputRA[11688] = [((16670,32),(16679,12),(16682,1)),1]
inputRA[11541] = [((16670,14),(16680,1),(16681,6)),1]
inputRA[11695] = [((16670,23),(16680,7),(16681,2)),1]
inputRA[11531] = [((16670,14),(16680,3),(16683,1)),1]
inputRA[11535] = [((16670,23),(16681,1),(16682,2)),1]
inputRA[11547] = [((16670,9),(16683,1),(17317,1)),1]
"""

db = MySQLdb.connect(host="localhost",user="root",port=3306,db="eve_static",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()

for item in listOfT2:
	sql="SELECT * FROM invTypeMaterials WHERE typeID="+str(item)+";"
	cursor.execute(sql)
	rows = cursor.fetchall()
	ingr=[[],1]
	for row in rows:
		ingr[0].append((int(row[1]),int(row[2])))
	#print item,ingr
	inputRA[item] = ingr

#print len(listOfP1),len(listOfP2),len(listOfP3),len(listOfP4)

allThings = set()

thingsToMake = set()
thingsToMakeReqs = dict()
otherThingsToBuy = set()
productsToMake = set()
productNames = dict()
groupIDs = dict()


for item in listOfT2:
	allThings.add(item)
	productsToMake.update(findAllProducts(cursor,item))

for item in listOfComplex:
	allThings.add(item)
	productsToMake.update(findAllProducts(cursor,item))

for item in listOfSimple:
	allThings.add(item)
	productsToMake.update(findAllProducts(cursor,item))

nRaw = len(listOfRaw)
for index,item in enumerate(listOfRaw):
	allThings.add(item)
	productsToMake.update(findAllProducts(cursor,item))
	allColors[item] = colorsys.hls_to_rgb(float(index/(1.0*nRaw)),0.5,0.5)

nProducts = len(productsToMake)
while True:
	moreProducts = set()
	for item in productsToMake:
		moreProducts.update(findAllProducts(cursor,item))
	productsToMake.update(moreProducts)
	if nProducts == len(productsToMake): break
	else: nProducts = len(productsToMake)

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
	if not allColors.has_key(item):
		allColors[item] = colorsys.hls_to_rgb(float(index/(5.0*nRaw)+0.8),0.5,0.5)
	if index % 100 == 0:
		theprices = getPrices(locations,requestStr)
		prices.update(theprices)
		requestStr = ""

theprices = getPrices(locations,requestStr)
prices.update(theprices)

t2me4 = set((358,834,830,324,893,831,541))
t2me3 = set()
t2me2 = set((358,894,832,833))
t2me1 = set((902,540,898,900))
	
for k in productsToMake:
	nproduct = 1
	name = productNames[k]
	if "Missile" in name or "Torpedo" in name: nproduct = 100
	elif "Javelin" in name or "Void" in name or "Null" in name or "Spike" in name: nproduct = 100
	elif "Aurora" in name or "Gleam" in name or "Conflagration" in name or "Scorch" in name:
		nproduct = 4
	elif "Tremor" in name or "Quake" in name or "Barrage" in name or "Hail" in name: nproduct = 5000
	newr = Resource(k,productNames[k],ingredientsDict[k],nproduct)
	newr.sellCost = prices[k][10000002][0]
	#if prices[k][10000002][0] > prices[k][30002187][0]:
	#	newr.sellCost = prices[k][30002187][0]
	#	newr.sellCostLocation = 30002187
	newr.buyCost = prices[k][10000002][1]
	if groupIDs[k] in t2me1: newr.me = -1
	elif groupIDs[k] in t2me4: newr.me = -4
	elif groupIDs[k] == t2me3: newr.me = -3
	elif groupIDs[k] == t2me2: newr.me = -2
	resources[k] = newr

for k,v in inputRA.iteritems():
	nproduced = 1
	importCost = 0
	newr = Resource(k,productNames[k],v[0],v[1])
	newr.sellCost = prices[k][10000002][0]
	#if prices[k][30000142][0] > prices[k][30002187][0]:
	#	newr.sellCost = prices[k][30002187][0]
	#	newr.sellCostLocation = 30002187
	newr.buyCost = prices[k][10000002][1]
	resources[k] = newr

for k in listOfRaw:
	nproduced = 1
	newr = Resource(k,productNames[k],[],nproduced)
	newr.sellCost = prices[k][10000002][0]
	#if prices[k][30000142][0] > prices[k][30002187][0]:
	#	newr.sellCost = prices[k][30002187][0]
	#	newr.sellCostLocation = 30002187
	newr.buyCost = prices[k][10000002][1]
	resources[k] = newr

for k in allThings:
	if resources.has_key(k): continue
	ingredients = ingredientsDict[k] if ingredientsDict.has_key(k) else []
	newr = Resource(item,productNames[k],ingredients,1)
	newr.sellCost = prices[k][10000002][0]
	#if prices[k][30000142][0] > prices[k][30002187][0]:
	#	newr.sellCost = prices[k][30002187][0]
	#	newr.sellCostLocation = 30002187
	newr.buyCost = prices[k][10000002][1]
	resources[k] = newr

for item in listOfSimple:
	r = resources[item]
	pc = 0
	pcs = 0
	for v in r.ingredients:
		pc += v[1]*resources[v[0]].getCheapest()
		pcs += v[1]*resources[v[0]].sellCost
	r.produceCost = pc/float(r.nProduced)
	r.produceCostSell = pcs/float(r.nProduced)

for item in listOfComplex:
	r = resources[item]
	pc = 0
	pcs = 0
	for v in r.ingredients:
		pc += v[1]*resources[v[0]].getCheapest()
		pcs += v[1]*resources[v[0]].sellCost
	r.produceCost = pc/float(r.nProduced)
	r.produceCostSell = pcs/float(r.nProduced)

for item in listOfT2:
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

#for k in listOfRaw:
#	print resources[k]

#print "--------------------------------------------"
#print "--------------------------------------------"

#for k in listOfSimple:
#	print resources[k]

#print "--------------------------------------------"
#print "--------------------------------------------"

#for k in listOfComplex:
#	print resources[k]

#for k,r in resources.iteritems():
#	print r

#print "--------------------------------------------"
#print "--------------------------------------------"

#for item in listOfT2:
#	print resources[item]

#print "--------------------------------------------"
#print "--------------------------------------------"
#print "--------------------------------------------"
#print "--------------------------------------------"


#for item in listOfT2:
#	print resources[item]

totalVolume = dict()
for item in listOfRaw:
	totalVolume[item] = 0

productIngredients = dict()
mercuryUse = dict()
hafniumUse = dict()
caesiumUse = dict()

for item in productsToMake:
	finalItemProcess(item)


print "--------------------------------------------"
print "--------------------------------------------"
print "--------------------------------------------"
print "------------\/Products\/--------------------"

for k,v in totalVolume.iteritems():
	print "%s - %0.2f" % (productNames[k],v,)

print "-------------^Products^---------------------"
print "--------------\/Raw\/-----------------------"

for item in listOfRaw:
	totalVolume[item] = 0

for item in listOfRaw:
	finalItemProcess(item)

for k,v in totalVolume.iteritems():
	print "%s - %0.2f" % (productNames[k],v,)

print "----------------^Raw^-----------------------"
print "--------------\/Simple\/--------------------"

for item in listOfRaw:
	totalVolume[item] = 0

for item in listOfSimple:
	finalItemProcess(item)

for k,v in totalVolume.iteritems():
	print "%s - %0.2f" % (productNames[k],v,)

print "----------------^Simple^--------------------"
print "--------------\/Complex\/-------------------"

for item in listOfRaw:
	totalVolume[item] = 0


for item in listOfComplex:
	finalItemProcess(item)

for k,v in totalVolume.iteritems():
	print "%s - %0.2f" % (productNames[k],v,)

print "---------------^Complex^--------------------"
print "----------------\/T2\/----------------------"

for item in listOfRaw:
	totalVolume[item] = 0

for item in listOfT2:
	finalItemProcess(item)

for k,v in totalVolume.iteritems():
	print "%s - %0.2f" % (productNames[k],v,)

print "-----------------^T2^-----------------------"
print "--------------------------------------------"


sorted_merc = sorted(mercuryUse.iteritems(), key=operator.itemgetter(1),reverse=True)
sorted_hafn = sorted(hafniumUse.iteritems(), key=operator.itemgetter(1),reverse=True)
sorted_caes = sorted(caesiumUse.iteritems(), key=operator.itemgetter(1),reverse=True)

#for kv in sorted_merc:
#	if kv[1] > 0: print "%s - %0.2f" % (productNames[kv[0]],kv[1],)

#print "--------------------------------------------"
#print "--------------------------------------------"

#for kv in sorted_hafn:
#	if kv[1] > 0: print "%s - %0.2f" % (productNames[kv[0]],kv[1],)


#print "--------------------------------------------"
#print "--------------------------------------------"
#for kv in sorted_caes:
#	if kv[1] > 0: print "%s - %0.2f" % (productNames[kv[0]],kv[1],)

print "--------------------------------------------"
print "------------\/Products\/--------------------"

for item in productsToMake:
	finalItemProcessCost(item)

print "-------------^Products^---------------------"
print "--------------\/Raw\/-----------------------"

for item in listOfRaw:
	finalItemProcessCost(item)

print "----------------^Raw^-----------------------"
print "--------------\/Simple\/--------------------"

for item in listOfSimple:
	finalItemProcessCost(item)


print "----------------^Simple^--------------------"
print "--------------\/Complex\/-------------------"


for item in listOfComplex:
	finalItemProcessCost(item)


print "---------------^Complex^--------------------"
print "----------------\/T2\/----------------------"

for item in listOfT2:
	finalItemProcessCost(item)

print "-----------------^T2^-----------------------"
print "--------------------------------------------"


#for item in listOfT2:
#	print "inputRA["+str(item)+"] =",resources[item].ingredients,resources[item].nProduced