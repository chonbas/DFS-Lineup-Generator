from bs4 import BeautifulSoup as bs
import urllib2
import csv

YEARS = range(11,17)
NUM_WEEKS = 17



with open('fo_teamdef.csv','wb') as outfile:
    outfile.truncate()
    fieldnames = ['year','place','team', 'def-dvoa','last_yr','wt_off','rank','pass_def','pass_rank','rush_def','rush_rank','non-adj-total','non-adj-pass','non-adj-rush','var','var-rank','sched','sched-rank']
    writer = csv.DictWriter(outfile , fieldnames=fieldnames)
    writer.writeheader()
    for year in YEARS:
        url_to_open = "http://www.footballoutsiders.com/stats/teamdef20%d" %(year)
        print url_to_open
        page = urllib2.urlopen(url_to_open)
        soup = bs(page, 'html.parser')
        table = soup.find_all('tr')
        invalid_ctr = 1
        teams_ctr = 0
        for row in table:
            if teams_ctr == 32:
                break
            if invalid_ctr <= 2:
                invalid_ctr += 1
                continue
            new_team = dict((field,0) for field in fieldnames)
            new_team['year'] = year
            field_counter = 1            
            for i in xrange(len(row)):
                try:
                    if i % 2 != 0:
                        field_val =row.contents[i].get_text().encode('ascii','ignore').replace('"','').replace('\n','')
                        new_team[fieldnames[field_counter]] = field_val
                        field_counter += 1
                except(AttributeError):
                    break
            if new_team['place'] != '' and new_team['place'] != 0:
                writer.writerow(new_team)
                teams_ctr+=1
            
