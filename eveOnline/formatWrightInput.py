primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59]

def extractCandidates(ls):
	candidates = []
	for i in range(11,len(ls)-5):
		print ls[i]
		cls = ls[i].split("-")
		candidate = cls[1].strip()
		candidates.append(candidate)
	return candidates
	
def extractBallot(ls):
	ballot = [0]*15
	for i in range(11,len(ls)-5):
		if ls[i] == "": continue
		if int(ls[i]) > 14: continue
		ballot[int(ls[i])] = i-10	
	nBallots = ls[len(ls)-4].strip()
	if nBallots == "": nBallots = 1
	else: nBallots = int(nBallots)
	print nBallots,ballot
	return nBallots,ballot

def getHash(ballot):
	ballotHash = 0
	tree = dict()
	for i in range(1,len(ballot)):
		if ballot[i] == 0: break
		ballotHash += pow(primes[i],ballot[i])
	if not hashes.has_key(ballotHash): hashes[ballotHash] = ballot
	return ballotHash

f = open("final_result_no_troll.csv","r")
ballotDict = dict()
hashes = dict()
candidates = []
total = 0
for index,line in enumerate(f.readlines()):
	ls = line.split(",")
	if index == 0: continue
	if index == 1: candidates = extractCandidates(ls)
	else:
		nBallots,ballot = extractBallot(ls)
		total += nBallots
		ballotHash = getHash(ballot)
		if not ballotDict.has_key(ballotHash): ballotDict[ballotHash] = 0
		ballotDict[ballotHash] += nBallots
f.close()

print total
outfile = open("csm.blt","w")
outfile.write(str(len(candidates))+" 14\n")
for ballotHash,nb in ballotDict.iteritems():
	line = str(nb)+" "
	ballot = hashes[ballotHash]
	for i in range(1,len(ballot)):
		line += str(ballot[i])+" "
	line += "0\n"
	outfile.write(line)
outfile.write("0\n")
print candidates
for candidate in candidates:
	outfile.write(candidate+"\n")
outfile.close()
