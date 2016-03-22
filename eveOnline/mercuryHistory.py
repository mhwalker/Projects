import MySQLdb
import urllib2
import xml.etree.cElementTree as ET
import operator
import matplotlib.pyplot as plt
import colorsys
import matplotlib.dates as mdates

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
		self.prices = dict()
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
	

	
def finalItemProcess(item):
	results = dict()
	mecorr = 0
	if resources[item].me < 0:
		mecorr = 0.1*(1.0-float(resources[item].me))
	printList(item,resources,1,results,mecorr)
	totalCost = 0
	productIngredients[item] = results
	return

def getPrices(cursor,locations,listOfItems):
	prices = dict()
	#print requestStr
	for item in listOfItems:
		prices[item] = dict()
		for location,name in locations.iteritems():	
			sql = "SELECT * FROM history WHERE regionID="+str(location)+" AND typeID="+str(item)+" AND day > \"2012-08-31 12:00:00\" AND day < \"2013-03-01 00:00:00\";"
			cursor.execute(sql)
			rows = cursor.fetchall()
			prices[item][location] = dict()
			for row in rows:
				prices[item][location][row[7]] = [int(row[3]),float(row[4]),float(row[5]),float(row[6])]
	return prices

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
	
def makeMercuryVolumesChart(item,dates,inputVolumes,outputVolumes):
	plt.figure()
	fig,ax = plt.subplots()
	axes = [ax,ax.twinx()]
	colors = ['Green','Red']
	labels = ['Input Volume','Product Volume']
	datas = [inputVolumes,outputVolumes]
	fig.subplots_adjust(left=0.15,right=0.85,bottom=0.2)
	for i,ax in enumerate(axes):
		ax.plot(dates,datas[i],'-',color=colors[i])
		ax.set_ylabel(labels[i],color=colors[i])
		ax.tick_params(axis='y', colors=colors[i])
		dmax = max(datas[i])
		ax.set_ylim((0,4500000))
	axes[0].set_xlabel('Date')
	ticks = []
	for i in range(0,len(dates)):
		if i % 10 == 0: ticks.append(dates[i])
	axes[0].set_xticks(ticks)
	axes[0].set_xticklabels([date.strftime("%Y-%m-%d") for date in ticks],rotation=90)
	fig.autofmt_xdate()
	axes[0].fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
	name = productNames[item]	
	name2 = (name.replace(" ","")).replace("'","")
	plt.title(name)
	plt.savefig("moonGooFigures/volumes_"+name2+".png")
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

listOfT2 = [11530,11531,11532,11533,11534,11535,11536,11537,11538,11539,11540,11541,11542,11543,11544,11545,11547,11548,11549,11550,11551,11552,11554,11554,11555,11556,11557,11558,11688,11689,11690,11691,11692,11693,11694,11695]

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

db2 = MySQLdb.connect(host="localhost",user="root",port=3306,db="MARKETHISTORY",unix_socket="/var/mysql/mysql.sock")
cursor2 = db2.cursor()


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
	sqlName = "SELECT types.typeNAME FROM invTypes as types WHERE types.typeID="+str(item)+";"
	cursor.execute(sqlName)
	nameRes = cursor.fetchone()
	#print item
	name=nameRes[0]
	productNames[item] = name
	if not allColors.has_key(item):
		allColors[item] = colorsys.hls_to_rgb(float(index/(5.0*nRaw)+0.8),0.5,0.5)

prices = getPrices(cursor2,locations,allThings)

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
	newr.prices = prices[k][10000002]
	if groupIDs[k] in t2me1: newr.me = -1
	elif groupIDs[k] in t2me4: newr.me = -4
	elif groupIDs[k] == t2me3: newr.me = -3
	elif groupIDs[k] == t2me2: newr.me = -2
	resources[k] = newr

for k,v in inputRA.iteritems():
	nproduced = 1
	importCost = 0
	newr = Resource(k,productNames[k],v[0],v[1])
	newr.prices = prices[k][10000002]
	resources[k] = newr

for k in listOfRaw:
	nproduced = 1
	newr = Resource(k,productNames[k],[],nproduced)
	newr.prices = prices[k][10000002]
	resources[k] = newr

for k in allThings:
	if resources.has_key(k): continue
	ingredients = ingredientsDict[k] if ingredientsDict.has_key(k) else []
	newr = Resource(item,productNames[k],ingredients,1)
	newr.prices = prices[k][10000002]
	resources[k] = newr


dates = sorted(prices[16646][10000002].keys())


productIngredients = dict()

for item in productsToMake:
	finalItemProcess(item)

for item in listOfRaw:
	finalItemProcess(item)

for item in listOfSimple:
	finalItemProcess(item)

for item in listOfComplex:
	finalItemProcess(item)

for item in listOfT2:
	finalItemProcess(item)

mercuryInput = []
mercuryOutput = []

for date in dates:
	totalVolumeInput = dict()
	totalVolumeOutput = dict()
	for item in listOfRaw:
		totalVolumeInput[item] = 0
		totalVolumeOutput[item] = 0
	for item in productsToMake:
		if not prices[item][10000002].has_key(date): continue
		for k,v in productIngredients[item].iteritems():
			if totalVolumeOutput.has_key(k): totalVolumeOutput[k] += v * prices[item][10000002][date][0]
	for item in listOfRaw:
		if not prices[item][10000002].has_key(date): continue
		for k,v in productIngredients[item].iteritems():
			if totalVolumeInput.has_key(k): totalVolumeInput[k] += v * prices[item][10000002][date][0]
	for item in listOfSimple:
		if not prices[item][10000002].has_key(date): continue
		for k,v in productIngredients[item].iteritems():
			if totalVolumeInput.has_key(k): totalVolumeInput[k] += v * prices[item][10000002][date][0]
	for item in listOfComplex:
		if not prices[item][10000002].has_key(date): continue
		#for k,v in productIngredients[item].iteritems():
			#if totalVolumeInput.has_key(k): totalVolumeInput[k] += v * prices[item][10000002][date][0]
	mercuryInput.append(totalVolumeInput[16646])
	mercuryOutput.append(totalVolumeOutput[16646])

makeMercuryVolumesChart(16646,dates,mercuryInput,mercuryOutput)

print "--------------------------------------------"
print "--------------------------------------------"
print "--------------------------------------------"
print "--------------------------------------------"

for k,v in totalVolumeInput.iteritems():
	print productNames[k],v,totalVolumeOutput[k]

#for item in listOfT2:
#	print resources[item]


