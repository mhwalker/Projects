
#years = range(1999,2013)
years = [2012]

metros = dict()
metros[41860] = "San Francisco"
metros[35620] = "New York"
metros[71650] = "Boston"
metros[42660] = "Seattle"
metros[47900] = "Washington D.C."
metros[31100] = "Los Angeles"
metros[37980] = "Philadelphia"
metros[16980] = "Chicago"

def cleanLow(stuff,ofile):
	exp0 = stuff.split("</table>")
	exp1 = exp0[0].split("Mean RSE")
	mmm = len(exp0)
	nnn = len(exp1)
	print mmm,nnn
	for i in range(1,nnn):
		exp2 = exp1[i].split("<tr>")
		ooo = len(exp2)
		for i in range(1,ooo):
			exp3 = exp2[i].split("<td>")
			if len(exp3) < 2: continue
			print len(exp3), exp3
			exp4 = exp3[1].split("<nobr>")
			if len(exp4) > 1:code = exp4[1].strip()
			else: code = exp4[0].strip()
			line = str(code)+" "+exp3[3].strip()+" 0 0 0 "+exp3[4].strip()+" "+exp3[5].strip()+" "+exp3[6].strip()+" "+exp3[7].strip()+"\n"
			ofile.write(line)
			
	
	return
	
def cleanHigh(stuff,ofile):
	exp0 = stuff.split("</table>")
	exp1 = exp0[0].split("Mean wage RSE")
	mmm = len(exp0)
	nnn = len(exp1)
	print mmm,nnn
	for i in range(1,nnn):
		exp2 = exp1[i].split("<tr>")
		ooo = len(exp2)
		for i in range(1,ooo):
			exp3 = exp2[i].split("<td>")
			if len(exp3) < 2: continue
			print len(exp3), exp3
			exp4 = exp3[1].split("<nobr>")
			if len(exp4) > 1:code = exp4[1].strip()
			else: code = exp4[0].strip()
			if len(exp3) < 12: continue
			line = str(code)+" "+exp3[4].strip()+" "+exp3[5].strip()+" "+exp3[6].strip()+" "+exp3[7].strip()+" "+exp3[8].strip()+" "+exp3[9].strip()+" "+exp3[10].strip()+" "+exp3[11].strip()+"\n"
			ofile.write(line)

	return


for year in years:
	for m,c in metros.iteritems():
		ifname = "data_html/"+str(m)+"_"+str(year)+".htm"
		ifile = open(ifname,"r")
		stuff = ifile.read()
		ifile.close()
		ofname = "data_clean/"+str(m)+"_"+str(year)+".dat"
		ofile = open(ofname,"w")
		if year < 2011: cleanLow(stuff,ofile)
		else: cleanHigh(stuff,ofile)
		ofile.close()
