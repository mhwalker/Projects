import operator

infile = open("test2.csv","r")
nSpots = 14
ballots = []
candidates = []

for i,line in enumerate(infile.readlines()):
	ls = (line.strip()).split(",")
	if i == 0:
		#print len(ls)
		for j in range(0,len(ls)):
			candidates.append(ls[j])
	else:
		ballot = [" "]*14
		for j in range(0,len(ls)):
			if ls[j].strip() == "": continue
			ballot[int(ls[j])-1] = candidates[j]
		#print ballot
		ballots.append(ballot)

nBallots = len(ballots)
quota = int(float(nBallots)/float(1+nSpots))+1
nElected = 0
#print nBallots, quota
removed = []

while nElected != nSpots:
	elected = []
	ballotCount = dict()
	for c in candidates:
		if c in removed: continue
		ballotCount[c] = 0

	total = 0
	for ballot in ballots:
		for b in ballot:
			if b in elected: continue
			if b in removed: continue
			ballotCount[b] += 1
			total += 1
			break

	quota = int(float(total)/float(1+nSpots))+1

	surplusCount = dict()
	surplus = 0
	for c,v in ballotCount.iteritems():
		#print c,v
		if v >= quota:
			elected.append(c)
			surplusCount[c] = float(v - quota)/float(v)
			surplus += v-quota
		else:
			surplusCount[c] = 1

	nElected = len(elected)
	if nElected == nSpots: break

	if nElected > 0 and surplus > 0:
		#print nElected,surplus
		recount = dict()
	        for c in candidates:
			if c in removed: continue
			if c in elected: continue
	                recount[c] = 0.0

		total = 0
		for ballot in ballots:
			i = -1
			for j,b in enumerate(ballot):
				if b in removed: continue
				if b in elected:
					i = j
					continue
				#print j,i,surplusCount[ballot[i]]
				if i < 0: i = j
				recount[b] += surplusCount[ballot[i]]
				total += 1
				break
		quota = int(float(total)/float(1+nSpots))+1

		#print "aaaaaaaaaaaaaaaa"

		for c,v in recount.iteritems():
			#print c,v
			if c in elected: continue
			if v >= quota:
				elected.append(c)

		nElected = len(elected)
		
		#print "bbbbbbbbbbbbbbbb"

		nonElected = dict()
		for c,v in recount.iteritems():
			if c in elected: continue
			nonElected[c] = v
		sorted_nonElected = sorted(nonElected.iteritems(), key=operator.itemgetter(1))
		exclusionTotal = 0
		excludable = []
		for p in sorted_nonElected:
			#print p[0],p[1],exclusionTotal
			if exclusionTotal < p[1] or exclusionTotal < quota:
				excludable.append(p[0])
				exclusionTotal += p[1]
			else:
				excludable.pop()
				break
		removed.extend(excludable)
	
		print "removed:",removed
	else:
		sorted_nonElected = sorted(ballotCount.iteritems(), key=operator.itemgetter(1))
		removed.append(sorted_nonElected[0][0])
		print "removed:",removed
		
print "elected:",elected
