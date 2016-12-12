import csv
from collections import OrderedDict, defaultdict


POSITIONS = ['RB', 'WR', 'TE', 'QB', 'PK', 'Def']
POS_DIR = 'Data/Predictions/'
TYPE = 'classification'
MAX_PLAYERS = 5 # number of players to consider for each position group


class LineupDB:
    def __init__(self, week=10, year=2016, hashable=True):
        self.data = defaultdict(str)
        for pos in POSITIONS:
            self.data[pos] = self.loadPosData(pos, hashable, week)
        self.team = 0
        self.pts = 1
        self.salary = 2

    def loadPosData(self, pos, hashable, week):
        pos_data = OrderedDict()
        file_path = POS_DIR + 'Week' + str(week) + '/' + TYPE + "_" + pos + '_preds.csv'
        with open(file_path,'rb') as data:
            data.next()
            reader = csv.reader(data, delimiter=',', quotechar='"')
            i = 0
            for line in reader:
                name = line[0]
                pos = line[1]
                team = line[2]
                pts = float(line[3])
                salary = int(line[4])
                
                if hashable:
                    entry = (team, pts, salary)
                    pos_data[name] = entry
                else:
                    entry = {'name':name, 'team':team}
                    week_entry = defaultdict(str, entry)
                    if pts not in pos_data:
                        pos_data[pts] = OrderedDict()
                    if salary not in pos_data[pts]:
                        pos_data[pts][salary] = []
                    pos_data[pts][salary].append(week_entry)

                if i > MAX_PLAYERS: break
                i += 1
        return pos_data




