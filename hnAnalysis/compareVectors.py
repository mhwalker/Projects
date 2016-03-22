import simplejson as json
import operator

covfile = open("pcaOutput.json","r")
invec1 = json.load(covfile)
covfile.close()

covfile = open("pcaOutput_run2.json","r")
invec2 = json.load(covfile)
covfile.close()

nVectors = 15
for k in range(0,nVectors):
	vec = invec1[str(k)]
	line = str(k)
	for j in range(0,nVectors):
		vec2 = invec2[str(j)]
		ip = 0
		for key,val in vec.iteritems():
			if vec2.has_key(key):
				ip += val*vec2[key]
		line += " %0.3f" % (ip,)
	print k,line
