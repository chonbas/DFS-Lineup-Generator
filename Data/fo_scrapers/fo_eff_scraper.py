from bs4 import BeautifulSoup as bs
import urllib2
import csv

YEARS = range(11,16)

with open('fo_team_eff.csv','wb') as outfile:
    outfile.truncate()
    fieldnames = ['year','place','team', 'total_dvoa','last_yr','non-adj-tot-voa','w-l','off_dvoa','off_rank','def_dvoa','def_rank','st_dvoa','st_rank']
    writer = csv.DictWriter(outfile , fieldnames=fieldnames)
    writer.writeheader()
    for year in YEARS:
        url_to_open = "http://www.footballoutsiders.com/stats/teameff20%d" %(year)
        print url_to_open
        page = urllib2.urlopen(url_to_open)
        soup = bs(page, 'html.parser')
        table = soup.find_all('tr')
        invalid_ctr = 0
        team_ctr = 0
        for row in table:
            if team_ctr == 32:
                break
            if invalid_ctr < 1:
                invalid_ctr +=1
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
                team_ctr+=1
            