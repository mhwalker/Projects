import MySQLdb


db = MySQLdb.connect(host="localhost",user="testmetrics",passwd="t3stm3trics",db="MARKETHISTORY")
cursor = db.cursor()



query = "SELECT typeID,AVG(quantity*average) as avgmove,AVG((high-low)/low) as avgspread FROM history WHERE day > '2014-05-31 23:59:59' AND regionID=10000043 GROUP BY typeID ORDER BY avgmove DESC;"
cursor.execute(query)
rows = cursor.fetchall()

things = []

for row in rows:
    typeID = int(row[0])
    avgmove = float(row[1])
    avgspread = float(row[2])
    if avgmove < 100000000: break
    things.append((typeID,(avgmove,avgspread)))

print things

