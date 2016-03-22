import simplejson as json
import operator

bifile = open("skimbigrams.json","r")
bigrams = json.load(bifile)
bifile.close()

sortedbigrams = sorted(bigrams.iteritems(), key = operator.itemgetter(1),reverse=True)

print len(sortedbigrams)
i = 0
while True:
	print i,sortedbigrams[i][0],sortedbigrams[i][1]
	i += 1
	if i > 100:break