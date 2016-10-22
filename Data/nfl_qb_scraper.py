from bs4 import BeautifulSoup as bs
import urllib2
import csv

# http://rotoguru1.com/cgi-bin/fyday.pl?week=17&year=2011&game=fd&scsv=1

BASE_URL = "http://www.nfl.com/stats/weeklyleaders?week="

# http://www.nfl.com/stats/weeklyleaders?week=1&season=2016&showCategory=Passing
# 1&season=2016&showCategory=Passing

YEARS = range(11,17)
NUM_WEEKS = 17
GAME_TYPE = 'fd'


with open('nflqbs.csv','wb') as outfile:
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
                        field_val =row.contents[i].get_text().encode('ascii','ignore').replace('"','').replace('\n','')
                        new_qb[fieldnames[field_counter]] = field_val
                        field_counter += 1
                writer.writerow(new_qb)
                #         relevant = soup.find('pre')
                #         outfile.write(relevant.prettify())
                #     outfile.write("\n")