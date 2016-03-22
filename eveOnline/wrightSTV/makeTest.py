import random
f = open("test2.csv","w")

base=["1","2","3","4","5","6","7","8","9","10","11","12","13","14"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "]

f.write("AA,AB,BB,BC,CC,CD,DD,DE,EE,FF,FG,GG,GH,HH,HI,II,JJ,KK,LL,MM,NN,NQ,OO,PP,PQ,QQ,RR,SS,TT,UU,VV,WW,XX,YY,ZZ\n")
for i in range(0,1000):
	line = ""
	ballot = random.sample(base,len(base))
	for j in range(0,len(base)):
		line += ballot[j]
		if j != len(base)-1:
			line += ","
	line += "\n"
	f.write(line)

f.close()
