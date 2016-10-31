import csv
from collections import OrderedDict, defaultdict

def loadRunningBacks():
    def createNewEntry(name, data):
        year_dict = OrderedDict()
        for i in xrange(2011, 2017):
            week_dict = OrderedDict()
            for j in xrange(1,18):
                week_dict[str(j)] = {}
            year_dict[str(i)] = week_dict
        data[name] = year_dict

    roto_data = OrderedDict()

    # roto
    # week;year;GID;name;pos;team;h/a;oppt;fd points;fd salary
    with open('rotoguru_stats/roto_RB.csv','rb') as roto:
        roto.next()
        rotoreader = csv.reader(roto, delimiter=';', quotechar='"')
        for line in rotoreader:
            week = line[0]
            year = line[1]
            name = line[3]
            pos = line[4]
            team = line[5]
            h_a = line[6]
            opp = line[7]
            fd_pts = line[8]
            fd_salary = line[9]
            week_entry = defaultdict
            entry = {'name':name, 'year':year, 'week':week, 'pos':pos, 'team':team, 'h_a':h_a, 'opp':opp, 'fd_pts':fd_pts, 'fd_salary':fd_salary}
            week_entry = defaultdict(str, entry)
            if name not in roto_data:
                createNewEntry(name, roto_data)
            roto_data[name][year][week] =  week_entry


    # nfl
    # week,year,name,team,opp,score,att,yds,avg,td,fum    
    with open('nfl_stats/nflrushers.csv') as nfl:
        nfl.next()
        nflreader = csv.reader(nfl, delimiter=',', quotechar='"')
        for line in nflreader:
            name = line[2]
            if name not in roto_data:
                createNewEntry(name, roto_data)
            year = '20' + line[1]
            week = line[0]
            result_score_line = line[5].replace('\r','').replace('\t',' ')
            result = result_score_line[0]
            score = result_score_line[1:]
            roto_data[name][year][week]['result'] = result
            roto_data[name][year][week]['score'] = score.lstrip()
            roto_data[name][year][week]['attempts'] = line[6]
            roto_data[name][year][week]['yards'] = line[7]
            roto_data[name][year][week]['avg'] = line[8]
            roto_data[name][year][week]['tds'] = line[9]
            roto_data[name][year][week]['fum'] = line[10]
    return roto_data

roto_data = loadRunningBacks()

with open('nfl_roto_rbs.csv','wb') as outfile:
    outfile.truncate()
    fieldnames = ['name','year','week', 'pos','team', 'h_a','opp', 'score','result','attempts','yards','avg','tds','fum','fd_pts','fd_salary']
    writer = csv.DictWriter(outfile , fieldnames=fieldnames)
    writer.writeheader()
    for name in roto_data:
        for year in roto_data[name]:
                for week in roto_data[name][year]:
                    if 'name' in roto_data[name][year][week]:
                        writer.writerow(roto_data[name][year][week])
                    