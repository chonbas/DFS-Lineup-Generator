import csv
from collections import OrderedDict, defaultdict

class FantasyDataDictionary:
    def __init__(self):
        self.rbs = self.loadRunningBacks()
        self.wrs = self.loadWideReceivers()
        self.tes = self.loadTightEnds()
        self.qbs = self.loadQuarterBacks()
        self.pks = self.loadKickers()
        self.teams = self.loadTeams()

    def loadTeams(self):
        pass

    def dumpRBToFile(self, path):
        with open('nfl_roto_rbs.csv','wb') as outfile:
            outfile.truncate()
            fieldnames = ['name','year','week', 'pos','team', 'h_a','opp', 'score','result','attempts','yards','avg','tds','fum','fd_pts','fd_salary']
            writer = csv.DictWriter(outfile , fieldnames=fieldnames)
            writer.writeheader()
            for name in self.rbs:
                for year in self.rbs[name]:
                        for week in self.rbs[name][year]:
                            if 'name' in self.rbs[name][year][week]:
                                writer.writerow(self.rbs[name][year][week])

    def createNewEntry(self, name):
        year_dict = OrderedDict()
        for i in xrange(2011, 2017):
            week_dict = OrderedDict()
            for j in xrange(1,18):
                week_dict[str(j)] = {}
            year_dict[str(i)] = week_dict
        return year_dict
    
    def loadRotoData(self, pos):
        roto_data = OrderedDict()
        file_path = 'rotoguru_stats/roto_' + pos + '.csv'
        with open(file_path,'rb') as roto:
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
                    roto_data[name] = self.createNewEntry(name)
                roto_data[name][year][week] =  week_entry
        return roto_data

    def loadRunningBacks(self):
        roto_data =self.loadRotoData('RB')
        # nfl
        # week,year,name,team,opp,score,att,yds,avg,td,fum    
        with open('nfl_stats/nflrushers.csv') as nfl:
            nfl.next()
            nflreader = csv.reader(nfl, delimiter=',', quotechar='"')
            for line in nflreader:
                name = line[2]
                if name not in roto_data:
                    continue # if name not in roto_data, then player not a RB
                year = '20' + line[1]
                week = line[0]
                result_score_line = line[5]
                result = result_score_line[0]
                score = result_score_line[1:]
                roto_data[name][year][week]['result'] = result
                roto_data[name][year][week]['score'] = score.lstrip()
                roto_data[name][year][week]['ru_attempts'] = line[6]
                roto_data[name][year][week]['ru_yards'] = line[7]
                roto_data[name][year][week]['ru_avg'] = line[8]
                roto_data[name][year][week]['ru_tds'] = line[9]
                roto_data[name][year][week]['fum'] = line[10]

        with open('nfl_stats/nflreceiving.csv') as nfl:
            nfl.next()
            nflreader = csv.reader(nfl, delimiter=',', quotechar='"')
            for line in nflreader:
                name = line[2]
                if name not in roto_data:
                    continue # if name not in roto_data, then player not a RB
                year = '20' + line[1]
                week = line[0]
                roto_data[name][year][week]['receptions'] = line[6]
                roto_data[name][year][week]['rec_yards'] = line[7]
                roto_data[name][year][week]['rec_avg'] = line[8]
                roto_data[name][year][week]['rec_tds'] = line[9]
                roto_data[name][year][week]['fum'] = line[10]
        return roto_data


    def loadWideReceivers(self):
        roto_data = self.loadRotoData('WR')
        # nfl
        # week,year,name,team,opp,score,att,yds,avg,td,fum 
        ##CHECK FOR TIGHTEND
        with open('nfl_stats/nflreceiving.csv') as nfl:
            nfl.next()
            nflreader = csv.reader(nfl, delimiter=',', quotechar='"')
            for line in nflreader:
                name = line[2]
                if name not in roto_data:
                    continue # if name not in roto_data, then player not a WR
                year = '20' + line[1]
                week = line[0]
                result_score_line = line[5]
                result = result_score_line[0]
                score = result_score_line[1:]
                roto_data[name][year][week]['result'] = result
                roto_data[name][year][week]['score'] = score.lstrip()
                roto_data[name][year][week]['receptions'] = line[6]
                roto_data[name][year][week]['rec_yards'] = line[7]
                roto_data[name][year][week]['rec_avg'] = line[8]
                roto_data[name][year][week]['rec_tds'] = line[9]
                roto_data[name][year][week]['fum'] = line[10]
        return roto_data
    
    def loadTightEnds(self):
        roto_data =self.loadRotoData('TE')
        # nfl
        # week,year,name,team,opp,score,att,yds,avg,td,fum    
        with open('nfl_stats/nflreceiving.csv') as nfl:
            nfl.next()
            nflreader = csv.reader(nfl, delimiter=',', quotechar='"')
            for line in nflreader:
                name = line[2]
                if name not in roto_data:
                    continue # if name not in roto_data, then player not a WR
                year = '20' + line[1]
                week = line[0]
                result_score_line = line[5]
                result = result_score_line[0]
                score = result_score_line[1:]
                roto_data[name][year][week]['result'] = result
                roto_data[name][year][week]['score'] = score.lstrip()
                roto_data[name][year][week]['receptions'] = line[6]
                roto_data[name][year][week]['rec_yards'] = line[7]
                roto_data[name][year][week]['rec_avg'] = line[8]
                roto_data[name][year][week]['rec_tds'] = line[9]
                roto_data[name][year][week]['fum'] = line[10]
        return roto_data

    def loadQuarterBacks(self):
        roto_data =self.loadRotoData('QB')
        # nfl
        # week,year,name,team,opp,score,att,yds,avg,td,fum    
        with open('nfl_stats/nflrushers.csv') as nfl:
            nfl.next()
            nflreader = csv.reader(nfl, delimiter=',', quotechar='"')
            for line in nflreader:
                name = line[2]
                if name not in roto_data:
                    continue # if name not in roto_data, then player not a QB
                year = '20' + line[1]
                week = line[0]
                result_score_line = line[5]
                result = result_score_line[0]
                score = result_score_line[1:]
                roto_data[name][year][week]['result'] = result
                roto_data[name][year][week]['score'] = score.lstrip()
                roto_data[name][year][week]['ru_attempts'] = line[6]
                roto_data[name][year][week]['ru_yards'] = line[7]
                roto_data[name][year][week]['ru_avg'] = line[8]
                roto_data[name][year][week]['ru_tds'] = line[9]

        with open('nfl_stats/nflqbs.csv') as nfl:
            nfl.next()
            nflreader = csv.reader(nfl, delimiter=',', quotechar='"')
            for line in nflreader:
                name = line[2]
                if name not in roto_data:
                    continue # if name not in roto_data, then player not a QB
                year = '20' + line[1]
                week = line[0]
                roto_data[name][year][week]['pass_comp'] = line[6]
                roto_data[name][year][week]['pass_att'] = line[7]
                roto_data[name][year][week]['pass_yds'] = line[8]
                roto_data[name][year][week]['pass_tds'] = line[9]
                roto_data[name][year][week]['int'] = line[10]
                roto_data[name][year][week]['sack'] = line[11]
                roto_data[name][year][week]['fum'] = line[12]
                roto_data[name][year][week]['qb_rating'] = line[13]
        return roto_data

        #week,year,name,team,opp,score,comp,att,yds,td,int,sck,fum,rate

    def loadKickers(self):
        roto_data =self.loadRotoData('PK')
        # nfl
        # week,year,name,team,opp,score,fg-made,fg-att,xp-made,xp-att,pts
        with open('nfl_stats/nflkickers.csv') as nfl:
            nfl.next()
            nflreader = csv.reader(nfl, delimiter=',', quotechar='"')
            for line in nflreader:
                name = line[2]
                if name not in roto_data:
                    continue # if name not in roto_data, then player not a PK
                year = '20' + line[1]
                week = line[0]
                result_score_line = line[5]
                result = result_score_line[0]
                score = result_score_line[1:]
                roto_data[name][year][week]['result'] = result
                roto_data[name][year][week]['score'] = score.lstrip()
                roto_data[name][year][week]['fg-made'] = line[6]
                roto_data[name][year][week]['fg-att'] = line[7]
                roto_data[name][year][week]['xp-made'] = line[8]
                roto_data[name][year][week]['xp-att'] = line[9]
                roto_data[name][year][week]['pts'] = line[10]
        return roto_data