from bs4 import BeautifulSoup as bs
import urllib2
import csv

YEARS = range(11,17)

with open('fo_dl_runblock.csv','wb') as runblockfile:
    with open('fo_dl_passblock.csv','wb') as passblockfile:

        runblockfile.truncate()
        passblockfile.truncate()

        fieldnames_run = ['year','place','team', 'adj-line-yards','rb-yards','power-sucess','power rank','stuffed','stuffed-rank','2nd_level_yds','2nd_level_rank','open_field_yds','open_field_rank']
        fieldnames_pass = ['year','team','rank','sacks','adjusted_sack_rate']

        writer_run = csv.DictWriter(runblockfile, fieldnames=fieldnames_run)
        writer_run.writeheader()
        writer_pass = csv.DictWriter(passblockfile, fieldnames=fieldnames_pass)
        writer_pass.writeheader()

        for year in YEARS:
            url_to_open = "http://www.footballoutsiders.com/stats/dl20%d" %(year)
            print url_to_open
            page = urllib2.urlopen(url_to_open)
            soup = bs(page, 'html.parser')
            table = soup.find_all('tr')
            invalid_ctr = 1
            team_ctr = 0
            for row in table:
                if team_ctr == 33:
                    break
                if invalid_ctr < 3:
                    invalid_ctr += 1
                    continue
                new_run = dict((field,0) for field in fieldnames_run)
                new_pass = dict((field,0) for field in fieldnames_pass)
                new_run['year'] = year
                new_pass['year'] = year
                field_counter = 1            
                for i in xrange(len(row)):
                    try:
                        if i % 2 != 0:
                            field_val = row.contents[i].get_text().encode('ascii','ignore').replace('"','').replace('\n','')
                            if field_counter < 13:
                                new_run[fieldnames_run[field_counter]] = field_val
                            else:
                                new_pass[fieldnames_pass[field_counter - 12]] = field_val
                            field_counter += 1
                    except(AttributeError):
                        break
                if new_run['place'] != '' and new_run['place'] != 'RUN BLOCKING':
                    writer_run.writerow(new_run)
                    writer_pass.writerow(new_pass)
                    team_ctr += 1
                
