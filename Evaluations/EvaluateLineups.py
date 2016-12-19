import csv
from Data.FantasyDB import FantasyDB

MDP_LINEUP_FILE = 'Lineups/MDP/Week_'
MDP_OUTPUT_FILE = 'Evaluations/Lineups/Evals_MDP_'

db = FantasyDB()

FIELDNAMES = ['Week','Greed','Predicted Points', 'Actual Points']

def getActualPts(player, year, week, pos):
    pos_data = db.getData(pos)
    try:
        pts = pos_data[player][year][week]['fd_pts']
        return pts
    except TypeError:
        print 'Can\'t find player ' + player + ' in week ' + week
        return 0


def evaluateMDP(start_week, end_week, greed):
    if greed:
        outputpath = MDP_OUTPUT_FILE + '_greed_' + str(start_week)+'_'+str(end_week) + '.csv'
    else:
        outputpath = MDP_OUTPUT_FILE + str(start_week)+'_'+ str(end_week) + '.csv' 
    with open(outputpath, 'wb') as outfile:
        outfile.truncate()
        writer = csv.DictWriter(outfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        for week in range(start_week, end_week + 1):
            if greed:
                inpath = MDP_LINEUP_FILE + 'greed_' + str(week) + '.csv'  
            else:
                inpath = MDP_LINEUP_FILE + str(week) + '.csv'  
            with open(inpath, 'r') as infile:
                infile.next()
                reader = csv.reader(infile, delimiter=',', quotechar='"')
                totalPred = 0
                totalActual = 0
                for line in reader:
                    year, week, name, pos, sal, predPts = line
                    actualPts = getActualPts(name, year, week, pos)
                    totalPred += float(predPts)
                    totalActual += float(actualPts)
                writer.writerow({'Week':week, 'Greed':greed,
                                'Predicted Points':totalPred, 'Actual Points':totalActual})



