import urllib2
import time
base="http://www.bls.gov/oes/"
years = range(1999,2013)

metros = dict()
metros[41860] = "San Francisco"
metros[35620] = "New York"
metros[71650] = "Boston"
metros[42660] = "Seattle"
metros[47900] = "Washington D.C."
metros[31100] = "Los Angeles"
metros[37980] = "Philadelphia"
metros[16980] = "Chicago"

metromap = dict()
metromap[16980] = 1600
metromap[31100] = 4480
metromap[41860] = 7360
metromap[47900] = 8840
metromap[71650] = 1120
metromap[35620] = 5600
metromap[37980] = 6160
metromap[42660] = 7600

for year in years:
	for m,c in metros.iteritems():
		url=base+str(year)+"/"
		if year > 2002: url += "may/"
		mid = m
		if year < 2005: mid = metromap[m]
		url += "oes_"+str(mid)+".htm"
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
		ofname = "data_html/"+str(m)+"_"+str(year)+".htm"
		ofile = open(ofname,"w")
		ofile.write(result.read())
		ofile.close()
		time.sleep(1)