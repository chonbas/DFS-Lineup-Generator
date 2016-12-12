import csv
from collections import OrderedDict, defaultdict, deque

YEARS = range(2011,2017)
TRAIN_YEARS = range(2011,2016)

WEEKS = range(1,18)
NFL_DIR = 'Data/nfl_stats/'
ROTO_DIR = 'Data/rotoguru_stats/'
FO_DIR = 'Data/fo_stats/'
FANDUEL_DIR = 'Data/fanduel_lists/'
FINAL_WEEK = 17
EXPECTATION_VALUES = [2.5, 7.5, 12.5, 17.5, 22.5, 27.5]

class FantasyDB:

    def __init__(self):
        self.rbs = self.loadRunningBacks()
        self.wrs = self.loadWideReceivers()
        self.tes = self.loadTightEnds()
        self.qbs = self.loadQuarterBacks()
        self.pks = self.loadKickers()
        self.defs = self.loadDefenses()
        self.teams = self.loadTeams()

    def getPredictionPoints(self, pos, game_lead, year, week):
        data = []
        keys = self.getKeys(pos)
        names = []
        salaries = []
        teams = []
        # 0    1      2   3   4    5   6   7
        # Year,Week,Name,Pos,Team,Opp,H_A,Salary
        with open(FANDUEL_DIR + 'FanDuel-NFL-2016-Week-' + str(week) + '.csv') as fd_list:
            fd_list.next() # skip header
            fdreader = csv.reader(fd_list, delimiter=',', quotechar='"')
            for line in fdreader:
                position = line[3]
                if position != pos:
                    continue
                name = line[2]
                if line[7] == '':
                    salary = 0
                else:
                    salary = float(line[7])
                team = line[4]
                if team == '':
                    continue
                if pos == 'Def':
                    name = team
                opp = line[5]
                if opp == '-' or opp=='':
                    continue
                h_a = float(line[6])
                data_point = self.fetchPrevGameData(pos, name, game_lead, year, week)
                for key in keys:
                    if key == 'team':
                        data_point += self.getTeamData(team, opp, year, pos)
                    if key == 'h_a':
                        data_point.append(h_a)
                    if key == 'fd_salary':
                        data_point.append(salary)
                data.append(data_point)
                names.append(name)
                salaries.append(salary)
                teams.append(team)
        return data, names, salaries, teams

    def fetchGameDataWeekRange(self, pos, name, year, week_start, week_end):
        prevGameData = []
        data = self.getData(pos)
        keys = self.getKeys(pos)        
        year_data = data[name][year]
        for week in xrange(week_start, week_end):
            week_data = year_data[str(week)]
            if week_data is None:
                prevGameData += [0.0 for x in xrange(len(self.getFeatureNames(pos)))]
                continue
            for key in keys:
                if key == 'year':
                    continue
                if key == 'team':
                    prevGameData += self.getTeamData(week_data[key], week_data['opp'], year, pos)
                    continue
                if key == 'h_a':
                    if week_data[key] == 'h':
                        prevGameData.append(1)
                    else:
                        prevGameData.append(0)
                    continue
                if week_data[key] == '':
                    prevGameData.append(0)
                    continue
                prevGameData.append(float(week_data[key]))
        return prevGameData

    def fetchPrevGameData(self, pos, name, game_lead, year, week):
        data = self.getData(pos)
        if name in data:
            prevGameData = []
            week_start = week - game_lead
            if week_start <= 0:
                prev_year_week_start = FINAL_WEEK + week - game_lead
                prev_year = str(int(year) - 1)
                prevGameData += self.fetchGameDataWeekRange(pos, name, prev_year, prev_year_week_start, FINAL_WEEK + 1)
                week_start = 1
            prevGameData += self.fetchGameDataWeekRange(pos, name, year, week_start, week)
            return prevGameData                             
        else:
            return [0.0 for x in xrange(len(self.getFeatureNames(pos)) * game_lead)]   
    
    def computeExpectation(self, pred):
        return  sum([EXPECTATION_VALUES[i]*pred[i] for i in xrange(len(pred))])

    def getClassLabel(self, fd_pts):
        fd_pts = float(fd_pts)
        if 0 <= fd_pts and fd_pts < 5:
            return 0
        if 5 <= fd_pts  and fd_pts < 10:
            return 1
        if 10 <= fd_pts  and fd_pts < 15:
            return 2
        if 15 <= fd_pts and fd_pts < 20:
            return 3
        if 20 <= fd_pts and fd_pts < 25:
            return 4
        return 5
    
    def getFDPointsFromLabel(self, label):
        if label == 0:
            return '0-5'
        if label == 1:
            return '5-10'
        if label == 2:
            return '10-15'
        if label == 3:
            return '15-20'
        if label == 4:
            return '20-25'
        return '25+'

    def getTrainingExamples(self,pos, game_lead, classification):        
        data = self.getData(pos)
        keys = self.getKeys(pos)
        training_X = []
        training_Y = []
        #iterate by player to populate a queue of games played
        for name in data:
            game_deck = deque()
            for i in TRAIN_YEARS:
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
                for i in xrange(game_lead + 1):
                    game_lead_deck.append(game_deck.popleft())
                #after popping up game_lead games for first training example
                #continue to pop off a game from the games played queue
                #and add it to the training lead queue
                #continue to do this until we run out of games played 
                while True:
                    new_training_X = []
                    new_training_Y = game_lead_deck[-1]['fd_pts'] 
                    if classification:
                        new_training_Y = self.getClassLabel(new_training_Y)
                    for i in xrange(game_lead + 1):
                        game = game_lead_deck[i]
                        year = game['year']
                        team = game['team']
                        opp = game['opp']
                        for key in keys:
                            if i == game_lead and (key != 'team' and key != 'h_a' and key != 'opp' and key != 'fd_salary'):
                                continue
                            if key == 'year':
                                continue
                            if key == 'team':
                                new_training_X += self.getTeamData(team, opp, year, pos)
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
                    if len(game_deck) == 0:
                        break
                    game_lead_deck.popleft()
                    game_lead_deck.append(game_deck.popleft())
        return training_X, training_Y

    def getTeamData(self,team, opp, year, pos):
        if pos != 'Def':
            side_of_ball = 'OFF'
            opp_side = 'DEF'
        else:
            side_of_ball = 'DEF'
            opp_side = 'OFF'
        team_data = self.teams[team][year][side_of_ball]
        opp_data = self.teams[opp][year][opp_side]
        data = []
        if pos =='RB' or pos == 'QB' or pos == 'WR' or pos == 'TE':
            for key in self.getKeys('RUN'):
                data.append(float(team_data['Run'][key].strip('%')) - float(opp_data['Run'][key].strip('%')))
        if pos == 'WR' or pos == 'TE' or pos == 'QB' or pos == 'RB':
            for key in self.getKeys('PASS'):
                data.append(float(team_data['Pass'][key].strip('%')) - float(opp_data['Pass'][key].strip('%')))
        for key in self.getKeys('TEAM'):
                data.append(float(team_data['Team'][key].strip('%')) - float(opp_data['Team'][key].strip('%')))
        if pos == 'PK' or pos =='QB':
            data += self.getTeamEfficiencyData(team, opp, year)
        return data

    def getTeamEfficiencyData(self,team, opp, year):
        def computeWinPercentage(eff_data):
            win_loss = eff_data['w_l'].split('-')
            wins = float(win_loss[0])
            losses = float(win_loss[1])
            return wins / (wins+losses)
        team_eff = self.teams[team][year]['Efficiency']
        opp_eff = self.teams[opp][year]['Efficiency']
        data = []
        for key in self.getKeys('EFF'):
            if key == 'w_l': #instead of using W-L string, convert to win %
                team_win_loss = computeWinPercentage(team_eff)
                opp_win_loss = computeWinPercentage(opp_eff)
                data.append( team_win_loss - opp_win_loss )
                continue
            data.append(float(team_eff[key].strip('%')) - float(opp_eff[key].strip('%')))
        return data

    def getFeatureNames(self, pos):
            keys = self.getKeys(pos)

            run_keys = self.getKeys('RUN')
            pass_keys = self.getKeys('PASS')
            team_keys = self.getKeys('TEAM')
            eff_keys = self.getKeys('EFF')

            features = []
            
            for key in keys:
                if key == 'year':
                    continue
                if key == 'team':
                    if pos == 'RB' or pos == 'QB' or pos == 'WR' or pos == 'TE':
                        features += run_keys
                    if pos == 'WR' or pos == 'TE' or pos == 'QB' or pos == 'RB':
                        features += pass_keys
                    features += team_keys
                    if pos == 'PK' or pos == 'QB':
                        features += eff_keys
                    continue
                features.append(key)
            return features            

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
        if pos == 'Def':
            return self.defs
        return None
    

    def getKeys(self, pos):
        RB_KEYS = ['team','year','h_a','fd_pts','fd_salary','ru_attempts','ru_yards','ru_avg','ru_tds',
                'fum','rec_yards','rec_avg','rec_tds']
        WR_KEYS = ['team','year','h_a','fd_pts','fd_salary','fum','rec_yards','rec_avg','rec_tds']
        TE_KEYS = ['team','year','h_a','fd_pts','fd_salary','fum','rec_yards','rec_avg','rec_tds']
        QB_KEYS = ['team','year','h_a','fd_pts','fd_salary','ru_attempts','ru_yards','ru_avg','ru_tds',
                'fum', 'pass_comp', 'pass_att','pass_yds','pass_tds','int','sack','qb_rating']
        PK_KEYS = ['team','year','h_a','fd_pts','fd_salary','fg-made','fg-att','xp-made','xp-att','pts']
        DEF_KEYS = ['team', 'year', 'h_a', 'fd_pts', 'fd_salary']
        RUN_KEYS = ['rank', 'adj_line_yds', 'rb_yds', 'power_success','power_rank','stuffed','stuffed_rank', 
                            'second_level_yds', 'second_level_rank','open_field_yds', 'open_field_rank']
        PASS_KEYS = ['rank', 'sacks','adj_sack_rate']
        TEAM_KEYS = ['rank', 'dvoa', 'last_yr', 'wt_dvoa', 'wt_rank','pass_dvoa', 'pass_rank', 'rush_dvoa',
                    'rush_rank', 'non_adj_total', 'non_adj_pass', 'non_adj_rush','var', 'var_rank','sched', 'sched_rank']
        EFF_KEYS = ['rank', 'total_dvoa', 'last_yr', 'non_adj_tot_dvoa','w_l', 'off_dvoa', 'off_rank', 'def_dvoa',
                         'def_rank','st_dvoa', 'st_rank']

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
        if pos == 'Def':
            return DEF_KEYS
        if pos == 'RUN':
            return RUN_KEYS
        if pos == 'PASS':
            return PASS_KEYS
        if pos == 'TEAM':
            return TEAM_KEYS
        if pos == 'EFF':
            return EFF_KEYS
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
        if team == 'LA':
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
        file_path = ROTO_DIR + 'roto_' + pos + '.csv'
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
                week_entry = defaultdict(str, entry)
                if name not in roto_data:
                    roto_data[name] = self.createNewEntry(name)
                roto_data[name][year][week] =  week_entry
        return roto_data

    def loadRunningBacks(self):
        roto_data =self.loadRotoData('RB')
        # nfl
        # week,year,name,team,opp,score,att,yds,avg,td,fum    
        with open(NFL_DIR + 'nflrushers.csv') as nfl:
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
                roto_data[name][year][week]['ru_attempts'] = line[6]
                roto_data[name][year][week]['ru_yards'] = line[7]
                roto_data[name][year][week]['ru_avg'] = line[8]
                roto_data[name][year][week]['ru_tds'] = line[9]
                roto_data[name][year][week]['fum'] = line[10]

        with open(NFL_DIR + 'nflreceiving.csv') as nfl:
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
        with open(NFL_DIR + 'nflreceiving.csv') as nfl:
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
                roto_data[name][year][week]['receptions'] = line[6]
                roto_data[name][year][week]['rec_yards'] = line[7]
                roto_data[name][year][week]['rec_avg'] = line[8]
                roto_data[name][year][week]['rec_tds'] = line[9]
                roto_data[name][year][week]['fum'] = line[10]
        return roto_data

    def loadDefenses(self):
        return self.loadRotoData('Def')

    def loadTightEnds(self):
        roto_data =self.loadRotoData('TE')
        # nfl
        # week,year,name,team,opp,score,att,yds,avg,td,fum    
        with open(NFL_DIR + 'nflreceiving.csv') as nfl:
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
        with open(NFL_DIR + 'nflrushers.csv') as nfl:
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
                roto_data[name][year][week]['ru_attempts'] = line[6]
                roto_data[name][year][week]['ru_yards'] = line[7]
                roto_data[name][year][week]['ru_avg'] = line[8]
                roto_data[name][year][week]['ru_tds'] = line[9]

        with open(NFL_DIR + 'nflqbs.csv') as nfl:
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
        with open(NFL_DIR + 'nflkickers.csv') as nfl:
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
        with open(FO_DIR + 'fo_dl_passblock.csv') as dlinepass:
            dlinepass.next()
            dlinereader = csv.reader(dlinepass, delimiter=',')
            #year,team,rank,sacks,adjusted_sack_rate
            for line in dlinereader:
                year = '20'+line[0]
                team = self.fixTeamName(line[1].upper())
                rank = line[2]
                sacks = line[3]
                adj_sack_rate= line[4]
                if team in roto_data:
                    if 'DEF' not in roto_data[team][year]:
                        roto_data[team][year]['DEF'] = {'Run':None, 'Pass':None,'Team':None}
                    roto_data[team][year]['DEF']['Pass'] = {'rank':rank, 'sacks':sacks,'adj_sack_rate':adj_sack_rate}
        
        #load d-line run block
        with open(FO_DIR + 'fo_dl_runblock.csv') as dlinerun:
            dlinerun.next()
            dlinereader = csv.reader(dlinerun, delimiter=',')
            #year,place,team,adj-line-yards,rb-yards,power-sucess,power rank,stuffed,stuffed-rank,2nd_level_yds,
            #2nd_level_rank,open_field_yds,open_field_rank
            for line in dlinereader:
                year = '20'+line[0]
                rank = line[1]
                team = self.fixTeamName(line[2].upper())
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
                if team in roto_data:
                    entry = {'rank':rank, 'adj_line_yds':adj_line_yds, 'rb_yds':rb_yds, 'power_success':power_success,
                            'power_rank':power_rank, 'stuffed':stuffed, 'stuffed_rank':stuffed_rank, 
                            'second_level_yds':second_level_yds, 'second_level_rank':second_level_rank,
                            'open_field_yds':open_field_yds, 'open_field_rank':open_field_rank}
                    roto_data[team][year]['DEF']['Run'] = entry
        
        #load team defense
        with open(FO_DIR + 'fo_teamdef.csv') as teamdef:
            teamdef.next()
            teamdefreader = csv.reader(teamdef, delimiter=',')
            #year,place,team,def-dvoa,last_yr,wt_off,rank,pass_def,
            #pass_rank,rush_def,rush_rank,non-adj-total,non-adj-pass,
            #non-adj-rush,var,var-rank,sched,sched-rank
            for line in teamdefreader:
                year = '20'+line[0]
                rank = line[1]
                team = self.fixTeamName(line[2].upper())
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
                # if team in roto_data:
                entry = {'rank':rank, 'dvoa':def_dvoa, 'last_yr':last_yr,'wt_dvoa':wt_def,'wt_rank':wt_rank,
                        'pass_dvoa':pass_def,'pass_rank':pass_rank, 'rush_dvoa':rush_def, 'rush_rank':rush_rank,
                        'non_adj_total':non_adj_total, 'non_adj_pass':non_adj_pass, 'non_adj_rush':non_adj_rush,
                        'var':var, 'var_rank':var_rank, 'sched':sched, 'sched_rank':sched_rank}
                roto_data[team][year]['DEF']['Team'] = entry        

        #load o-line pass block
        with open(FO_DIR + 'fo_ol_passblock.csv') as olinepass:
            olinepass.next()
            olinereader = csv.reader(olinepass, delimiter=',')
            #year,team,rank,sacks,adjusted_sack_rate
            #year,team,rank,sacks,adjusted_sack_rate
            for line in olinereader:
                year = '20'+line[0]
                team = self.fixTeamName(line[1].upper())
                rank = line[2]
                sacks = line[3]
                adj_sack_rate= line[4]
                if team in roto_data:
                    if 'OFF' not in roto_data[team][year]:
                        roto_data[team][year]['OFF'] = {'Run':None, 'Pass':None,'Team':None}
                    roto_data[team][year]['OFF']['Pass'] = {'rank':rank, 'sacks':sacks,'adj_sack_rate':adj_sack_rate}
        
        #load o-line run block
        with open(FO_DIR + 'fo_ol_runblock.csv') as olinerun:
            olinerun.next()
            olinereader = csv.reader(olinerun, delimiter=',')
            #year,place,team,adj-line-yards,rb-yards,power-sucess,power rank,stuffed,stuffed-rank,2nd_level_yds,
            #2nd_level_rank,open_field_yds,open_field_rank
            #year,place,team,adj-line-yards,rb-yards,power-sucess,power rank,stuffed,stuffed-rank,2nd_level_yds,
            #2nd_level_rank,open_field_yds,open_field_rank
            for line in olinereader:
                year = '20'+line[0]
                rank = line[1]
                team = self.fixTeamName(line[2].upper())
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
                if team in roto_data:
                    entry = {'rank':rank, 'adj_line_yds':adj_line_yds, 'rb_yds':rb_yds, 'power_success':power_success,
                            'power_rank':power_rank, 'stuffed':stuffed, 'stuffed_rank':stuffed_rank, 
                            'second_level_yds':second_level_yds, 'second_level_rank':second_level_rank,
                            'open_field_yds':open_field_yds, 'open_field_rank':open_field_rank}
                    roto_data[team][year]['OFF']['Run'] = entry
        
        #load team offense
        with open(FO_DIR + 'fo_teamoff.csv') as teamoff:
            teamoff.next()
            teamoffreader = csv.reader(teamoff, delimiter=',')
            #year,place,team,def-dvoa,last_yr,wt_off,rank,pass_def,
            #pass_rank,rush_def,rush_rank,non-adj-total,non-adj-pass,
            #non-adj-rush,var,var-rank,sched,sched-rank
            for line in teamoffreader:
                year = '20'+line[0]
                rank = line[1]
                team = self.fixTeamName(line[2].upper())
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
                if team in roto_data:
                    entry = {'rank':rank, 'dvoa':off_dvoa, 'last_yr':last_yr,'wt_dvoa':wt_off,'wt_rank':wt_rank,
                            'pass_dvoa':pass_off,'pass_rank':pass_rank, 'rush_dvoa':rush_off, 'rush_rank':rush_rank,
                            'non_adj_total':non_adj_total, 'non_adj_pass':non_adj_pass, 'non_adj_rush':non_adj_rush,
                            'var':var, 'var_rank':var_rank, 'sched':sched, 'sched_rank':sched_rank}
                    roto_data[team][year]['OFF']['Team'] = entry   
        
        #load team effectiveness
        with open(FO_DIR + 'fo_team_eff.csv') as teameff:
            teameff.next()
            teameffreader = csv.reader(teameff, delimiter=',')
            #year,place,team,total_dvoa,last_yr,non-adj-tot-voa,
            #w-l,off_dvoa,off_rank,def_dvoa,def_rank,st_dvoa,st_rank
            for line in teameffreader:
                year = '20'+line[0]
                rank = line[1]
                team = self.fixTeamName(line[2].upper())
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
                if team in roto_data:
                    entry = {'rank':rank, 'total_dvoa':total_dvoa, 'last_yr': last_yr, 'non_adj_tot_dvoa':non_adj_tot_dvoa,
                            'w_l':w_l, 'off_dvoa':off_dvoa, 'off_rank':off_rank, 'def_dvoa':def_dvoa, 'def_rank':def_rank,
                            'st_dvoa':st_dvoa, 'st_rank':st_rank}
                    roto_data[team][year]['Efficiency'] = entry
        return roto_data