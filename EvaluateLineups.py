import csv
from Data.FantasyDB import FantasyDB

CSP_LINEUP_FILE = 'Lineups/CSP_oracle_lineup'
CSP_OUTPUT_FILE = 'Evaluations/Evals_CSP_oracle_2_14.csv'

MDP_LINEUP_FILE = 'Lineups/MDP/Week_RF_'
MDP_OUTPUT_FILE = 'Evaluations/Evals_MDP_RF_2_14.csv'
MDP_END_WEEK = 14

db = FantasyDB()

def getActualPts(player, year, week, pos):
    pos_data = db.getData(pos)
    try:
        pts = pos_data[player][year][week]['fd_pts']
        return pts
    except TypeError:
        print 'Can\'t find player ' + player + ' in week ' + week
        return 0

def evaluateCSP():
    with open(CSP_OUTPUT_FILE, 'wb') as outfile:
        outfile.truncate()
        outfile.write('"Week","Predicted Points","Actual Points"\n')
        with open(CSP_LINEUP_FILE  + '.csv', 'r') as infile:
            infile.next()
            reader = csv.reader(infile, delimiter=',', quotechar='"')
            prevWeek = None
            totalPred = 0
            totalActual = 0
            for line in reader:
                year, week, name, pos, sal, predPts = line
                actualPts = getActualPts(name, year, week, pos)
                if prevWeek == None: prevWeek = week

                if week != prevWeek:
                    outfile.write('"' + prevWeek + '","' + str(totalPred) + '","' + str(totalActual) + '"\n')
                    prevWeek = week
                    totalPred = 0
                    totalActual = 0
                totalPred += float(predPts)
                totalActual += float(actualPts)
            outfile.write('"' + week + '","' + str(totalPred) + '","' + str(totalActual) + '"\n')

def evaluateMDP():
    with open(MDP_OUTPUT_FILE, 'wb') as outfile:
        outfile.truncate()
        outfile.write('"Week","Predicted Points","Actual Points"\n')
        for week in range(2,MDP_END_WEEK + 1):
            with open(MDP_LINEUP_FILE  + str(week) + '.csv', 'r') as infile:
                infile.next()
                reader = csv.reader(infile, delimiter=',', quotechar='"')
                prevWeek = None
                totalPred = 0
                totalActual = 0
                for line in reader:
                    year, week, name, pos, sal, predPts = line
                    actualPts = getActualPts(name, year, week, pos)
                    if prevWeek == None: prevWeek = week

                    if week != prevWeek:
                        outfile.write('"' + prevWeek + '","' + str(totalPred) + '","' + str(totalActual) + '"\n')
                        prevWeek = week
                        totalPred = 0
                        totalActual = 0
                    totalPred += float(predPts)
                    totalActual += float(actualPts)
                outfile.write('"' + week + '","' + str(totalPred) + '","' + str(totalActual) + '"\n')

evaluateCSP()
evaluateMDP()



