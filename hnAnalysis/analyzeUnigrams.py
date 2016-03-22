import simplejson as json
import operator

unifile = open("skimunigrams.json","r")
unigrams = json.load(unifile)
unifile.close()

sortedunigrams = sorted(unigrams.iteritems(), key = operator.itemgetter(1),reverse=True)

i = 0
while True:
	print i,sortedunigrams[i][0],sortedunigrams[i][1]
	i += 1
	if sortedunigrams[i][1] < 100000:break