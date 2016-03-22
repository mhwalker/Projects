import MySQLdb
import urllib2
import xml.etree.cElementTree as ET
import operator
import matplotlib.pyplot as plt
import colorsys
import simplejson as json
import datetime
import locale
import time

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

locations = dict()
locations[30002187] = "Amarr"
locations[30000142] = "Jita"
#locations[30002510] = "Rens"
locations[30002659] = "Dodixie"
#locations[30002053] = "Hek"

regionmap = dict()
regionmap[10000002] = 30000142
regionmap[10000032] = 30002659
regionmap[10000043] = 30002187

def getJSData(itemID,loc,data):
    dodixieSorted = sorted(data)
    dataDoLo = "  var data"+loc+"Lo_"+str(itemID)+" = ["
    dataDoAvg = "  var data"+loc+"Avg_"+str(itemID)+" = ["
    dataDoHi = "  var data"+loc+"Hi_"+str(itemID)+" = ["
    for iii,day in enumerate(dodixieSorted):
        record = data[day]
        low = record["low"]
        avg = record["avg"]
        hig = record["high"]
        qua = record["quantity"]
        if iii > 0:
            dataDoLo += ","
            dataDoAvg += ","
            dataDoHi += ","
        utcday = str(int((datetime.datetime.strptime(day,"%Y-%m-%d %H:%M:%S") - datetime.datetime(1970,1,1)).total_seconds()*1000))
        dataDoLo += "["+utcday+","+str(low/1000000)+"]"
        dataDoAvg += "["+utcday+","+str(avg/1000000)+"]"
        dataDoHi += "["+utcday+","+str(hig/1000000)+"]"
    dataDoLo += "];\n"
    dataDoAvg += "];\n"
    dataDoHi += "];\n"
    return dataDoLo,dataDoAvg,dataDoHi

def makePlotFunction(itemID):
    line = "$(function(){\n"
    line += "$.plot(\"#div_"+itemID+"\",[\n"
    line += " {\n"
    line += "  data: dataJiAvg_"+itemID+",\n"
    line += "  lines: { show:true , fillColor:\"#00fa00\"},\n"
    line += "  points: {show:true, symbol: \"circle\", fillColor: \"#00fa00\"},\n"
    line += "  label: \"Jita Average\"\n"
    #line += "  yaxis: 1\n"
    line += " },\n"
    line += " {\n"
    line += "  data: dataJiLo_"+itemID+",\n"
    line += "  lines: { show:true, fillColor: \"#00fa00\"},\n"
    line += " },\n"
    line += " {\n"
    line += "  data: dataJiHi_"+itemID+",\n"
    line += "  lines: { show:true, fillColor: \"#00fa00\"},\n"
    line += " },\n"
    line += " {\n"
    line += "  data: dataAmAvg_"+itemID+",\n"
    line += "  lines: { show:true , fillColor:\"#0000fa\"},\n"
    line += "  points: {show:true, symbol: \"diamond\", fillColor: \"#0000fa\"},\n"
    line += "  label: \"Amarr Average\"\n"
    #line += "  yaxis: 1\n"
    line += " },\n"
    line += " {\n"
    line += "  data: dataAmLo_"+itemID+",\n"
    line += "  lines: { show:true, fillColor: \"#0000fa\"},\n"
    line += " },\n"
    line += " {\n"
    line += "  data: dataAmHi_"+itemID+",\n"
    line += "  lines: { show:true, fillColor: \"#0000fa\"},\n"
    line += " },\n"
    line += " {\n"
    line += "  data: dataDoAvg_"+itemID+",\n"
    line += "  lines: { show:true , fillColor:\"#fa0000\"},\n"
    line += "  points: {show:true, symbol: \"square\", fillColor: \"#fa0000\"},\n"
    line += "  label: \"Dodixie Average\"\n"
    #line += "  yaxis: 1\n"
    line += " },\n"
    line += " {\n"
    line += "  data: dataDoLo_"+itemID+",\n"
    line += "  lines: { show:true, fillColor: \"#fa0000\"},\n"
    line += " },\n"
    line += " {\n"
    line += "  data: dataDoHi_"+itemID+",\n"
    line += "  lines: { show:true, fillColor: \"#fa0000\"},\n"
    line += " }\n"
    line += "],\n"
    line += " {\n"
    line += "  xaxis: {mode: \"time\", timeformat:\"%m-%d\"},\n"
    line += "  legend: {position: \"nw\"},\n"
    line += "  colors: [\"#33cc33\",\"#33cc33\",\"#33cc33\",\"#0000fa\",\"#0000fa\",\"#0000fa\",\"#fa0000\",\"#fa0000\",\"#fa0000\"]\n"
    line += " });\n"
    line += "});\n"
    line += "\n\n"
    #line += "plotLineGraph_"+itemID+"();\n"
    return line

