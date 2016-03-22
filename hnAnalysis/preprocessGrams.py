import MySQLdb
import nltk
import re
import HTMLParser
import cPickle as pickle

goodTags = set(["CC","DT","EX","IN","JJ","JJR","JJS","MD","PDT","RB","RBR","RP","TO","UH","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WRB"])

h = HTMLParser.HTMLParser()

db = MySQLdb.connect(host="localhost",user="root",port=3306,db="hnAnalysis",unix_socket="/var/mysql/mysql.sock")
cursor = db.cursor()

query = "SELECT text FROM commentMetaData;"
cursor.execute(query)
results = cursor.fetchall()

unigrams = dict()
bigrams = dict()

for row in results:
	text = row[0]
	unesctext = h.unescape(text)
	tokens = nltk.word_tokenize(unesctext)
	tagged = nltk.pos_tag(tokens)
	#print tagged
	i = 0
	bg = ["",""]
	bgtags = ["",""]
	for t in tagged:
		word = t[0]
		tag = t[1]
		bg[0] = bg[1]
		bg[1] = word
		bgtags[0] = bgtags[1]
		bgtags[1] = tag		
		#print word,tag
		if tag not in goodTags: continue
		if not unigrams.has_key(word): unigrams[word] = 0
		#print word
		unigrams[word] += 1
		if i > 0 and bgtags[0] in goodTags:
			key = bg[0].lower()+" "+bg[1].lower()
			if not bigrams.has_key(key): bigrams[key] = 0
			bigrams[key] += 1
			#print key
		i += 1


unigramsreverse = dict()
bigramsreverse = dict()
print len(unigrams),len(bigrams)

count = 0
for k,v in bigrams.iteritems():
	if v > 1: count += 1
print count

outfile = open("output.pckl","w")
pickle.dump(unigrams,outfile)
pickle.dump(bigrams,outfile)
