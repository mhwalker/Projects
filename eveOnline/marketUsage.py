import MySQLdb
import urllib2
import xml.etree.cElementTree as ET
import operator
import matplotlib.pyplot as plt
import colorsys
import matplotlib.dates as mdates

locations = dict()
locations[10000002] = "Forge"
locations[10000043] = "Delve"


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




db = MySQLdb.connect(host="localhost",user="root",port=3306,db="eve_static",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()

db2 = MySQLdb.connect(host="localhost",user="root",port=3306,db="MARKETHISTORY",unix_socket="/var/mysql/mysql.sock")
cursor2 = db2.cursor()


query = " 