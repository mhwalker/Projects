from numpy import *
from numpy.linalg import *
import MySQLdb
import nltk
import re
import HTMLParser
import cPickle as pickle
import simplejson as json

goodTags = set(["CC","DT","EX","IN","JJ","JJR","JJS","MD","PDT","RB","RBR","RP","TO","UH","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WRB"])

h = HTMLParser.HTMLParser()

unifile = open("skimunigrams10k.json","r")
unigrams = json.load(unifile)
unifile.close()

bifile = open("skimbigrams10k.json","r")
bigrams = json.load(bifile)
bifile.close()

keymap = dict()
nBigrams = len(bigrams)

covfile = open("pcaOutput.json","r")
invec = json.load(covfile)
covfile.close()
nVectors = 15

i = 0
for bg in bigrams.keys():
	keymap[bg] = i
	i += 1

db = MySQLdb.connect(host="localhost",user="hnAnalysis",passwd="hnhnhn",db="hnAnalysis")
cursor = db.cursor()

for j in range(0,454):
	print j
	query = "SELECT text,id,pcaresults FROM commentMetaData ORDER BY id_md5 limit %i,10000;" % (j*10000,)
	cursor.execute(query)
	results = cursor.fetchall()


	for row in results:
		text = row[0]
		commentid = int(row[1])
		prevResults=row[2]
		unesctext = h.unescape(text)
		tokens = nltk.word_tokenize(unesctext)
		tagged = nltk.pos_tag(tokens)
		i = 0
		bg = ["",""]
		bgtags = ["",""]
		keys = []
		for t in tagged:
			word = t[0]
			tag = t[1]
			bg[0] = bg[1]
			bg[1] = word
			bgtags[0] = bgtags[1]
			bgtags[1] = tag		
			if tag not in goodTags: continue
			if i > 0 and bgtags[0] in goodTags:
				key = bg[0].lower()+" "+bg[1].lower()
				if not bigrams.has_key(key): continue
				keys.append(key)
			i += 1
		nKeys = len(keys)
		keylist = ""
		for k in range(0,nKeys):
			key=""
			try:
				key = MySQLdb.escape_string(keys[k])
			except:
				key = ""
			if key == "": continue
			if k > 0: keylist += ":"
			keylist += key
		weight = 0
		if nKeys > 0: weight = 1.0/sqrt(float(nKeys))
		inline=str(nKeys)
		for k in range(0,nVectors):
			vec = invec[str(k)]
			ip = 0
			inline += ","
			for key,val in vec.iteritems():
				if key in keys: ip += val*weight
			inline += "%0.3f" % (ip,)
		#print inline
		if len(prevResults) > 0: inresults=prevResults+":"+inline
		else: inresults=inline
		inquery="UPDATE commentMetaData SET pcaresults=\""+inline+"\",keylist=\""+keylist+"\" where id="+str(commentid)+";"
		#print inquery
		cursor.execute(inquery)
		cursor.execute("commit")

