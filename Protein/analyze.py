import string
import operator
import matplotlib.pyplot as plt

organisms = ["HUMAN","ARATH","BOVIN","CAEEL","CANFA","CHICK","DANRE","DROME","MOUSE","PIG","RAT","YEAST"]
badletters = ["B","J","O","U","X","Z"]
colors = dict()
colors["HUMAN"] = (0,0,0)
colors["ARATH"] = (0.5,0.2,0.2)
colors["BOVIN"] = (0.8,0.2,0.2)
colors["CAEEL"] = (1.0,0.2,0.2)
colors["CANFA"] = (0.2,0.5,0.2)
colors["CHICK"] = (0.2,0.8,0.2)
colors["DANRE"] = (0.2,1.0,0.2)
colors["DROME"] = (0.2,0.2,0.5)
colors["MOUSE"] = (0.2,0.2,0.8)
colors["PIG"] = (0.2,0.2,1.0)
colors["RAT"] = (0.5,0.2,0.5)
colors["YEAST"] = (0.8,0.2,0.8)

class Protein:
	def __init__(self,db,uniqueid,entryname,sequence):
		self.db = db
		self.id = uniqueid
		self.entry = entryname
		self.sequence = sequence
		return
	def __str__(self):
		return str(self.db)+"|"+str(self.id)+"|"+str(self.entry)+": "+str(self.sequence)
	def __repr__(self):
		return str(self.db)+"|"+str(self.id)+"|"+str(self.entry)+": "+str(self.sequence)

def initDictionary():
	pairs = dict()
	singles = dict()
	for letter in string.uppercase:
		if letter in badletters: continue
		singles[letter] = 0
		for letter2 in string.uppercase:
			if letter2 in badletters: continue
			pair = letter+letter2
			pairs[pair] = 0
	return singles,pairs
	

def extractProteins(filelines):
	proteins = []
	sequence = ""
	entry = ""
	db = ""
	uniqueid = ""
	for line in filelines:
		if line[0] == ">":
			if len(db) > 0:
				p = Protein(db,uniqueid,entry,sequence)
				#print p
				proteins.append(p)
			sline = line[1:]
			exp1 = sline.split(" ")
			exp2 = exp1[0].split("|")
			db = exp2[0]
			uniqueid = exp2[1]
			entry = exp2[2]
			sequence = ""
		else:
			sequence += line.strip()
	return proteins


def populateDictionary(protein,dictionary,singleDictionary):
	for i in range(0,len(protein.sequence)):
		if protein.sequence[i] in badletters: continue
		singleDictionary[protein.sequence[i]] += 1
		pair = protein.sequence[i:i+2]
		if len(pair) < 2: return
		if pair[1] in badletters: continue
		#print dictionary[pair]
		dictionary[pair] += 1

def main():

	sorted_single = []
	sorted_pair = []
	singlelabels = []
	singlefrequencies = dict()
	pairlabels = []
	pairfrequencies = dict()
	plots = dict()
	fig = plt.figure()
	ax1 = fig.add_subplot(211)
	plt.subplot(211)
	plt.xlabel("Amino acid")
	plt.ylabel("frequency")
	ax2 = fig.add_subplot(212)
	plt.subplot(212)
	plt.ylabel("frequency")
	plt.xlabel("Pair of amino acids")
	for organism in organisms:
		f = open(organism+".fasta")
		singlefrequencies[organism] = []
		pairfrequencies[organism] = []
		
		lines = f.readlines()
		singleDictionary,pairDictionary = initDictionary()
		proteins = extractProteins(lines)
		for p in proteins:
			populateDictionary(p,pairDictionary,singleDictionary)

		stotal = 0
		ptotal = 0

		print organism,len(proteins)

		for k,v in singleDictionary.iteritems():
			stotal += v
		for k,v in pairDictionary.iteritems():
			ptotal += v
		if organism == "HUMAN":
			sorted_single = sorted(singleDictionary.iteritems(), key=operator.itemgetter(1),reverse=True)
			sorted_pair = sorted(pairDictionary.iteritems(), key=operator.itemgetter(1),reverse=True)
			for ss in sorted_single:
				singlelabels.append(ss[0])
			for sp in sorted_pair:
				pairlabels.append(sp[0])
			


		ofs = open("output/"+organism+".single.output",'w')
		ofp = open("output/"+organism+".pair.output",'w')
		for s in sorted_single:
			line = s[0]+" "+str(float(singleDictionary[s[0]])/float(stotal))+"\n"
			singlefrequencies[organism].append(float(singleDictionary[s[0]])/float(stotal))
			ofs.write(line)
		ofs.close()
		for s in sorted_pair:
			line = s[0]+" "+str(float(pairDictionary[s[0]])/float(ptotal))+" "+str(float(singleDictionary[s[0][0]]*singleDictionary[s[0][1]])/float(stotal*stotal))+"\n"
			pairfrequencies[organism].append(float(pairDictionary[s[0]])/float(ptotal))
			ofp.write(line)
		ofp.close()



		sx = [i for i in range(0,len(singlelabels))]
		px = [i for i in range(0,len(pairlabels))]
		ax1.plot(sx,singlefrequencies[organism],'-',label=organism,color=colors[organism])
		ax2.plot(px,pairfrequencies[organism],'-',color=colors[organism])

	#fig.show()
	box1 = ax1.get_position()
	ax1.set_position([box1.x0, box1.y0, box1.width * 0.8, box1.height])
	box2 = ax2.get_position()
	ax2.set_position([box2.x0,box2.y0,box2.width * 0.8, box2.height])

	# Put a legend to the right of the current axis
	ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),title='Organism')

	#handles, labels = ax1.get_legend_handles_labels()
	#ax1.legend(handles,labels,title='Organism')
	fig.savefig("figure.pdf")
	fig.savefig("figure.png")
		#for k,v in pairDictionary.iteritems():
			#print k,v,float(v)/float(ptotal),float(singleDictionary[k[0]]*singleDictionary[k[1]])/float(stotal*stotal)
	return
	
if __name__ == '__main__':
	#import profile
	#profile.run("main()")
	main()

