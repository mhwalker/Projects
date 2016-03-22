from ROOT import *
import random
#from scipy.stats import powerlaw
import numpy as np
from operator import itemgetter

def doTrial(nUsers,alpha):
	items = []
	initial = []
	for j in range(0,nUsers):
		standard = np.random.pareto(1)+20
		#standard = random.gauss(80,10)
		#items.sort(key=itemgetter(1),reverse=true)
		for item in items:
			p_read = float(item[1])/float(j+1)
			read = random.random()
			if p_read > read:
				if standard < item[0]:
					item[1] += 1
				#else:
				#	item[1] -= 1
		nNew = floor(np.random.poisson(alpha/(j+1)))
		#print nNew
		newQ = np.random.pareto(1,size=nNew)
		#if nNew > 0: print standard,newQ
		for q in newQ:
			items.append([standard+q,1])
			initial.append(standard+q)
	#print items
	items.sort(key=itemgetter(1),reverse=true)
	results = []
	for i,item in enumerate(items):
		if i < alpha:
			results.append(item[0])
	return results,initial

nTrials = 1000

nUsers = 10000

alpha = 20

#outfile = TFile("gauss_80_10.root","RECREATE")
outfile = TFile("power_1_20_10k.root","RECREATE")
histogram = TH1F("top_quality","",200,-0.5,199.5)
histogram_init = TH1F("initial_quality","",200,-0.5,199.5)

for i in range(0,nTrials):
	results,initial = doTrial(nUsers,alpha)
	#if i % 100 == 0: print results
	for r in results:
		histogram.Fill(r)
	for q in initial:
		histogram_init.Fill(q)

outfile.Write()
outfile.Close()