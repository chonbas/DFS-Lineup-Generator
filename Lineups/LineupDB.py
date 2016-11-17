import csv
from collections import OrderedDict, defaultdict


POSITIONS = ['RB', 'WR', 'TE', 'QB', 'PK', 'Def']
POS_DIR = '../Predictions/'

YEAR = 2016
WEEK = 9

class LineupDB:
    def __init__(self, hashable=True):
        self.data = defaultdict(str)
        for pos in POSITIONS:
            self.data[pos] = self.loadPosData(pos, hashable)
        # self.rbs = self.loadPosData('RB')
        # self.wrs = self.loadPosData('WB')
        # self.tes = self.loadPosData('TE')
        # self.qbs = self.loadPosData('QB')
        # self.pks = self.loadPosData('PK')
        # self.defs = self.loadPosData('Def')
        self.team = 0
        self.pts = 1
        self.salary = 2

    def loadPosData(self, pos, hashable):
        pos_data = OrderedDict()
        file_path = POS_DIR + 'Week' + str(WEEK) + '/' + pos + 'preds.csv'
        with open(file_path,'rb') as data:
            data.next()
            reader = csv.reader(data, delimiter=',', quotechar='"')
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
        return pos_data




