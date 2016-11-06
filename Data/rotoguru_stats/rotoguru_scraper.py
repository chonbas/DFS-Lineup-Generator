#!/usr/bin/env python
from bs4 import BeautifulSoup as bs
import urllib2
import csv

BASE_URL = "http://rotoguru1.com/cgi-bin/fyday.pl?"

URLS =["http://rotoguru1.com/cgi-bin/fyday.pl?week=1&year=2011&game=fd&scsv=1"] 
YEARS = range(11,17)
NUM_WEEKS = 17
GAME_TYPE = 'fd'
PATH = 'rotoguru_stats/'

def scrapeRawData():
    with open(PATH+'rotoguru.csv','wb') as outfile:
        outfile.truncate()
        for year in YEARS:
            for week in xrange(1,NUM_WEEKS+1):
                url_to_open = BASE_URL + "week=%d&year=20%d&game=fd&scsv=1" %(week, year)
                print url_to_open
                page = urllib2.urlopen(url_to_open)
                soup = bs(page, 'html.parser')
                relevant = soup.find('pre')
                outfile.write(relevant.prettify())
                outfile.write("\n")

def parseRawData():
    writers = {'QB':None,'WR':None,'RB':None,'TE':None,'PK':None,'Def':None}
    fieldnames = ['week', 'year', 'GID', 'name', 'pos', 'team', 'h/a', 'oppt', 'fd points', 'fd salary']

    POS_INDEX = 4
    NAME_INDEX = 3

    for pos in writers.keys():
        outfile = open(PATH + 'roto_'+pos+'.csv','wb')
        outfile.write(';'.join(fieldnames))
        outfile.write('\n')
        outfile.truncate()
        writers[pos] = outfile
        

    with open(PATH+'rotoguru.csv','rb') as infile:
        infile.next()
        rotoreader = csv.reader(infile, delimiter=';', quotechar='"')
        for line in rotoreader:
            if len(line) <= 1:
                continue
            if line[0].find('<pre>') != -1:
                continue
            pos = line[POS_INDEX]
            name = line[NAME_INDEX]
            gap = name.find(',')
            if pos != 'Def':
                name = name[gap+2:] + ' ' + name[:gap]
            line[NAME_INDEX] = name
            line_write = ';'.join(line)
            writers[pos].write(line_write+'\n')

    for pos in writers.keys():
        writers[pos].close()
    
if __name__=='__main__':
    scrapeRawData()
    parseRawData()