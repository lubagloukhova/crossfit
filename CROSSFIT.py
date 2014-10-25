import feedparser
from django.utils.html import strip_tags
import bs4
import re
import nltk
import pickle
from collections import defaultdict
from datetime import datetime
import csv
import re
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from ggplot import *
import rpy2.robjects as robjects
from datetime import date

def remove_html_markup(s):
    tag = False
    quote = False
    out = " " # try with a space

    for c in s:
            if c == '<' and not quote:
                tag = True
            elif c == '>' and not quote:
                tag = False
            elif (c == '"' or c == "'") and tag:
                quote = not quote
            elif not tag:
                out = out + c

    return out


#############################################################
################## SCRAPE ###################################
#############################################################


try:
    CFfp = feedparser.parse("http://www.crossfit.com/mt-archive2/2014_10.html")
except Exception, err:
    print err.message

html = CFfp['feed']['summary']
soup = bs4.BeautifulSoup(html)

links = soup.findAll("a", {"href" : re.compile("archive2/20")})
links = [l['href'] for l in links]

# parse
wodDict = {}
for l in links:
    try:
        CFfp = feedparser.parse(l)
    except Exception, err:
        print err.message

    html = CFfp['feed']['summary']
    soup = bs4.BeautifulSoup(html)

    s = soup.find("div", {"class" : re.compile("date")})
    for i in range(len(soup.findAll("div", {"class" : re.compile("date")}))-1):
        s = s.findNext("div", {"class" : re.compile("date")})
        workout = s.findNext('p')

        date = (str(s.getText())).strip()
        workout = remove_html_markup(str(workout)).replace('\n', ' ')
        wodDict[date]=workout

        i+=1


pickle.dump(wodDict, open( "wodDict.p", "wb" ) )
wodDict = pickle.load( open( "wodDict.p", "rb" ) )

writer = csv.writer(open('wodDict.csv', 'wb'))
for key, value in wodDict.items():
   writer.writerow([key, value])


#############################################################
################## MASSAGE ##################################
#############################################################

# Daily Dict
d2 = dict((datetime.strptime(k, '%B %d, %Y'), v) for k, v in wodDict.items())

# Yearly Dict
d3 = {}
for k, v in d2.items():
    if d3.has_key(k.year):
        d3[k.year] += str(v)
    else:
        d3[k.year] = str(v)



#############################################################
################## MOVEMENTS ################################
#############################################################

# from crossfit.com
text_file = open("CFmovements.txt", "r")

Movements = text_file.readlines()
Movements = map(lambda s: s.strip().lower(), Movements)

f = open('CFmovements.txt', 'w') # open for 'w'riting
for item in Movements:
  f.write("%s\n" % item)
f.close() # close the file

# count the number of times a movement occurs in an a string
numDict ={}
for move in Movements:
    numDict[move] = len(re.findall(move,d3[d3.keys()[0]].lower(),flags=re.I))

#for each movement, log the date on which the movement occurs
dateDict ={}
for move in Movements:
    for day in d2:
        if len(re.findall(move,d2[day].lower(),flags=re.I))>0:
            if dateDict.has_key(move):
                dateDict[move].append(day)
            else:
                dateDict[move] = []
                dateDict[move].append(day)

## Monthly Cumm of each Movement
movemonthDict={}
for move in Movements:
    month_aggregate = {}
    if dateDict.has_key(move):
        for d in dateDict[move]:
            month, day, year = d.month, d.day, d.year
            if month_aggregate.has_key(date(year, month, 1)):
                month_aggregate[date(year, month, 1)] += 1
            else:
                month_aggregate[date(year, month, 1)] = 1
        movemonthDict[move]=month_aggregate


pickle.dump(dateDict, open( "dateDict.p", "wb" ) )
dateDict = pickle.load( open( "dateDict.p", "rb" ) )

pickle.dump(movemonthDict, open( "movemonthDict.p", "wb" ) )
movemonthDict = pickle.load( open( "movemonthDict.p", "rb" ) )

#############################################################
################## VISUAL ###################################
#############################################################


################## MATPLOTLIB ###############################

# movemonthDict.keys()
# toplot=movemonthDict['tabata']
# toplot2=movemonthDict['burpee']
# plt.bar(toplot.keys(), toplot.values(), width=7, align='center', color='brown')
# plt.bar(toplot2.keys(), toplot2.values(), width=7, align='center', color='y')
# #plt.gcf().autofmt_xdate()
# plt.show()
########

################## GGPLOT ###################################

# Load Previous Work
movemonthDict = pickle.load( open( "movemonthDict.p", "rb" ) )
wodDict = pickle.load( open( "wodDict.p", "rb" ) )
dateDict = pickle.load( open( "dateDict.p", "rb" ) )

# Subset Dict
keys = ['snatch'] #['tabata', 'burpee', 'snatch', 'front squat', 'rope climb']
mmDictsubset = { k: movemonthDict[k] for k in keys }

# Convert to DataFrame
df = pandas.DataFrame(mmDictsubset)
df['year'] = [d.year for d in df.index]
df['date'] = [d.strftime('%Y%m%d') for d in df.index]
df.sort([str(keys[0]), 'date'], ascending=[1, 1]).head(10)
df_lng = pandas.melt(df, id_vars=['date','year'])
result = df_lng.sort(['variable', 'date'], ascending=[1, 1])


plot = ggplot(df_lng, aes(x='date', y='value'))+\
        geom_bar(aes(x='date', weight = 'value', fill='steelblue'))+\
        ylab('Number of Weekly Workouts w/ Snatch') + xlab('Date')
        # geom_vline(xintercept = 20011001)
        #+ scale_x_date(breaks=date_breaks('1 day'), labels='%b %d %Y')\
        # + scale_y_continuous(labels= 'percent')\
        # scale_x_continuous(breaks=['20011001'])

#print plot

ggsave(plot, "ggplotPythonBar_2.pdf")


#############################################################
################## OFF TO R! ################################
#############################################################

rDF = pd.DataFrame(movemonthDict)
rDF.to_csv('movemonthDict.csv', sep=',')


# Day Dict to R
dateDF = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in dateDict.iteritems() ])) # columns are movements, rows are dates (w/ NaT's)
dateDF.to_csv('dateDF.csv', sep=',')
