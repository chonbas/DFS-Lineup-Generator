#!/usr/bin/env python
from bs4 import BeautifulSoup as bs
import urllib2
import csv

BASE_URL = 'http://rotoguru1.com/cgi-bin/fyday.pl?'

URLS =['http://rotoguru1.com/cgi-bin/fyday.pl?week=1&year=2011&game=fd&scsv=1'] 
YEARS = range(11,17)
NUM_WEEKS = 17
GAME_TYPE = 'fd'
PATH = 'rotoguru_stats/'

def scrapeRawData():
    with open(PATH+'rotoguru.csv','wb') as outfile:
        outfile.truncate()
        for year in YEARS:
            for week in xrange(1,NUM_WEEKS+1):
                url_to_open = BASE_URL + 'week=%d&year=20%d&game=fd&scsv=1' %(week, year)
                print url_to_open
                page = urllib2.urlopen(url_to_open)
                soup = bs(page, 'html.parser')
                relevant = soup.find('pre')
                outfile.write(relevant.prettify())
                outfile.write('\n')

def standardizeDefenseName(name):
    if name == 'San Francisco Defense':
        return 'SF'
    if name == 'Baltimore Defense':
        return 'BAL'
    if name == 'Chicago Defense':
        return 'CHI'
    if name == 'New York J Defense':
        return 'NYJ'
    if name == 'Philadelphia Defense':
        return 'PHI'
    if name == 'Houston Defense':
        return 'HOU'
    if name == 'Washington Defense':
        return 'WAS'
    if name == 'Buffalo Defense':
        return 'BUF'
    if name == 'Oakland Defense':
        return 'OAK'
    if name == 'Atlanta Defense':
        return 'ATL'
    if name == 'Arizona Defense':
        return 'ARI'
    if name == 'Minnesota Defense':
        return 'MIN'
    if name == 'Green Bay Defense':
        return 'GB'
    if name == 'Denver Defense':
        return 'DEN'
    if name == 'Tampa Bay Defense':
        return 'TB'
    if name == 'Dallas Defense':
        return 'DAL'
    if name == 'Detroit Defense':
        return 'DET'
    if name == 'New England Defense':
        return 'NE'
    if name == 'Indianapolis Defense':
        return 'IND'
    if name == 'Cincinnati Defense':
        return 'CIN'
    if name == 'Jacksonville Defense':
        return 'JAC'
    if name == 'New York G Defense':
        return 'NYG'
    if name == 'Tennessee Defense':
        return 'TEN'
    if name == 'San Diego Defense':
        return 'SD'
    if name == 'New Orleans Defense':
        return 'NO'
    if name == 'Cleveland Defense':
        return 'CLE'
    if name == 'St. Louis Defense':
        return 'LARM'
    if name == 'Carolina Defense':
        return 'CAR'
    if name == 'Kansas City Defense':
        return 'KC'
    if name == 'Seattle Defense':
        return 'SEA'
    if name == 'Miami Defense':
        return 'MIA'
    if name == 'Los Angeles Defense':
        return 'LARM'
    if name == 'Pittsburgh Defense':
        return 'PIT'
    return ''



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
            if pos == 'Def':
                name = standardizeDefenseName(name)
            line[NAME_INDEX] = name
            line_write = ';'.join(line)
            writers[pos].write(line_write+'\n')

    for pos in writers.keys():
        writers[pos].close()
    
if __name__=='__main__':
    scrapeRawData()
    parseRawData()