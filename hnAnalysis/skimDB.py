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

    #thetime=datetime.datetime(2006,10,9)
    thetime=datetime.datetime(2009,2,28)
    deltatime=datetime.timedelta(1)
    #endtime=datetime.datetime(2013,9,30)
    endtime = datetime.datetime(2006,10,14)
    ind = 0
    while ind < 2551:
	begintime = thetime
	url="http://api.thriftdb.com/api.hnsearch.com/items/_search?filter[fields][create_ts]=["
	url += thetime.strftime("%Y-%m-%dT%H:%M:%SZ")
	thetime += deltatime
	url += "%20TO%20"
	url += thetime.strftime("%Y-%m-%dT%H:%M:%SZ")
	url += "]&filter[fields][type]=submission&limit=100&sortby=points%20desc"
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
		time.sleep(1)
		continue				
        # Un-serialize the JSON data to a Python dict.
        # Dump the market data to stdout. Or, you know, do more fun
        # things here.
	print data["hits"],len(data["results"])
	querynsub = "INSERT INTO submissions (date,submissions) VALUES(\""
	querynsub += begintime.strftime('%Y-%m-%d %H:%M:%S')+"\","+str(data["hits"])+") ON DUPLICATE KEY UPDATE date=date;"
	#print querynsub
	cursor.execute(querynsub)
	cursor.execute("commit")
	items = data["results"]
	ind += 1
	time.sleep(1)
	if len(items) == 0: continue
	for item in items:
		queryitem = "INSERT INTO submissionMetaData (id,id_db,create_ts,domain,num_comments,points,title,url,username) VALUES ("
		create_ts = item["item"]["create_ts"]
		createts = datetime.datetime.strptime(create_ts,"%Y-%m-%dT%H:%M:%SZ")
		#print item["item"]["id"],item["item"]["_id"],str(item["item"]["domain"])
		try:
			domain=str(item["item"]["domain"])
		except:
			domain=""
		queryitem += str(item["item"]["id"])+",\""+str(item["item"]["_id"])+"\",\""+ createts.strftime("%Y-%m-%d %H:%M:%S") + "\",\""+domain+"\","
		#print item["item"]["title"]
		try:
			itemtitle=MySQLdb.escape_string(item["item"]["title"])
		except:
			itemtitle=""
		queryitem += str(item["item"]["num_comments"])+","+str(item["item"]["points"])+",\""+itemtitle+"\",\""
		itemurl=item["item"]["url"]
		if itemurl is None: itemurl=""
		try:
			itemurl=MySQLdb.escape_string(itemurl)
		except:
			itemurl=""
		queryitem += itemurl+"\",\""+item["item"]["username"]+"\") ON DUPLICATE KEY UPDATE id=id;"
		#print queryitem
		cursor.execute(queryitem)
		cursor.execute("commit")

if __name__ == '__main__':
    main()


