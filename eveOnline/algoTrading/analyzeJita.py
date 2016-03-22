import MySQLdb

listOfRaw = [16633,16634,16635,16636,16637,16638,16639,16640,16641,16642,16643,16644,16646,16647,16648,16649,16650,16651,16652,16653]

allProducts = []
allProducts.extend(listOfRaw)

db = MySQLdb.connect(host="localhost",user="testmetrics",passwd="t3stm3trics",db="MARKETHISTORY")
cursor = db.cursor()


theCount = dict()
nItems = 0
totalRecords = 0
missing = []

for item in allProducts:
    nItems += 1
    query = "SELECT a.average,a.quantity as count FROM history WHERE regionID = 10000002 AND day > \"2014-02-28 23:59:59\" and day < \"2014-06-01 00:00:00\" and typeID="+str(item)+";"
    #print query
    cursor.execute(query)
    rows = cursor.fetchall()
    count = int(rows[0][0])
    theCount[item] = count
    totalRecords += count
    if count == 0: missing.append(item)


