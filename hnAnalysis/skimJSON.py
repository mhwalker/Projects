import MySQLdb
import nltk
import re
import HTMLParser
import cPickle as pickle
import simplejson as json

unifile = open("unigrams.json","r")
unigrams = json.load(unifile)
unifile.close()

bifile = open("bigrams.json","r")
bigrams = json.load(bifile)
bifile.close()

print len(unigrams),len(bigrams)

skimunigram = dict()
skimbigram = dict()

for k,v in bigrams.iteritems():
	if v < 10000: continue
	#if ".com" in k: print k,v
	skimbigram[k] = v
for k,v in unigrams.iteritems():
	if v < 10000: continue
	if ".com" in k: continue
	if ".org" in k: continue
	skimunigram[k] = v

print len(skimunigram),len(skimbigram)

unifile = open("skimunigrams10k.json","w")
json.dump(skimunigram,unifile)
unifile.close()
bifile = open("skimbigrams10k.json","w")
json.dump(skimbigram,bifile)
bifile.close()