import MySQLdb


db = MySQLdb.connect(host="localhost",user="testmetrics",passwd="t3stm3trics",db="MARKETHISTORY")
cursor = db.cursor()



query = "SELECT typeID,AVG(quantity*average) as avgmove FROM history WHERE day > '2014-05-31 23:59:59' AND regionID=10000002 GROUP BY typeID ORDER BY avgmove DESC;"
cursor.execute(query)
rows = cursor.fetchall()

things = []

for row in rows:
    typeID = int(row[0])
    avgmove = float(row[1])
    if avgmove < 100000000: break
    nquery = "SELECT low,average,high FROM history WHERE regionID=10000002 and typeID="+str(typeID)+" ORDER BY day DESC limit 1;"
    cursor.execute(nquery)
    prices=cursor.fetchone()
    #print prices
    things.append((typeID,(avgmove,float(prices[0]),float(prices[1]),float(prices[2]))))

print things

