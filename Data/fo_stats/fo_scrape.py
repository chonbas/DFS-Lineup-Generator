#!/usr/bin/env python
from bs4 import BeautifulSoup as bs
import urllib2
import csv

YEARS = range(11,17)
PATH = 'fo_stats/'

def scrapeDLine():
    with open(PATH+'fo_dl_runblock.csv','wb') as runblockfile:
        with open(PATH+'fo_dl_passblock.csv','wb') as passblockfile:

            runblockfile.truncate()
            passblockfile.truncate()

            fieldnames_run = ['year','place','team', 'adj-line-yards','rb-yards','power-sucess','power rank','stuffed','stuffed-rank','2nd_level_yds','2nd_level_rank','open_field_yds','open_field_rank']
            fieldnames_pass = ['year','team','rank','sacks','adjusted_sack_rate']

            writer_run = csv.DictWriter(runblockfile, fieldnames=fieldnames_run)
            writer_run.writeheader()
            writer_pass = csv.DictWriter(passblockfile, fieldnames=fieldnames_pass)
            writer_pass.writeheader()

            for year in YEARS:
                url_to_open = 'http://www.footballoutsiders.com/stats/dl20%d' %(year)
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

def scrapeTeamD():                    
    with open(PATH+'fo_teamdef.csv','wb') as outfile:
        outfile.truncate()
        fieldnames = ['year','place','team', 'def-dvoa','last_yr','wt_off','rank','pass_def','pass_rank','rush_def','rush_rank','non-adj-total','non-adj-pass','non-adj-rush','var','var-rank','sched','sched-rank']
        writer = csv.DictWriter(outfile , fieldnames=fieldnames)
        writer.writeheader()
        for year in YEARS:
            url_to_open = 'http://www.footballoutsiders.com/stats/teamdef20%d' %(year)
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

def scrapeTeamEff():
    with open(PATH+'fo_team_eff.csv','wb') as outfile:
        outfile.truncate()
        fieldnames = ['year','place','team', 'total_dvoa','last_yr','non-adj-tot-voa','w-l','off_dvoa','off_rank','def_dvoa','def_rank','st_dvoa','st_rank']
        writer = csv.DictWriter(outfile , fieldnames=fieldnames)
        writer.writeheader()
        for year in YEARS:
            url_to_open = 'http://www.footballoutsiders.com/stats/teameff20%d' %(year)
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
                    if year == 16 and (i==10 or i==11):
                        continue
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

def scrapeTeamOff():
    with open(PATH+'fo_teamoff.csv','wb') as outfile:
        outfile.truncate()
        fieldnames = ['year','place','team', 'off-dvoa','last_yr','wt_off','rank','pass_off','pass_rank','rush_off','rush_rank','non-adj-total','non-adj-pass','non-adj-rush','var','var-rank','sched','sched-rank']
        writer = csv.DictWriter(outfile , fieldnames=fieldnames)
        writer.writeheader()
        for year in YEARS:
            url_to_open = 'http://www.footballoutsiders.com/stats/teamoff20%d' %(year)
            print url_to_open
            page = urllib2.urlopen(url_to_open)
            soup = bs(page, 'html.parser')
            table = soup.find_all('tr')
            invalid_ctr = 1
            for row in table:
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

def scrapeOLine():        
    with open(PATH+'fo_ol_runblock.csv','wb') as runblockfile:
        with open(PATH+'fo_ol_passblock.csv','wb') as passblockfile:

            runblockfile.truncate()
            passblockfile.truncate()

            fieldnames_run = ['year','place','team', 'adj-line-yards','rb-yards','power-sucess','power rank','stuffed','stuffed-rank','2nd_level_yds','2nd_level_rank','open_field_yds','open_field_rank']
            fieldnames_pass = ['year','team','rank','sacks','adjusted_sack_rate']

            writer_run = csv.DictWriter(runblockfile, fieldnames=fieldnames_run)
            writer_run.writeheader()
            writer_pass = csv.DictWriter(passblockfile, fieldnames=fieldnames_pass)
            writer_pass.writeheader()

            for year in YEARS:
                url_to_open = 'http://www.footballoutsiders.com/stats/ol20%d' %(year)
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

if __name__ == '__main__':
    scrapeDLine()
    scrapeTeamD()
    scrapeTeamEff()
    scrapeTeamOff()
    scrapeOLine()