import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import colorsys
import matplotlib.dates as mdates

years = range(1999,2013)

metros = dict()
metros[41860] = "San Francisco"
metros[35620] = "New York"
metros[71650] = "Boston"
metros[42660] = "Seattle"
metros[47900] = "Washington D.C."
#metros[31100] = "Los Angeles"
#metros[37980] = "Philadelphia"
#metros[16980] = "Chicago"

colors = dict()
colors[151132] = "black"
colors[231011] = "blue"
colors[111021] = "red"
colors[132011] = "green"
colors[291069] = "magenta"
colors[291111] = "cyan"
colors[37980] = "yellow"
colors[16980] = "yellow"

codemap = dict()
codemap["15-1132"] = 151132
codemap["15-1031"] = 151132
codemap["11-1021"] = 111021
codemap["13-2011"] = 132011
#codemap["21-1021"] = 211021
codemap["23-1011"] = 231011
codemap["29-1069"] = 291069
codemap["29-1111"] = 291111
codemap["29-1141"] = 291111

occupationlabel = dict()
occupationlabel[151132] = "Software Engineer"
occupationlabel[231011] = "Lawyer"
occupationlabel[111021] = "Manager"
occupationlabel[132011] = "Accountant"
#occupationlabel[211021] = "Social Worker"
#occupationlabel[291069] = "Physician"
occupationlabel[291111] = "Nurse"

codes = codemap.keys()

metrodata = dict()
m = 41860
for year in years:
	ifname = "data_clean/"+str(m)+"_"+str(year)+".dat"
	ifile = open(ifname,"r")
	full = ifile.readlines()
	for line in full:
		splt = line.split()
		if len(splt) < 1: continue
		if splt[0] not in codes: continue
		code = codemap[splt[0]]
		if not metrodata.has_key(code): metrodata[code] = dict()
		metrodata[code][year] = [float(splt[i].replace(",","")) for i in range(1,len(splt))]
		print m,year


fig,ax = plt.subplots()
label = 'Average Salary per Year'
fig.subplots_adjust(right=0.86,bottom=0.2)
fig.set_size_inches(18,10)   
dmax = 0

for m,c in occupationlabel.iteritems():
	data = []
	for year in years:
		print m,year,metrodata[m][year]
		data.append(metrodata[m][year][6])
	ax.plot(years,data,'-',color=colors[m],label=c)
	dmax = max(max(data),dmax)
print dmax
ax.set_ylabel(label)
ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),prop={'size':10})
#ax.tick_params(axis='y', colors=colors[i])
ax.set_ylim((0,max(dmax*1.2,1.2)))
ax.set_xlabel('Year')
#ax.set_xticks(dates)
#ax.set_xticklabels([dates[i].strftime("%Y-%m-%d") if dates[i].day == 1 and dates[i].month % 2 == 1 else "" for i in range(0,len(dates))],rotation=45)
ticklabels = [str(year) for year in years]
ax.set_xticks(years)
ax.set_xticklabels(ticklabels)
fig.autofmt_xdate()
ax.fmt_xdata = mdates.DateFormatter('%Y')
plt.title('Average Salary Per Year in San Francisco')
fig.savefig('jobComparison.png')
plt.close()

fig,ax = plt.subplots()
label = 'Delta Salary per Year (%)'
fig.subplots_adjust(right=0.86,bottom=0.2)
fig.set_size_inches(18,10)   
dmax = 0
dmin = 100 
for m,c in occupationlabel.iteritems():
	data = []
	last = 0
	for year in years:
		delta = 0
		if last != 0:
			delta = (metrodata[m][year][6]-last)/last * 100
		data.append(delta)
		last = metrodata[m][year][6]
	ax.plot(years,data,'-',color=colors[m],label=c)
	dmax = max(max(data),dmax)
	dmin = min(min(data),dmin)
print dmin,dmax
ax.set_ylabel(label)
ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),prop={'size':10})
#ax.tick_params(axis='y', colors=colors[i])
ax.set_ylim((min(dmin*1.2,-1),max(dmax*1.2,1.2)))
ax.set_xlabel('Year')
#ax.set_xticks(dates)
#ax.set_xticklabels([dates[i].strftime("%Y-%m-%d") if dates[i].day == 1 and dates[i].month % 2 == 1 else "" for i in range(0,len(dates))],rotation=45)
ticklabels = [str(year) for year in years]
ax.set_xticks(years)
ax.set_xticklabels(ticklabels)
fig.autofmt_xdate()
ax.fmt_xdata = mdates.DateFormatter('%Y')
plt.title('Percentage Change in Salary Per Year in San Francisco')
fig.savefig('deltaJobComparison.png')
plt.close()
