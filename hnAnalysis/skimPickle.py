import MySQLdb
import nltk
import re
import HTMLParser
import cPickle as pickle
import simplejson as json

infile = open("output.pckl","rb")

unigrams = pickle.load(infile)
bigrams = pickle.load(infile)

infile.close()

print len(unigrams),len(bigrams)

outfile = open("unigrams.json","w")
json.dump(unigrams,outfile)
outfile.close()
outfile = open("bigrams.json","w")
json.dump(bigrams,outfile)
outfile.close()