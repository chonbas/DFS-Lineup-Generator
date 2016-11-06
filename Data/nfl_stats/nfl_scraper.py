#!/usr/bin/env python
from bs4 import BeautifulSoup as bs
import urllib2
import csv

YEARS = range(11,17)
NUM_WEEKS = 17
PATH = 'nfl_stats/'

def scrapeQBs():
    with open(PATH+'nflqbs.csv','wb') as outfile:
        outfile.truncate()
        fieldnames = ['week','year', 'name','team','opp','score','comp','att','yds','td','int','sck','fum','rate']
        writer = csv.DictWriter(outfile , fieldnames=fieldnames)
        writer.writeheader()
        for year in YEARS:
            for week in xrange(1,NUM_WEEKS+1):
                url_to_open = "http://www.nfl.com/stats/weeklyleaders?week=%d&season=20%d&showCategory=Passing" %(week, year)
                print url_to_open
                page = urllib2.urlopen(url_to_open)
                soup = bs(page, 'html.parser')
                table = soup.find_all('tr')
                first = True
                for row in table:
                    if first:
                        first = False
                        continue
                    new_qb = dict((field,0) for field in fieldnames)
                    new_qb['week'] = week
                    new_qb['year'] = year
                    field_counter = 2
                    for i in xrange(len(row)):
                        if i % 2 != 0:
                            field_val =row.contents[i].get_text().encode('ascii','ignore').replace('"','').replace('\n','').replace('\r','').replace('\t',' ')
                            new_qb[fieldnames[field_counter]] = field_val
                            field_counter += 1
                    writer.writerow(new_qb)
def scrapeSacks():
    with open(PATH+'nflsacks.csv','wb') as outfile:
        outfile.truncate()
        fieldnames = ['week','year', 'name','team','opp','score','sacks','sack-yds','qb-hits','tackles','assists','fum-forced','fum-rec']
        writer = csv.DictWriter(outfile , fieldnames=fieldnames)
        writer.writeheader()
        for year in YEARS:
            for week in xrange(1,NUM_WEEKS+1):
                url_to_open = "http://www.nfl.com/stats/weeklyleaders?week=%d&season=20%d&showCategory=Defensive" %(week, year)
                print url_to_open
                page = urllib2.urlopen(url_to_open)
                soup = bs(page, 'html.parser')
                table = soup.find_all('tr')
                first = True
                for row in table:
                    if first:
                        first = False
                        continue
                    new_player = dict((field,0) for field in fieldnames)
                    new_player['week'] = week
                    new_player['year'] = year
                    field_counter = 2
                    for i in xrange(len(row)):
                        if i % 2 != 0:
                            field_val =row.contents[i].get_text().encode('ascii','ignore').replace('"','').replace('\n','').replace('\r','').replace('\t',' ')
                            new_player[fieldnames[field_counter]] = field_val
                            field_counter += 1
                    writer.writerow(new_player)

def scrapeReceivers():
    with open(PATH+'nflreceiving.csv','wb') as outfile:
        outfile.truncate()
        fieldnames = ['week','year', 'name','team','opp','score','rec','yds','avg','td','fum']
        writer = csv.DictWriter(outfile , fieldnames=fieldnames)
        writer.writeheader()
        for year in YEARS:
            for week in xrange(1,NUM_WEEKS+1):
                url_to_open = "http://www.nfl.com/stats/weeklyleaders?week=%d&season=20%d&showCategory=Receiving" %(week, year)
                print url_to_open
                page = urllib2.urlopen(url_to_open)
                soup = bs(page, 'html.parser')
                table = soup.find_all('tr')
                first = True
                for row in table:
                    if first:
                        first = False
                        continue
                    new_player = dict((field,0) for field in fieldnames)
                    new_player['week'] = week
                    new_player['year'] = year
                    field_counter = 2
                    for i in xrange(len(row)):
                        if i % 2 != 0:
                            field_val =row.contents[i].get_text().encode('ascii','ignore').replace('"','').replace('\n','').replace('\r','').replace('\t',' ')
                            new_player[fieldnames[field_counter]] = field_val
                            field_counter += 1
                    writer.writerow(new_player)

def scraperRushers():
    with open(PATH+'nflrushers.csv','wb') as outfile:
        outfile.truncate()
        fieldnames = ['week','year', 'name','team','opp','score','att','yds','avg','td','fum']
        writer = csv.DictWriter(outfile , fieldnames=fieldnames)
        writer.writeheader()
        for year in YEARS:
            for week in xrange(1,NUM_WEEKS+1):
                url_to_open = "http://www.nfl.com/stats/weeklyleaders?week=%d&season=20%d&showCategory=Rushing" %(week, year)
                print url_to_open
                page = urllib2.urlopen(url_to_open)
                soup = bs(page, 'html.parser')
                table = soup.find_all('tr')
                first = True
                for row in table:
                    if first:
                        first = False
                        continue
                    new_player = dict((field,0) for field in fieldnames)
                    new_player['week'] = week
                    new_player['year'] = year
                    field_counter = 2
                    for i in xrange(len(row)):
                        if i % 2 != 0:
                            field_val =row.contents[i].get_text().encode('ascii','ignore').replace('"','').replace('\n','').replace('\r','').replace('\t',' ')
                            new_player[fieldnames[field_counter]] = field_val
                            field_counter += 1
                    writer.writerow(new_player)

def scrapeKickers():
    with open(PATH+'nflkickers.csv','wb') as outfile:
        outfile.truncate()
        fieldnames = ['week','year', 'name','team','opp','score','fg-made','fg-att','xp-made','xp-att','pts']
        writer = csv.DictWriter(outfile , fieldnames=fieldnames)
        writer.writeheader()
        for year in YEARS:
            for week in xrange(1,NUM_WEEKS+1):
                url_to_open = "http://www.nfl.com/stats/weeklyleaders?week=%d&season=20%d&showCategory=Placekick" %(week, year)
                print url_to_open
                page = urllib2.urlopen(url_to_open)
                soup = bs(page, 'html.parser')
                table = soup.find_all('tr')
                first = True
                for row in table:
                    if first:
                        first = False
                        continue
                    new_player = dict((field,0) for field in fieldnames)
                    new_player['week'] = week
                    new_player['year'] = year
                    field_counter = 2
                    for i in xrange(len(row)):
                        if i % 2 != 0:
                            field_val =row.contents[i].get_text().encode('ascii','ignore').replace('"','').replace('\n','').replace('\r','').replace('\t',' ')
                            new_player[fieldnames[field_counter]] = field_val
                            field_counter += 1
                    writer.writerow(new_player)

if __name__=='__main__':
    scrapeQBs()
    scrapeReceivers()
    scraperRushers()
    scrapeKickers()
    scrapeSacks()