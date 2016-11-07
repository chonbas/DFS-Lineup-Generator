import csv
from collections import OrderedDict, defaultdict, deque

YEARS = range(2011,2017)
WEEKS = range(1,18)

class FantasyDataDictionary:

    def __init__(self):
        self.rbs = self.loadRunningBacks()
        self.wrs = self.loadWideReceivers()
        self.tes = self.loadTightEnds()
        self.qbs = self.loadQuarterBacks()
        self.pks = self.loadKickers()
        self.teams = self.loadTeams()


    def getTrainingExamples(self,pos, game_lead):
        #Defenses take different logic
        if pos == 'Def':
            return self.getDefenseExamples()
        
        data = self.getData(pos)
        teams = self.teams
        keys = self.getKeys(pos)
        training_X = []
        training_Y = []
        #iterate by player to populate a queue of games played
        for name in data:
            game_deck = deque()
            for i in YEARS:
                year = str(i)
                for j in WEEKS:
                    week = str(j)
                    if data[name][year][week] is not None:
                        game_deck.append(data[name][year][week])
            #once queue of games played is created
            #pop off game_lead games for first training example
            #and put them in a new training lead queue
            if len(game_deck) > game_lead:
                game_lead_deck = deque()
                for i in xrange(game_lead):
                    game_lead_deck.append(game_deck.popleft())
                #after popping up game_lead games for first training example
                #continue to pop off a game from the games played queue
                #and add it to the training lead queue
                #continue to do this until we run out of games played 
                while len(game_deck) > 0:
                    new_training_X = []
                    new_training_Y = game_deck[0]['fd_pts'] 
                    for i in xrange(game_lead):
                        game = game_lead_deck[i]
                        year = game['year']
                        team = game['team']
                        opp = game['opp']
                        for key in keys:
                            if key == 'year':
                                continue
                            if key == 'team':
                                new_training_X += self.getTeamData(team, year, pos, 'OFF')
                                continue
                            if key == 'opp':
                                new_training_X += self.getTeamData(opp, year, pos, 'DEF')
                                continue
                            if key == 'h_a':
                                if game[key] == 'h':
                                    new_training_X.append(1)
                                else:
                                    new_training_X.append(0)
                                continue
                            if game[key] == '':
                                new_training_X.append(0)
                                continue
                            new_training_X.append(float(game[key]))
                    training_X.append(new_training_X)
                    training_Y.append(new_training_Y)
                    game_lead_deck.popleft()
                    game_lead_deck.append(game_deck.popleft())
        return training_X, training_Y
                            

    def getTeamData(self,team, year, pos, side_of_ball):
        team_data = self.teams[team][year][side_of_ball]
        data = []
        if pos =='RB' or pos == 'QB':
            for key in self.getKeys('RUN'):
                data.append(float(team_data['Run'][key].strip('%')))
        if pos == 'WR' or pos == 'TE' or pos == 'QB':
            for key in self.getKeys('PASS'):
                data.append(float(team_data['Pass'][key].strip('%')))
        for key in self.getKeys('TEAM_' + side_of_ball):
            data.append(float(team_data['Team'][key].strip('%')))
        data += self.getTeamEfficiencyData(team, year)
        return data
                

    def getTeamEfficiencyData(self,team, year):
        team_eff = self.teams[team][year]['Efficiency']
        data = []
        for key in self.getKeys('TEAM_EFF'):
            if key == 'w_l': #instead of using W-L string, convert to win %
                win_loss = team_eff[key].split('-')
                wins = float(win_loss[0])
                losses = float(win_loss[1])
                data.append( wins / (wins+losses) )
                continue
            data.append(float(team_eff[key].strip('%')))
        return data

            


    def getData(self, pos):
        if pos == 'RB':
            return self.rbs
        if pos == 'WR':
            return self.wrs
        if pos == 'TE':
            return self.tes
        if pos == 'QB':
            return self.qbs
        if pos == 'PK':
            return self.pks
        return None
    
    def getKeys(self, pos):
        RB_KEYS = ['team','year','h_a','opp','fd_pts','fd_salary','ru_attempts','ru_yards','ru_avg','ru_tds',
                'fum','rec_yards','rec_avg','rec_tds']
        WR_KEYS = ['team','year','h_a','opp','fd_pts','fd_salary','fum','rec_yards','rec_avg','rec_tds']
        TE_KEYS = ['team','year','h_a','opp','fd_pts','fd_salary','fum','rec_yards','rec_avg','rec_tds']
        QB_KEYS = ['team','year','h_a','opp','fd_pts','fd_salary','ru_attempts','ru_yards','ru_avg','ru_tds',
                'fum', 'pass_comp', 'pass_att','pass_yds','pass_tds','int','sack','qb_rating']
        PK_KEYS = ['team','year','h_a','opp','fd_pts','fd_salary','fg-made','fg-att','xp-made','xp-att','pts']
        RUN_KEYS = ['rank', 'adj_line_yds', 'rb_yds', 'power_success','power_rank','stuffed','stuffed_rank', 
                            'second_level_yds', 'second_level_rank','open_field_yds', 'open_field_rank']
        PASS_KEYS = ['rank', 'sacks','adj_sack_rate']
        TEAM_OFF_KEYS = ['rank', 'off_dvoa', 'last_yr','wt_off','wt_rank','pass_off','pass_rank', 'rush_off', 'rush_rank',
                            'non_adj_total', 'non_adj_pass', 'non_adj_rush','var', 'var_rank', 'sched', 'sched_rank']
        TEAM_EFF_KEYS = ['rank', 'total_dvoa', 'last_yr', 'non_adj_tot_dvoa','w_l', 'off_dvoa', 'off_rank', 'def_dvoa',
                         'def_rank','st_dvoa', 'st_rank']
        TEAM_DEF_KEYS = ['rank', 'def_dvoa', 'last_yr','wt_def','wt_rank','pass_def','pass_rank', 'rush_def', 'rush_rank',
                          'non_adj_total', 'non_adj_pass', 'non_adj_rush','var', 'var_rank','sched', 'sched_rank']

        if pos == 'RB':
            return RB_KEYS
        if pos == 'WR':
            return WR_KEYS
        if pos == 'TE':
            return TE_KEYS
        if pos == 'QB':
            return QB_KEYS
        if pos == 'PK':
            return PK_KEYS
        if pos == 'RUN':
            return RUN_KEYS
        if pos == 'PASS':
            return PASS_KEYS
        if pos == 'TEAM_OFF':
            return TEAM_OFF_KEYS
        if pos == 'TEAM_DEF':
            return TEAM_DEF_KEYS
        if pos == 'TEAM_EFF':
            return TEAM_EFF_KEYS
        return None

    def createNewEntry(self, name):
        year_dict = OrderedDict()
        for i in YEARS:
            week_dict = OrderedDict()
            for j in WEEKS:
                week_dict[str(j)] = None
            year_dict[str(i)] = week_dict
        return year_dict
    
    def fixTeamName(self, team):
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
        return team

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
                team = self.fixTeamName(line[5].upper())
                h_a = line[6]
                opp = self.fixTeamName(line[7].upper())
                if opp == '-':
                    continue
                fd_pts = line[8]
                fd_salary = line[9]
                entry = {'team':team, 'year':year, 'h_a':h_a, 'opp':opp, 'fd_pts':fd_pts, 'fd_salary':fd_salary}
                if pos == 'Def':
                    name = team
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
                if roto_data[name][year][week] is None:
                    continue
                result_score_line = line[5]
                result = result_score_line[0]
                score = result_score_line[1:]
                # roto_data[name][year][week]['result'] = result
                # roto_data[name][year][week]['score'] = score.lstrip()
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
                if roto_data[name][year][week] is None:
                    continue
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
                if roto_data[name][year][week] is None:
                    continue
                result_score_line = line[5]
                result = result_score_line[0]
                score = result_score_line[1:]
                # roto_data[name][year][week]['result'] = result
                # roto_data[name][year][week]['score'] = score.lstrip()
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
                if roto_data[name][year][week] is None:
                    continue
                result_score_line = line[5]
                result = result_score_line[0]
                score = result_score_line[1:]
                # roto_data[name][year][week]['result'] = result
                # roto_data[name][year][week]['score'] = score.lstrip()
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
                if roto_data[name][year][week] is None:
                    continue
                result_score_line = line[5]
                result = result_score_line[0]
                score = result_score_line[1:]
                # roto_data[name][year][week]['result'] = result
                # roto_data[name][year][week]['score'] = score.lstrip()
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
                if roto_data[name][year][week] is None:
                    continue
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
                if roto_data[name][year][week] is None:
                    continue
                result_score_line = line[5]
                result = result_score_line[0]
                score = result_score_line[1:]
                # roto_data[name][year][week]['result'] = result
                # roto_data[name][year][week]['score'] = score.lstrip()
                roto_data[name][year][week]['fg-made'] = line[6]
                roto_data[name][year][week]['fg-att'] = line[7]
                roto_data[name][year][week]['xp-made'] = line[8]
                roto_data[name][year][week]['xp-att'] = line[9]
                roto_data[name][year][week]['pts'] = line[10]
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
                    if 'DEF' not in roto_data[team][year]:
                        roto_data[team][year]['DEF'] = {'Run':None, 'Pass':None,'Team':None}
                    roto_data[team][year]['DEF']['Pass'] = {'rank':rank, 'sacks':sacks,'adj_sack_rate':adj_sack_rate}
        
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
                    roto_data[team][year]['DEF']['Run'] = entry
        
        #load team defense
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
                # if team in roto_data:
                entry = {'rank':rank, 'def_dvoa':def_dvoa, 'last_yr':last_yr,'wt_def':wt_def,'wt_rank':wt_rank,
                        'pass_def':pass_def,'pass_rank':pass_rank, 'rush_def':rush_def, 'rush_rank':rush_rank,
                        'non_adj_total':non_adj_total, 'non_adj_pass':non_adj_pass, 'non_adj_rush':non_adj_rush,
                        'var':var, 'var_rank':var_rank, 'sched':sched, 'sched_rank':sched_rank}
                roto_data[team][year]['DEF']['Team'] = entry        

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
                    if 'OFF' not in roto_data[team][year]:
                        roto_data[team][year]['OFF'] = {'Run':None, 'Pass':None,'Team':None}
                    roto_data[team][year]['OFF']['Pass'] = {'rank':rank, 'sacks':sacks,'adj_sack_rate':adj_sack_rate}
        
        #load o-line run block
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
                    roto_data[team][year]['OFF']['Run'] = entry
        
        #load team offense
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
                    roto_data[team][year]['OFF']['Team'] = entry   
        
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