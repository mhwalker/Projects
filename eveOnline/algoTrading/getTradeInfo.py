import MySQLdb
import urllib2
import xml.etree.cElementTree as ET
import operator
import matplotlib.pyplot as plt
import colorsys
import datetime
import simplejson as json

locations = dict()
locations[30002187] = "Amarr"
locations[30000142] = "Jita"
#locations[30002510] = "Rens"
locations[30002659] = "Dodixie"
#locations[30002053] = "Hek"

regions = dict()
regions[10000002] = "The Forge"
regions[10000032] = "Sinq Liaison"
regions[10000043] = "Domain"

db = MySQLdb.connect(host="localhost",user="testmetrics",passwd="t3stm3trics",db="MARKETHISTORY")
cursor = db.cursor()

now = datetime.datetime.now()

starttime = now - datetime.timedelta(microseconds=now.microsecond,days=35)
datatime = now - datetime.timedelta(microseconds=now.microsecond,days=8)

query = "SELECT typeID,AVG(quantity*average) as avgmove FROM history WHERE day > '"+starttime.strftime("%Y-%m-%d %H:%M:%S")+"' AND regionID=10000002 GROUP BY typeID ORDER BY avgmove DESC;"

print query
print ""

cursor.execute(query)
rows = cursor.fetchall()

things = dict()

for row in rows:
    typeID = int(row[0])
    avgmove = float(row[1])
    #avgspread = float(row[2])
    if avgmove < 50000000: break
    things[typeID] = dict()
    things[typeID]["avg"] = dict()
    nquery = "SELECT regionID,AVG(quantity),AVG(quantity*average),AVG((high-low)/low) FROM history WHERE (regionID=10000002 OR regionID=10000032 OR regionID=10000043) AND typeID="+str(typeID)+" AND day > '"+starttime.strftime("%Y-%m-%d %H:%M:%S")+"' GROUP BY regionID;"
    #print nquery
    cursor.execute(nquery)
    results=cursor.fetchall()
    for rr in results:
        #print rr
        regionID = int(rr[0])
        quantity = float(rr[1])
        avgsales = float(rr[2])
        avgspread = float(rr[3])
        things[typeID]["avg"][regionID] = dict()
        things[typeID]["avg"][regionID]["avgsales"] = avgsales
        things[typeID]["avg"][regionID]["avgspread"] = avgspread
        things[typeID]["avg"][regionID]["avgquantity"] = quantity

    things[typeID]["prices"] = dict()
    for location,locname in regions.iteritems():
        prices = dict()
        dquery = "SELECT day,low,average,high,quantity FROM history WHERE regionID="+str(location)+" and day>'"+datatime.strftime("%Y-%m-%d %H:%M:%S")+"' and typeID="+str(typeID)+";"
        cursor.execute(dquery)
        priceresults = cursor.fetchall()
        for prr in priceresults:
            day = prr[0].strftime("%Y-%m-%d %H:%M:%S")
            low = float(prr[1])
            av = float(prr[2])
            high = float(prr[3])
            quantity = int(prr[4])
            prices[day] = dict()
            prices[day]["low"] = low
            prices[day]["avg"] = av
            prices[day]["high"] = high
            prices[day]["quantity"] = quantity
        things[typeID]["prices"][location] = prices

    #things[typeID][30000142] = (avgmove,avgspread,float(prices[0]),float(prices[1]),float(prices[2]))

db2 = MySQLdb.connect(host="localhost",user="testmetrics",passwd="t3stm3trics",db="eve_static")
cursor2 = db2.cursor()

#goodItems = []

prices = dict()
typeNames = dict()

for itemID in things.keys():
	sqlName = "SELECT types.typeNAME FROM invTypes as types WHERE types.typeID="+str(itemID)+";"
	cursor2.execute(sqlName)
	nameRes = cursor2.fetchone()
	name=nameRes[0]
        things[itemID]["name"] = name
	#typeNames[itemID] = name

outfile = open("itemdata.json","w")
json.dump(things,outfile)
outfile.close()
