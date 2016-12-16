from Data.FantasyDB import FantasyDB
from collections import defaultdict

POSITIONS = ['RB', 'WR', 'TE', 'QB', 'PK', 'Def']
POS_DIR = 'Data/Predictions/'
YEAR = '2016'


db = FantasyDB()


def orderDataByWeek(pos_data_by_name):
    pos_data_by_week = defaultdict(list)
    for name in pos_data_by_name.keys():
        data = pos_data_by_name[name][YEAR]
        for week in data.keys():
            if data[week] is None: continue
            # print week, data[week]
            # if pos_data_by_week[week] is None:
            #     pos_data_by_week[week] = []
            pos_data_by_week[week].append((name, data[week]['team'], data[week]['fd_pts'],\
                                                 data[week]['fd_salary']))
    return pos_data_by_week


for pos in POSITIONS:
    pos_data = orderDataByWeek(db.getData(pos))
    # print 'Got data: ',pos_data
    for week in range(2, 15):
        file_path = POS_DIR + 'Week' + str(week) + '/oracle_' + pos + '_preds.csv'
        with open(file_path,'wb') as outfile:
            outfile.truncate()
            outfile.write('"Name","Position","Team","Points","Salary"\n')

            for line in pos_data[str(week)]:
                # print 'Printing: ' + line
                outfile.write('"' + line[0] + '","' + pos +'","' + line[1] + '","' + line[2] + \
                    '","' + line[3] + '"\n')
            


