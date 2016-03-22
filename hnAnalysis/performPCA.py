from numpy import *
from numpy.linalg import *
import simplejson as json

bifile = open("skimbigrams10k.json","r")
bigrams = json.load(bifile)
bifile.close()

keymap = dict()
nBigrams = len(bigrams)

i = 0
for bg in bigrams.keys():
	keymap[bg] = i
	i += 1


covfile = open("pcaCov10k_run2.json","r")
incov = json.load(covfile)
covfile.close()

covariance = incov["cov"]
meanvec = incov["mean"]

covmatrix = matrix(covariance)

nVectors = 15
vectors = []
for i in range(0,nVectors):
	nvec = random.uniform(-1.0,1.0,nBigrams)
	ncolumn = matrix(nvec).transpose()
	ncolumn /= norm(ncolumn)
	while True:
		ocolumn = covmatrix*ncolumn
		#print norm(ncolumn)
		ocolumn /= norm(ocolumn)
		#ocolumn = ncolumn
		dcolumn = ocolumn
		for v in vectors:
			a = float(ocolumn.transpose()*v)
			dcolumn -= a*v
		dcolumn /= norm(dcolumn)
		ocolumn = dcolumn
		#print ocolumn.shape
		#print len(ocolumn),len(ncolumn)
		#print ocolumn.shape,ncolumn.shape
		#print abs(1.0 - inner(ocolumn.transpose(),ncolumn.transpose()))
		#print (inner(ocolumn.transpose(),ncolumn.transpose()))
		if abs(1.0 - inner(ocolumn.transpose(),ncolumn.transpose())) < 1e-3:
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

unifile = open("pcaOutput_run2.json","w")
json.dump(outvectors,unifile)
unifile.close()
