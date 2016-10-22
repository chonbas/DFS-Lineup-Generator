from bs4 import BeautifulSoup as bs
import urllib2
import csv

# http://rotoguru1.com/cgi-bin/fyday.pl?week=17&year=2011&game=fd&scsv=1

executable_path = {'executable_path':'~/downloads/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'}

BASE_URL = "http://rotoguru1.com/cgi-bin/fyday.pl?"

URLS =["http://rotoguru1.com/cgi-bin/fyday.pl?week=1&year=2011&game=fd&scsv=1"] 
YEARS = range(11,17)
NUM_WEEKS = 17
GAME_TYPE = 'fd'
with open('rotoguru.csv','wb') as outfile:
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
