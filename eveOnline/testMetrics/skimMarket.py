"""
Example Python EMDR client.
"""
import zlib
import zmq
# You can substitute the stdlib's json module, if that suits your fancy
import simplejson
import MySQLdb
import dateutil.parser as parser

def main():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)

    # Connect to the first publicly available relay.
    subscriber.connect('tcp://relay-us-central-1.eve-emdr.com:8050')
    # Disable filtering.
    subscriber.setsockopt(zmq.SUBSCRIBE, "")

    db = MySQLdb.connect(host="localhost",user="testmetrics",passwd="t3stm3trics",db="MARKETHISTORY")
    cursor = db.cursor()

    ind = 0
    while True:
        # Receive raw market JSON strings.
        market_json = zlib.decompress(subscriber.recv())
        # Un-serialize the JSON data to a Python dict.
        market_data = simplejson.loads(market_json)
        # Dump the market data to stdout. Or, you know, do more fun
        # things here.
 	if market_data["resultType"] == "history":
            data1 = market_data["rowsets"]
            rows = data1[0]["rows"]
            regionID = int(data1[0]['regionID'])
            typeID = int(data1[0]['typeID'])
            columns = market_data['columns']
            generatedAt = (parser.parse(data1[0]['generatedAt'])).replace(tzinfo=None)
            columnDict = dict()
            for i,c in enumerate(columns):
                columnDict[c] = i
            for row in rows:
                recordtime = (parser.parse(row[columnDict["date"]])).replace(tzinfo=None)
                if (generatedAt - recordtime).days < 1: continue
                sqlquery = "INSERT INTO history (typeID,regionID,orders,quantity,low,high,average,day,generatedAt) VALUES ("
                sqlquery += str(typeID)+","+str(regionID)+","+str(row[columnDict["orders"]])+","+str(row[columnDict["quantity"]])+","
                sqlquery += str(row[columnDict["low"]])+","+str(row[columnDict["high"]])+","+str(row[columnDict["average"]])
                sqlquery += ",\""+str(recordtime)+"\",\""+str(generatedAt)+"\") ON DUPLICATE KEY UPDATE typeID=typeID;"
                cursor.execute(sqlquery)
                cursor.execute("commit")


if __name__ == '__main__':
    main()


