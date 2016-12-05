import csv
from collections import OrderedDict

POSITIONS = ['QB', 'WR', 'RB', 'TE', 'PK', 'Def']
MAX_POS = {'QB':2, 'WR':5, 'RB':4, 'TE':2, 'PK':2, 'Def':2}

POS_DIR = '../Predictions/'

YEAR = 2016
WEEK = 10

class LineupProbDB:
    def __init__(self, hashable=True):
        print MAX_POS
        self.data = OrderedDict()
        self.teams = set()
        for pos in POSITIONS:
            self.data[pos] = self.loadPosData(pos, hashable)
        self.teams = sorted(list(self.teams))

    def getPosData(self,pos):
        return self.data[pos]
    
    def getPlayerData(self, player):
        for pos in POSITIONS:
            if player in self.data[pos]:
                return self.data[pos][player]
        return None

    def getPlayerTeamSalaryPos(self, player):
        for pos in POSITIONS:
            if player in self.data[pos]:
                return self.data[pos][player][0], self.data[pos][player][2], pos
        return None, None, None

    # name,pos,team,expectation,salary,prob_0_5,prob_5_10,prob_10_15,prob_15_20,prob_20+
    def loadPosData(self, pos, hashable):
        pos_data = OrderedDict()
        file_path = POS_DIR + 'Week' + str(WEEK) + '/classification_' + pos + '_preds.csv'
        with open(file_path,'rb') as data:
            data.next()
            reader = csv.reader(data, delimiter=',', quotechar='"')
            for line in reader:
                name = line[0]
                pos = line[1]
                team = line[2]
                self.teams.add(team)
                expected_pts = float(line[3])
                salary = int(line[4])
                prob_0_5 = float(line[5])
                prob_5_10 = float(line[6])
                prob_10_15 = float(line[7])
                prob_15_20 = float(line[8])
                prob_20_25 = float(line[9])
                prob_25 = float(line[10])

                if len(pos_data) == MAX_POS[pos]:
                    continue

                entry = (team, expected_pts, salary, prob_0_5, prob_5_10, prob_10_15, prob_15_20, prob_20_25, prob_25)
                pos_data[name] = entry

        return pos_data




