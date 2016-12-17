import csv
from collections import OrderedDict, defaultdict


POSITIONS = ['RB', 'WR', 'TE', 'QB', 'PK', 'Def']
POS_DIR = 'Data/Predictions/'



class LineupDB:
    def __init__(self, week, year, model, algo, max_players):
        self.max_players = max_players
        self.data = defaultdict(str)
        for pos in POSITIONS:
            self.data[pos] = self.loadPosData(pos, week, model, algo)
        self.team = 0
        self.pts = 1
        self.salary = 2

    def loadPosData(self, pos, week, model, algo):
        pos_data = OrderedDict()
        if algo == '':
            algo_formatted = ''
        else:
            algo_formatted = algo + '_'
        file_path = POS_DIR + 'Week' + str(week) + '/' + model + '_' + algo_formatted + pos + '_preds.csv'
        with open(file_path,'rb') as data:
            data.next()
            reader = csv.reader(data, delimiter=',', quotechar='"')
            i = 0
            for line in reader:
                name = line[0]
                pos = line[1]
                team = line[2]
                pts = float(line[3])
                salary = float(line[4])
                
                entry = (team, pts, salary)
                pos_data[name] = entry


                i += 1
                if i > self.max_players: break
        return pos_data




