import csv
from collections import OrderedDict

POS_DIR = 'Data/Predictions/'
POSITIONS = ['QB', 'WR', 'RB' , 'TE', 'PK', 'Def']
YEAR = 2016

class LineupProbDB:
    def __init__(self, week, max_pos):
        self.max_pos = max_pos
        self.data = OrderedDict()
        self.teams = set()
        print('---------Players to be Considered:-----------')
        for pos in POSITIONS:
            self.data[pos] = self.loadPosData(pos, week)
            print pos
            for player in self.data[pos].items():
                if pos == 'Def':
                    print('%s\t\t\t %.3f'%(player[0], player[1][1]))
                else:
                    print('%s\t\t %.3f'%(player[0], player[1][1]))
            print('----------------------------------------------')
        self.teams = sorted(list(self.teams))
        
    def getExpectedValues(self,pos):
        if pos == 'QB':
            return [-2.07, -12.75, 39.30, 18.75, 25.25]
            # return [-2.02, -10.11, 22.99, 37.20, 20.62]
        if pos == 'WR':
            # return [1.24, 4.23, -16.31, 19.95, 32.55]
            return [0.79, 3.27, -9.58, 12.88, 34.11]
        if pos == 'RB':
            # return [0.31, 3.55, -9.63, 15.59, 36.39]
            return [0.32, 4.13, -11.42, 16.25, 37.19]
        if pos == 'TE':
            # return [2.21, -11.42, 7.01, 21.85, 17.07]
            return [3.15, -19.21, 16.44, 20.14, 16.01]
        if pos == 'PK':
            # return [-3.23, 20.81, -3.34, 19.38, 9.48]
            return [-2.76, 20.03, -1.07, 19.36, 2.89]
        if pos == 'Def':
            return [-6.47, 4.56, 14.83, 2.85, 30.03]
            # return [-5.34, 4.62, 14.13, -1.91, 34.46]

    def getPosData(self,pos):
        return self.data[pos]
    
    def getPlayerData(self, player):
        for pos in POSITIONS:
            if player in self.data[pos]:
                return self.data[pos][player], pos
        return None

    def getPlayerTeamSalaryPos(self, player):
        for pos in POSITIONS:
            if player in self.data[pos]:
                return self.data[pos][player][0], self.data[pos][player][2], pos
        return None, None, None

    
    def loadPosData(self, pos, week):
        pos_data = OrderedDict()
        file_path = POS_DIR + 'Week' + str(week) + '/' +pos + '_preds.csv'
        with open(file_path,'rb') as data:
            data.next()
            reader = csv.reader(data, delimiter=',', quotechar='"')
            for line in reader:
                name = line[0]
                pos = line[1]
                team = line[2]
                self.teams.add(team)
                salary = float(line[4])
                prob_0_5 = float(line[5])
                prob_5_10 = float(line[6])
                prob_10_15 = float(line[7])
                prob_15_20 = float(line[8])
                prob_20 = float(line[9])
                expected_values = self.getExpectedValues(pos)
                expected_pts = prob_0_5* expected_values[0] +\
                                prob_5_10 *  expected_values[1] +\
                                prob_10_15 * expected_values[2] +\
                                prob_15_20 * expected_values[3] +\
                                prob_20 * expected_values[4]

                entry = (team, expected_pts, salary, prob_0_5, prob_5_10, prob_10_15, prob_15_20, prob_20)
                pos_data[name] = entry
        pos_data = OrderedDict(sorted(pos_data.items(), key=lambda x: x[1][1], reverse=True))
        return OrderedDict((list(pos_data.items())[:self.max_pos[pos]]))




