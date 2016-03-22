from numpy import *
from numpy.linalg import *
import MySQLdb
import nltk
import re
import HTMLParser
import cPickle as pickle
import simplejson as json
import operator


covfile = open("pcaOutput.json","r")
invec = json.load(covfile)
covfile.close()

nVectors = 15
for k,vec in invec.iteritems():
	sortedvector = sorted(vec.iteritems(), key = operator.itemgetter(1),reverse=True)
	line = ""
	for j in range(0,15):
		line += sortedvector[j][0]
		line += ": %0.2e " % (pow(sortedvector[j][1],2),)
	print k,line