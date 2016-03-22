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

bifile = open("skimbigrams.json","r")
bigrams = json.load(bifile)
bifile.close()

keymap = dict()
nBigrams = len(bigrams)

i = 0
for bg in bigrams.keys():
	keymap[bg] = i
	i += 1


covfile = open("pcaCov.json","r")
incov = json.load(covfile)
covfile.close()

covariance = incov["cov"]
meanvec = incov["mean"]

covmatrix = matrix(covariance)
meanc = matrix(meanvec).transpose()/100000.0
meanmean = meanc*meanc.transpose()
covmatrix = covmatrix - meanmean

nVectors = 15
vectors = []
for i in range(0,nVectors):
	nvec = random.random(nBigrams)
	ncolumn = matrix(nvec).transpose()
	ncolumn = ncolumn / norm(ncolumn)
	while True:
		ncolumn = covmatrix*ncolumn
		ncolumn = ncolumn / norm(ncolumn)
		ocolumn = ncolumn
		for v in vectors:
			ocolumn = ocolumn - (ocolumn*v.transpose())*v
		ocolumn = ocolumn / norm(ocolumn)
		#print len(ocolumn),len(ncolumn)
		#print ocolumn.shape,ncolumn.shape
		#print inner(ocolumn.transpose(),ncolumn.transpose())
		if abs(1.0 - inner(ocolumn.transpose(),ncolumn.transpose())) < 1e-6:
			vectors.append(ocolumn)
			print i
			break
		ncolumn = ocolumn
		
outvectors = dict()
for i in range(0,nVectors):
	ov = dict()
	for k,v in keymap.iteritems():
		#print i,k,v,vectors[i][v].item(0)
		ov[k] = vectors[i][v].item(0)
	outvectors[i] = ov

unifile = open("pcaOutput.json","w")
json.dump(outvectors,unifile)
unifile.close()