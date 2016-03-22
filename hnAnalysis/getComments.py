# You can substitute the stdlib's json module, if that suits your fancy
import simplejson
import MySQLdb
import dateutil.parser as parser
import datetime
import time
import urllib2
import json

def main():
    db = MySQLdb.connect(host="localhost",user="hnAnalysis",passwd="hnhnhn",db="hnAnalysis")
    cursor = db.cursor()

    endtime=datetime.datetime(2013,10,01)
    ind = 0
    query = "SELECT id_db FROM submissionMetaData WHERE create_ts < \""+endtime.strftime("%Y-%m-%d %H:%M:%S")+"\" AND num_comments > 0;"
    cursor.execute(query)
    results = cursor.fetchall()
    for row in results:
        id_db = row[0]

        done = False
        start = 0
        while not done:
            time.sleep(1)
            url="http://api.thriftdb.com/api.hnsearch.com/items/_search?filter[fields][type]=comment&filter[fields][discussion.sigid]="+id_db+"&limit=100&start="+str(start)

            print url
            request = urllib2.Request(url)
            try: 
		result = urllib2.urlopen(request)
            except urllib2.HTTPError,err:
		print "ERROR:",url,err.code
		if err.code == 403 or err.code == 500:
                    time.sleep(1)
                    continue
		else: break
            except urllib2.URLError, err:
		print "ERROR URL",url,err.reason

            try:		
		data = json.load(result)
            except ValueError:
		print "Decoding Failed",url
		continue				
        # Un-serialize the JSON data to a Python dict.
        # Dump the market data to stdout. Or, you know, do more fun
        # things here.
            if data["hits"] < start + 100 or start >= 900: done = True
            print id_db,data["hits"],len(data["results"])
            items = data["results"]
            if len(items) == 0: continue
            for item in items:
		queryitem = "INSERT INTO commentMetaData (id,id_db,create_ts,discussion_id,discussion_id_db,num_comments,parent_id,parent_id_db,points,text,username) VALUES ("

		create_ts = item["item"]["create_ts"]
		createts = datetime.datetime.strptime(create_ts,"%Y-%m-%dT%H:%M:%SZ")
		#print item["item"]["id"],item["item"]["_id"],str(item["item"]["domain"])
                queryitem += str(item["item"]["id"])+",\""+str(item["item"]["_id"])+"\",\""+ createts.strftime("%Y-%m-%d %H:%M:%S") + "\","+str(item["item"]["discussion"]["id"])+",\""+str(item["item"]["discussion"]["sigid"])+"\","
		#print item["item"]["title"]
                queryitem += str(item["item"]["num_comments"])+","+str(item["item"]["parent_id"])+",\""+str(item["item"]["parent_sigid"])+"\","+str(item["item"]["points"])+",\""
		itemtext=item["item"]["text"]
		if itemtext is None: itemtext=""
		try:
                    itemtext=MySQLdb.escape_string(itemtext)
		except:
                    itemtext=""
                queryitem += itemtext+"\",\""+item["item"]["username"]+"\") ON DUPLICATE KEY UPDATE id=id;"
		#print queryitem
		cursor.execute(queryitem)
		cursor.execute("commit")
            start += 100

if __name__ == '__main__':
    main()


