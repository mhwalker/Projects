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
colors[41860] = "black"
colors[35620] = "blue"
colors[71650] = "red"
colors[42660] = "green"
colors[47900] = "magenta"
colors[31100] = "cyan"
colors[37980] = "yellow"
colors[16980] = "yellow"

codes = ["15-1132","15-1031"]
metrodata = dict()

for m,c in metros.iteritems():
	metrodata[m] = dict()
	for year in years:
		ifname = "data_clean/"+str(m)+"_"+str(year)+".dat"
		ifile = open(ifname,"r")
		full = ifile.readlines()
		for line in full:
			splt = line.split()
			if len(splt) < 1: continue
			if splt[0] not in codes: continue
			metrodata[m][year] = [float(splt[i].replace(",","")) for i in range(1,len(splt))]
			print m,year


fig,ax = plt.subplots()
label = 'Average Salary per Year'
fig.subplots_adjust(right=0.86,bottom=0.2)
fig.set_size_inches(18,10)   
dmax = 0   
for m,c in metros.iteritems():
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
plt.title('Average Salary Per Year')
fig.savefig('metroComparison.png')
plt.close()

fig,ax = plt.subplots()
label = 'Delta Salary per Year (%)'
fig.subplots_adjust(right=0.86,bottom=0.2)
fig.set_size_inches(18,10)   
dmax = 0
dmin = 100 
for m,c in metros.iteritems():
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
plt.title('Percentage Change in Salary Per Year')
fig.savefig('deltaMetroComparison.png')
plt.close()
