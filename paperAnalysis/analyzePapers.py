import MySQLdb
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import colorsys
import matplotlib.dates as mdates
from mpltools import style
from mpltools import layout
from mpltools import color


style.use('ggplot')

db =  MySQLdb.connect(host="localhost",user="papers",passwd="papers1234pass",db="paperAnalysis",charset='utf8')
cursor = db.cursor()

query = "SELECT collaboration,papertype,nCitations,creation_date FROM papers;"
cursor.execute(query)
results = cursor.fetchall()

atlas = dict()
cms = dict()

for row in results:
    collaboration = row[0]
    papertype = row[1]
    nCitations = int(row[2])
    creation = row[3]
    if row[0] == "CMS":
        if not cms.has_key(papertype):
            cms[papertype] = dict()
            cms[papertype]["dates"] = []
            cms[papertype]["citations"] = []
        cms[papertype]["dates"].append(int((datetime.datetime.now() - creation).days))
        cms[papertype]["citations"].append(nCitations)
    else:
        if not atlas.has_key(papertype):
            atlas[papertype] = dict()
            atlas[papertype]["dates"] = []
            atlas[papertype]["citations"] = []
        atlas[papertype]["dates"].append(int((datetime.datetime.now() - creation).days))
        atlas[papertype]["citations"].append(nCitations)

totalATLASDates = []
totalCMSDates = []
totalATLAScites = []
totalCMScites =[]

for papertype,cmspd in cms.iteritems():
    print papertype
    totalCMSDates.extend(cmspd["dates"])
    totalCMScites.extend(cmspd["citations"])
    if not atlas.has_key(papertype):
        continue
    atlpd = atlas[papertype]
    totalATLASDates.extend(atlpd["dates"])
    totalATLAScites.extend(atlpd["citations"])
    fig,ax = plt.subplots()
    fig.subplots_adjust(right=0.86,bottom=0.2)
    fig.set_size_inches(8,5) 
    label = papertype.upper()+" Papers"
    #ax.scatter(cmspd["dates"],cmspd["citations"],marker="o",color="Green",label="CMS")
    #ax.scatter(atlpd["dates"],atlpd["citations"],marker="s",color="Blue",label="ATLAS")
    ax.scatter(cmspd["dates"],cmspd["citations"],marker="o",color="Green",label="CMS")
    ax.scatter(atlpd["dates"],atlpd["citations"],marker="s",color="Blue",label="ATLAS")
    ax.set_ylabel("Citations")
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),prop={'size':10})
    ax.set_xlabel("Days ago")
    if papertype == "hig":
        ax.set_ylim((2,5000))
        ax.set_yscale("log")
    else:
        ax.set_ylim((0,500))
    ax.set_xlim(ax.get_xlim()[::-1])
    plt.title(label)
    fig.savefig(papertype+".pdf")
    plt.close()

print "total"
fig,ax = plt.subplots()
fig.subplots_adjust(right=0.86,bottom=0.2)
fig.set_size_inches(8,5) 
label = "All Papers"
print len(totalCMSDates),len(totalCMScites),len(totalATLASDates),len(totalATLAScites)
ax.scatter(totalCMSDates,totalCMScites,marker="o",color="Green",label="CMS")
ax.scatter(totalATLASDates,totalATLAScites,marker="s",color="Blue",label="ATLAS")
ax.set_ylabel("Citations")
ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),prop={'size':10})
ax.set_xlabel("Days ago")
ax.set_ylim((2,5000))
ax.set_yscale("log")
ax.set_xlim(ax.get_xlim()[::-1])
plt.title(label)
fig.savefig("total.pdf")
plt.close()
