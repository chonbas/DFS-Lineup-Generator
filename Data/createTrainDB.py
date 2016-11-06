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
                team = line[5].upper()
                h_a = line[6]
                opp = line[7].upper()
                fd_pts = line[8]
                fd_salary = line[9]
                week_entry = defaultdict
                if team == 'STL':
                    team = 'LARM'
                if team == 'LAR':
                    team = 'LARM'
                if team == 'NWE':
                    team = 'NE'
                if team == 'SFO':
                    team = 'SF'
                if team == 'GNB':
                    team = 'GB'
                if team == 'TAM':
                    team = 'TB'
                if team == 'SDG':
                    team = 'SD'
                if team == 'NOR':
                    team = 'NO'
                if team == 'KAN':
                    team = 'KC'
                if opp == 'STL':
                    opp = 'LARM'
                entry = {'name':name, 'year':year, 'week':week, 'pos':pos, 'team':team, 'h_a':h_a, 'opp':opp, 'fd_pts':fd_pts, 'fd_salary':fd_salary}
                if pos == 'Def':
                    name = team
                week_entry = defaultdict(str, entry)
                if name not in roto_data:
                    roto_data[name] = self.createNewEntry(name)
                roto_data[name][year][week] =  week_entry
        return roto_data

    def loadTeams(self):
        roto_data = self.loadRotoData('Def')
        #load defensive stats

        #load d-line pass block
        with open('fo_stats/fo_dl_passblock.csv') as dlinepass:
            dlinepass.next()
            dlinereader = csv.reader(dlinepass, delimiter=',')
            #year,team,rank,sacks,adjusted_sack_rate
            for line in dlinereader:
                year = '20'+line[0]
                team = line[1]
                rank = line[2]
                sacks = line[3]
                adj_sack_rate= line[4]
                if team == 'STL':
                    team = 'LARM'
                if team in roto_data:
                    if 'Defense' not in roto_data[team][year]:
                        roto_data[team][year]['Defense'] = {'Run':None, 'Pass':None,'Team':None}
                    roto_data[team][year]['Defense']['Pass'] = {'rank':rank, 'sacks':sacks,'adj_sack_rate':adj_sack_rate}
        
        #load d-line run block
        with open('fo_stats/fo_dl_runblock.csv') as dlinerun:
            dlinerun.next()
            dlinereader = csv.reader(dlinerun, delimiter=',')
            #year,place,team,adj-line-yards,rb-yards,power-sucess,power rank,stuffed,stuffed-rank,2nd_level_yds,
            #2nd_level_rank,open_field_yds,open_field_rank
            for line in dlinereader:
                year = '20'+line[0]
                rank = line[1]
                team = line[2]
                adj_line_yds = line[3]
                rb_yds = line[4]
                power_success = line[5]
                power_rank = line[6]
                stuffed = line[7]
                stuffed_rank = line[8]
                second_level_yds = line[9]
                second_level_rank = line[10]
                open_field_yds = line[11]
                open_field_rank = line[12]
                if team == 'STL':
                    team = 'LARM'
                if team in roto_data:
                    entry = {'rank':rank, 'adj_line_yds':adj_line_yds, 'rb_yds':rb_yds, 'power_success':power_success,
                            'power_rank':power_rank, 'stuffed':stuffed, 'stuffed_rank':stuffed_rank, 
                            'second_level_yds':second_level_yds, 'second_level_rank':second_level_rank,
                            'open_field_yds':open_field_yds, 'open_field_rank':open_field_rank}
                    roto_data[team][year]['Defense']['Run'] = entry
        
        #load team deff
        with open('fo_stats/fo_teamdef.csv') as teamdef:
            teamdef.next()
            teamdefreader = csv.reader(teamdef, delimiter=',')
            #year,place,team,def-dvoa,last_yr,wt_off,rank,pass_def,
            #pass_rank,rush_def,rush_rank,non-adj-total,non-adj-pass,
            #non-adj-rush,var,var-rank,sched,sched-rank
            for line in teamdefreader:
                year = '20'+line[0]
                rank = line[1]
                team = line[2]
                def_dvoa = line[3]
                last_yr = line[4]
                wt_def = line[5]
                wt_rank = line[6]
                pass_def = line[7]
                pass_rank = line[8]
                rush_def = line[9]
                rush_rank = line[10]
                non_adj_total = line[11]
                non_adj_pass = line[12]
                non_adj_rush = line[13]
                var = line[14]
                var_rank = line[15]
                sched = line[16]
                sched_rank = line[17]
                if team == 'STL':
                    team = 'LARM'
                if team in roto_data:
                    entry = {'rank':rank, 'def_dvoa':def_dvoa, 'last_yr':last_yr,'wt_def':wt_def,'wt_rank':wt_rank,
                            'pass_def':pass_def,'pass_rank':pass_rank, 'rush_def':rush_def, 'rush_rank':rush_rank,
                            'non_adj_total':non_adj_total, 'non_adj_pass':non_adj_pass, 'non_adj_rush':non_adj_rush,
                            'var':var, 'var_rank':var_rank, 'sched':sched, 'sched_rank':sched_rank}
                    roto_data[team][year]['Defense']['Team'] = entry        

        #load o-line pass block
        with open('fo_stats/fo_ol_passblock.csv') as olinepass:
            olinepass.next()
            olinereader = csv.reader(olinepass, delimiter=',')
            #year,team,rank,sacks,adjusted_sack_rate
            #year,team,rank,sacks,adjusted_sack_rate
            for line in olinereader:
                year = '20'+line[0]
                team = line[1]
                rank = line[2]
                sacks = line[3]
                adj_sack_rate= line[4]
                if team == 'STL':
                    team = 'LARM'
                if team in roto_data:
                    if 'Offense' not in roto_data[team][year]:
                        roto_data[team][year]['Offense'] = {'Run':None, 'Pass':None,'Team':None}
                    roto_data[team][year]['Offense']['Pass'] = {'rank':rank, 'sacks':sacks,'adj_sack_rate':adj_sack_rate}
        
        #load d-line run block
        with open('fo_stats/fo_ol_runblock.csv') as olinerun:
            olinerun.next()
            olinereader = csv.reader(olinerun, delimiter=',')
            #year,place,team,adj-line-yards,rb-yards,power-sucess,power rank,stuffed,stuffed-rank,2nd_level_yds,
            #2nd_level_rank,open_field_yds,open_field_rank
            #year,place,team,adj-line-yards,rb-yards,power-sucess,power rank,stuffed,stuffed-rank,2nd_level_yds,
            #2nd_level_rank,open_field_yds,open_field_rank
            for line in olinereader:
                year = '20'+line[0]
                rank = line[1]
                team = line[2]
                adj_line_yds = line[3]
                rb_yds = line[4]
                power_success = line[5]
                power_rank = line[6]
                stuffed = line[7]
                stuffed_rank = line[8]
                second_level_yds = line[9]
                second_level_rank = line[10]
                open_field_yds = line[11]
                open_field_rank = line[12]
                if team == 'STL':
                    team = 'LARM'
                if team in roto_data:
                    entry = {'rank':rank, 'adj_line_yds':adj_line_yds, 'rb_yds':rb_yds, 'power_success':power_success,
                            'power_rank':power_rank, 'stuffed':stuffed, 'stuffed_rank':stuffed_rank, 
                            'second_level_yds':second_level_yds, 'second_level_rank':second_level_rank,
                            'open_field_yds':open_field_yds, 'open_field_rank':open_field_rank}
                    roto_data[team][year]['Offense']['Run'] = entry
        
        #load team deff
        with open('fo_stats/fo_teamoff.csv') as teamoff:
            teamoff.next()
            teamoffreader = csv.reader(teamoff, delimiter=',')
            #year,place,team,def-dvoa,last_yr,wt_off,rank,pass_def,
            #pass_rank,rush_def,rush_rank,non-adj-total,non-adj-pass,
            #non-adj-rush,var,var-rank,sched,sched-rank
            for line in teamoffreader:
                year = '20'+line[0]
                rank = line[1]
                team = line[2]
                off_dvoa = line[3]
                last_yr = line[4]
                wt_off = line[5]
                wt_rank = line[6]
                pass_off = line[7]
                pass_rank = line[8]
                rush_off = line[9]
                rush_rank = line[10]
                non_adj_total = line[11]
                non_adj_pass = line[12]
                non_adj_rush = line[13]
                var = line[14]
                var_rank = line[15]
                sched = line[16]
                sched_rank = line[17]
                if team == 'STL':
                    team = 'LARM'
                if team in roto_data:
                    entry = {'rank':rank, 'off_dvoa':off_dvoa, 'last_yr':last_yr,'wt_off':wt_off,'wt_rank':wt_rank,
                            'pass_off':pass_off,'pass_rank':pass_rank, 'rush_off':rush_off, 'rush_rank':rush_rank,
                            'non_adj_total':non_adj_total, 'non_adj_pass':non_adj_pass, 'non_adj_rush':non_adj_rush,
                            'var':var, 'var_rank':var_rank, 'sched':sched, 'sched_rank':sched_rank}
                    roto_data[team][year]['Defense']['Team'] = entry   
        
        #load team effectiveness
        with open('fo_stats/fo_team_eff.csv') as teameff:
            teameff.next()
            teameffreader = csv.reader(teameff, delimiter=',')
            #year,place,team,total_dvoa,last_yr,non-adj-tot-voa,
            #w-l,off_dvoa,off_rank,def_dvoa,def_rank,st_dvoa,st_rank
            for line in teameffreader:
                year = '20'+line[0]
                rank = line[1]
                team = line[2]
                total_dvoa = line[3]
                last_yr = line[4]
                non_adj_tot_dvoa  = line[5]
                w_l  = line[6]
                off_dvoa = line[7]
                off_rank = line[8]
                def_dvoa = line[9]
                def_rank = line[10]
                st_dvoa = line[11]
                st_rank = line[12]
                if team == 'STL':
                    team = 'LARM'
                if team in roto_data:
                    entry = {'rank':rank, 'total_dvoa':total_dvoa, 'last_yr': last_yr, 'non_adj_tot_dvoa':non_adj_tot_dvoa,
                            'w_l':w_l, 'off_dvoa':off_dvoa, 'off_rank':off_rank, 'def_dvoa':def_dvoa, 'def_rank':def_rank,
                            'st_dvoa':st_dvoa, 'st_rank':st_rank}
                    roto_data[team][year]['Efficiency'] = entry
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