def makeBlock(ofile,itemID,things,prices):
    thingName = things[itemID]["name"]
    printItemAction = False
    printItemPrice = False
    line = "<div class=\"container\">\n"
    line += "%s (%s)\n" % (thingName,itemID,)
    line += "  <table class=\"info\">\n"
    line += "  <thead><tr><th rowspan=\"2\">Location</th><th rowspan=\"2\">Graph</th><th colspan=\"4\">Recent History</th><th colspan=\"2\"><a href=\"http://www.eve-central.com/home/quicklook.html?typeid="+str(itemID)+"\">Current Prices</a></th></tr>\n"
    line += "  <tr><th>Low</th><th>Average</th><th>High</th><th>Quantity</th><th>Buy Max</th><th>Sell Min</th></thead>\n"
    line += "  <tbody>\n"
    recentAvg = dict()
    maxAction = 0
    for regionID,locationID in regionmap.iteritems():
        reclow = 0
        recavg = 0
        rechig = 0
        recqua = 0
        avglow = 0
        avgavg = 0
        avghig = 0
        avgqua = 0
        ncount = 0
        lastday = None
        for day,record in things[itemID]["prices"][str(regionID)].iteritems():
            if lastday is None: lastday = day
            if int(record["quantity"]) > 0:
                avglow += float(record["low"])
                avgavg += float(record["avg"])
                avghig += float(record["high"])
                avgqua += int(record["quantity"])
                ncount += 1
            if day > lastday:
                lastday = day
                reclow = float(record["low"])
                recavg = float(record["avg"])
                rechig = float(record["high"])
                recqua = int(record["quantity"])
        if ncount > 0:
            avglow /= float(ncount)
            avgavg /= float(ncount)
            avghig /= float(ncount)
            avgqua /= float(ncount)
        reclow = avglow
        recavg = avgavg
        rechig = avghig
        recqua = avgqua
        recentAvg[regionID] = (reclow,recavg,rechig,recqua)
        minaction = 0
        minprofit = 0
        if recavg > 0 and reclow > 0:
            if recavg - reclow > rechig - recavg:
                minaction = (rechig-recavg)*recqua
                minprofit = (rechig-recavg)/recavg
            else:
                minaction = (recavg-reclow)*recqua
                minprofit = (recavg-reclow)/reclow
        if minaction > 50000000 and minprofit > 0.1 and recqua > 10:
            printItemAction = True
            if minaction > maxAction: maxAction = minaction
    regcount = 0
    for regionID,locationID in regionmap.iteritems():
        for regionID2,locationID2 in regionmap.iteritems():
            if regionID == regionID2: continue
            action = 0
            profit = 0
            if recentAvg[regionID][1] > 0 and recentAvg[regionID2][1] > 0:
                action = min(recentAvg[regionID][3],recentAvg[regionID2][3])*abs(recentAvg[regionID][1]-recentAvg[regionID2][1])
                profit = abs(recentAvg[regionID][1]-recentAvg[regionID2][1])/min(recentAvg[regionID][1],recentAvg[regionID2][1])
                quantity = min(recentAvg[regionID][3],recentAvg[regionID2][3])
            if action > 80000000 and profit > 0.12 and quantity > 10:
                printItemAction = True
                if action > maxAction: maxAction = action
        locationname = locations[locationID]
        sellMin = float(prices[itemID][str(locationID)][0])
        buyMax = float(prices[itemID][str(locationID)][1])
        if buyMax < 2e8: printItemPrice = True
        line += "    <tr><td>"+locationname+"</td>"
        if regcount == 0:
            line += "<td rowspan=\"3\"><div class=\"graph\" id=\"div_"+str(itemID)+"\"></div></td>"
            regcount += 1
        line += "<td>%s</td><td>%s</td><td>%s</td><td>%i</td><td>%s</td><td>%s</td>" % (locale.currency(recentAvg[regionID][0],grouping=True).replace('$','ISK '),locale.currency(recentAvg[regionID][1],grouping=True).replace('$','ISK '),locale.currency(recentAvg[regionID][2],grouping=True).replace('$','ISK '),recentAvg[regionID][3],locale.currency(buyMax,grouping=True).replace('$','ISK '),locale.currency(sellMin,grouping=True).replace('$','ISK '),)
        line += "</tr>\n"
    line += "  </tbody>\n"
    line += "  </table>\n"
    line += "</div>\n"
    line += "<script type=\"text/javascript\">\n"
    dataDoLo,dataDoAvg,dataDoHi = getJSData(itemID,"Do",things[itemID]["prices"]["10000032"])
    line += dataDoLo + dataDoAvg + dataDoHi
    dataJiLo,dataJiAvg,dataJiHi = getJSData(itemID,"Ji",things[itemID]["prices"]["10000002"])
    line += dataJiLo + dataJiAvg + dataJiHi
    dataAmLo,dataAmAvg,dataAmHi = getJSData(itemID,"Am",things[itemID]["prices"]["10000043"])
    line += dataAmLo + dataAmAvg + dataAmHi
    line += "\n"
    line += makePlotFunction(itemID)
    line += "</script>\n"
    line += "\n\n"
    if printItemAction and printItemPrice:
        return maxAction,line
        #ofile.write(line)
    else:
        return 0,""

datafile=open("itemdata.json","r")
things = json.load(datafile)
datafile.close()

pricefile = open("recentprices.json","r")
prices = json.load(pricefile)
pricefile.close()

ofile=open("body.html","w")
actions = dict()
for itemID,ppp in prices.iteritems():
    action,line = makeBlock(ofile,itemID,things,prices)
    actions[action] = line

for key in sorted(actions,reverse=True):
    if key > 0:
        ofile.write(actions[key])

ofile.close()
