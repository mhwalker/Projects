import MySQLdb
import datetime
import matplotlib
matplotlib.use('Agg')
import pylab
import matplotlib.pyplot as plt
import colorsys
import time
import matplotlib.dates as mdates
import numpy as np
from scipy.optimize import curve_fit
import urllib2
import json
from ROOT import *
from array import array

nPeriods = 4
endPoints = ("2007-01-01","2008-01-01","2010-01-01","2011-03-01","2013-09-01")
#colors = ("Black","Blue","Red","Green")
colors = (kBlack,kBlue,kRed,kGreen+3)

def func(x,a,b):
	return b*np.power(x,a)

allData = []
allX = []
allY = []
scaledData = []
maxY = []
minY = []
bins = []
bins.append(-1000)
for i in range(0,100):
	bins.append(i)
for i in range(0,20):
	bins.append(i*10+100)
for i in range(0,34):
	bins.append(i*50+300)
for i in range(0,16):
	bins.append(i*500+2000)
for i in range(0,30):
	bins.append(i*1000+10000)
for i in range(0,16):
	bins.append(i*10000+40000)


histos = []
#label = 'Users with Karma'
#fig,ax = plt.subplots()
#fig.subplots_adjust(right=0.71,bottom=0.08,left=0.05)
#fig.set_size_inches(18,10)


for i in range(0,len(endPoints)-1):
	time.sleep(1)
	url="http://api.thriftdb.com/api.hnsearch.com/users/_search?pretty_print=true&facet[fields][karma][include]=1&facet[fields][karma][limit]=1000000&filter[fields][create_ts]=["+endPoints[i]+"T00:00:00Z%20TO%20"+endPoints[i+1]+"T00:00:00Z]"

	try: 
		result = urllib2.urlopen(url)
	except urllib2.HTTPError,err:
	        print "ERROR:",url,err.code
	except urllib2.URLError, err:
	        print "ERROR URL",url,err.reason

	try:            
	        jsondata = json.load(result)
	except ValueError:
	        print "Decoding Failed",url
	thisData = []
	thisX = []
	thisY = []
	nh = TH1F("histo_"+str(i),"",len(bins)-1,array('d',bins))
	for facet in jsondata["facet_results"]["fields"]["karma"]["facets"]:
		count = int(facet["count"])
		value = int(facet["value"])
		for x in range(0,count):
			thisData.append(value)
		if value <= 0: continue
		thisX.append(value)
		thisY.append(count)
		nh.Fill(value,count)
	popt,pcov = curve_fit(func,thisX,thisY)
	#print popt,pcov,colors[i]
	print popt[1]/len(thisData)
	scaledY = func(sorted(thisX),popt[0],popt[1]/len(thisData))
	scaledYdata = [float(y)/float(len(thisData)) for y in thisY]
	#print scaledYdata
	allData.append(thisData)
	allX.append(thisX)
	allY.append(thisY)
	maxY.append(max(scaledY))
	minY.append(min(scaledY))
	#nh.Scale(1./nh.Integral())
	nh.SetMarkerColor(colors[i])
	nh.SetMarkerStyle(20+i)
	for j in range(1,nh.GetNbinsX()+1):
		nh.SetBinContent(j,nh.GetBinContent(j)/nh.GetBinWidth(j))
	f1 = TF1("f_"+str(i),"[0]*pow(x,[1])",1,160000)
	f1.SetParameter(0,nh.Integral())
	f1.SetParameter(1,-1)
	nh.Fit(f1,"rl","",5,500)
	nh.GetFunction("f_"+str(i)).SetLineColor(colors[i])
	histos.append(nh)
	#ax.plot(thisX,scaledYdata,'.',color=colors[i],alpha=0.3,label="Users (actual) created between "+endPoints[i]+" and "+endPoints[i+1])
	#ax.plot(sorted(thisX),scaledY,'-',color=colors[i],label="Users (fit) created between "+endPoints[i]+" and "+endPoints[i+1],linewidth=2)


gROOT.SetStyle("Plain")
gStyle.SetOptStat(0)
canvas = TCanvas("c","",800,600)
legend = TLegend(0.35,0.6,0.93,0.88)
legend.SetFillStyle(0)
legend.SetLineStyle(0)
legend.SetTextSize(legend.GetTextSize()*3)
#maxY = 0
#minY = 0.01
histos[0].GetYaxis().SetRangeUser(0.01,100000)
histos[0].GetXaxis().SetRangeUser(0,20000)
for i in range(0,len(endPoints)-1):
	legend.AddEntry(histos[i],"Users created between "+endPoints[i]+" and "+endPoints[i+1],"p")
	if i == 0:
		histos[i].SetXTitle("Karma")
		histos[i].SetYTitle("Users / Unit Karma")
		histos[i].Draw("p")
	histos[i].Draw("psame")

canvas.SetLogy()
canvas.SetLogx()
legend.Draw()

#ax.set_ylabel("Fraction of Users")
#ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),prop={'size':10})
#ax.tick_params(axis='y', colors=colors[i])
#dmax = max(maxY)
#dmin = min(minY)
#ax.set_ylim((min(0.1,dmin/10.),max(dmax*1.2,1.2)))
#ax.set_xlabel('Karma')
#ax.set_xticks(dates)
#ax.set_xticklabels([dates[i].strftime("%Y-%m-%d") if dates[i].day == 1 and dates[i].month % 2 == 1 else "" for i in range(0,len(dates))],rotation=45)
#ax.set_xticks(ticks)
#ax.set_xticklabels(ticklabels)
#ax.set_yscale('log')
#ax.set_xscale('log')
filename="karmaPowers.png"
#fig.autofmt_xdate()
#ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
#plt.title('Distribution of Karma')
#fig.savefig(filename)
#plt.close()

canvas.SaveAs(filename)
