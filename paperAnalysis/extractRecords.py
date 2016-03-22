import MySQLdb
import dateutil.parser as parser
import urllib2
import datetime
import time
import glob
import re
from bs4 import BeautifulSoup
import json
import sys

db =  MySQLdb.connect(host="localhost",user="papers",passwd="papers1234pass",db="paperAnalysis",charset='utf8')
cursor = db.cursor()

def getInspireUrl(parsed_html):
    links = parsed_html.findAll('a',href=re.compile("inspirehep.net"))
    if len(links) > 0: return links[0]['href']

    links = parsed_html.findAll('a',href=re.compile("arxiv.org/abs/"))
    if len(links) == 0: return ""
    arxivurl = links[0]['href']
    request = urllib2.Request(arxivurl)
    try: 
        result = urllib2.urlopen(request).read()
    except urllib2.HTTPError:
        print "ERROR:",url,err.code
        return ""
    except urllib2.URLError,err:
        print "ERROR URL:",url,err.reason
        return ""

    parsed_arxiv = BeautifulSoup(result)

    links_arxiv = parsed_arxiv.findAll('a',href=re.compile("inspirehep.net/search"))
    if len(links_arxiv) == 0: return ""

    inspireurl1 = links_arxiv[0]['href']

    request = urllib2.Request(inspireurl1)
    try: 
        result = urllib2.urlopen(request).read()
    except urllib2.HTTPError:
        print "ERROR:",url,err.code
        return ""
    except urllib2.URLError,err:
        print "ERROR URL:",url,err.reason
        return ""

    parsed_inspire = BeautifulSoup(result)

    links_inspire = parsed_inspire.findAll('a',href=re.compile("inspirehep.net/record"))
    if len(links_inspire) == 0: return 0
    return links_inspire[0]['href']
    

def extractInfo(url,tag):
    print url
    ls0 = url.split("/")
    ls1 = ls0[-1].split("?")
    cdsID = int(ls1[0])
    request = urllib2.Request(url)
    try: 
        result = urllib2.urlopen(request).read()
    except urllib2.HTTPError:
        print "ERROR:",url,err.code
        return
    except urllib2.URLError,err:
        print "ERROR URL:",url,err.reason
        return

    parsed_html = BeautifulSoup(result)

    rows = parsed_html.findAll('tr')
    doi = ''
    for row in rows:
        cols = row.findAll('td')
        if "Preprint" == cols[0].text.strip():
            return
        if cols[0].text.strip() == "Title":
            title = cols[1].text.replace(u'\u221a',"sqrt").replace(u'\u2212',"-").replace(u'\u2013',"--")
        if "Experiment" in cols[0].text and len(cols) > 1:
            lsexp = cols[1].text.split(";")
            collaboration = lsexp[1].strip()
        if cols[0].text.strip() == "In:":
            journal = cols[1].text.replace(u'\u2013',"--")
        if cols[0].text.strip() == "DOI":
            lsdoi = cols[1].text.split("\n")
            doi = lsdoi[0].strip()
    

    inspireurl = getInspireUrl(parsed_html)

    print inspireurl

    if inspireurl == "": return

    request2 = urllib2.Request(inspireurl+"?of=recjson&ot=recid,number_of_citations,creation_date")
    try: 
        result2 = urllib2.urlopen(request2)
    except urllib2.HTTPError:
        print "ERROR:",inspireurl,err.code
        return
    except urllib2.URLError,err:
        print "ERROR URL:",inspireurl,err.reason
        return
    try:            
        data = json.load(result2)
    except ValueError:
        print "Decoding Failed",inspireurl
        return

    inspireID = data[0]["recid"]
    numCite = data[0]["number_of_citations"]
    creation = datetime.datetime.strptime(data[0]["creation_date"],"%Y-%m-%dT%H:%M:%S")
    cdate = creation.strftime("%Y-%m-%d %H:%M:%S")

    querysub = "INSERT INTO papers (cdsID,title,papertype,collaboration,journal,inspireID,doi,nCitations,creation_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE cdsID=cdsID;"
    cursor.execute(querysub,(cdsID,title,tag,collaboration,journal,inspireID,doi,numCite,cdate))
    print cursor._last_executed
    cursor.execute("commit")
    #print querysub
    return
    

recfiles = glob.glob("./*.record")

#extractInfo("http://cds.cern.ch/record/1335111?ln=en","sus")

#sys.exit()

for fname in recfiles:
    print fname
    f = open(fname)
    lstag = fname.split(".")
    lstag2 = lstag[1].split("_")
    for line in f.readlines():
        url = "http://cds.cern.ch"+line.strip()
        extractInfo(url,lstag2[1])
