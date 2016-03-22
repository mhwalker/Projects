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
covariance = []
meancolumn = [0]*nBigrams

for i in range(0,nBigrams):
	covariance.append([0]*nBigrams)

i = 0
for bg in bigrams.keys():
	keymap[bg] = i
	i += 1

db = MySQLdb.connect(host="localhost",user="hnAnalysis",passwd="hnhnhn",db="hnAnalysis")
cursor = db.cursor()

query = "SELECT text FROM commentMetaData ORDER BY id_md5 limit 100000,100000;"
cursor.execute(query)
results = cursor.fetchall()


for row in results:
	text = row[0]
	unesctext = h.unescape(text)
	tokens = nltk.word_tokenize(unesctext)
	tagged = nltk.pos_tag(tokens)
	#print tagged
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
		#print word,tag
		if tag not in goodTags: continue
		if i > 0 and bgtags[0] in goodTags:
			key = bg[0].lower()+" "+bg[1].lower()
			if not bigrams.has_key(key): continue
			keys.append(key)
			#print key
		i += 1
	nKeys = len(keys)
	for j in range(0,nKeys):
		keyjd = keymap[keys[j]]
		meancolumn[keyjd] += 1
#		for k in range(j+1,nKeys):
#			keykd = keymap[keys[k]]
#			covariance[keykd][keyjd] += 1

nResults = len(results)
for i in range(0,len(meancolumn)):
	meancolumn[i] = float(meancolumn[i])/float(nResults)

for row in results:
	text = row[0]
	unesctext = h.unescape(text)
	tokens = nltk.word_tokenize(unesctext)
	tagged = nltk.pos_tag(tokens)
	#print tagged
	i = 0
	bg = ["",""]
	bgtags = ["",""]
	keys = [0]*nBigrams
	for t in tagged:
		word = t[0]
		tag = t[1]
		bg[0] = bg[1]
		bg[1] = word
		bgtags[0] = bgtags[1]
		bgtags[1] = tag		
		#print word,tag
		if tag not in goodTags: continue
		if i > 0 and bgtags[0] in goodTags:
			key = bg[0].lower()+" "+bg[1].lower()
			if not bigrams.has_key(key): continue
			keyid = keymap[key]
			keys[keyid] += 1
			#print key
		i += 1
	nKeys = len(keys)
	for j in range(0,nKeys):
		for k in range(0,nKeys):
			#if keys[k] > 0 or keys[j] > 0: print keys[k],keys[j],(keys[k] - meancolumn[k])*(keys[j] - meancolumn[j])
			covariance[k][j] += (keys[k] - meancolumn[k])*(keys[j] - meancolumn[j]) / (nResults - 1)


outcov = dict()
outcov["cov"] = covariance
outcov["mean"] = meancolumn
#print covmatrix
ofile = open("pcaCov10k_run2.json","w")
json.dump(outcov,ofile)
ofile.close()
