import csv
# from FantasyMDP import FantasyMDP
# from FantasyCSPConstructor import FantasyCSPConstructor
# from util import ValueIteration
# from BacktrackingSearch import BacktrackingSearch
from FantasyDB import FantasyDB

# #Note: really slow. Would not recommend.
# mdp = FantasyMDP()
# alg = ValueIteration()
# alg.solve(mdp, .001)

LINEUP_FILE = 'Lineups/MDP/Week12.csv'
OUTPUT_FILE = '2016_12_MDPPredictionsVsActual.csv'

WEEK = '12'

db = FantasyDB()
def getActualPts(player, year, week):
    pos_data = db.getData(pos)
    try:
        pts = pos_data[player][year][week]['fd_pts']
        return pts
    except TypeError:
        print 'Can\'t find player ' + player + ' in week ' + week
        return 0

with open(LINEUP_FILE, 'r') as infile:
    infile.next()
    reader = csv.reader(infile, delimiter=',', quotechar='"')
    with open(OUTPUT_FILE, 'w') as outfile:
        outfile.truncate()
        outfile.write('"Player","Position","Salary","Predicted Points","Actual Points"\n')

        totalPred = 0
        totalActual = 0
        totalSalary = 0
        for line in reader:
            year, week, name, pos, sal, predPts = line
            actualPts = getActualPts(name, year, week)

            if week == WEEK:
                outfile.write('"' + name + '","' + pos + '","' + sal + '","' + str(predPts) + '","' + str(actualPts) + '"\n')
                prevWeek = week
                totalPred += float(predPts)
                totalActual += float(actualPts)
                totalSalary += float(sal)

        outfile.write('"Total","","' + str(totalSalary) + '","' + str(totalPred) + '","' + str(totalActual) + '"\n')





