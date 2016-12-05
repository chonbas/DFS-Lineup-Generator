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

LINEUP_FILE = 'Lineups/CSPLineup.csv'
OUTPUT_FILE = '2016_CSPPredictionsVsActual.csv'



db = FantasyDB()
def getActualPts(player, year, week):
    pos_data = db.getData(pos)
    try:
        pts = pos_data[player][year][week]['fd_pts']
        return pts
    except TypeError:
        return 0

with open(LINEUP_FILE, 'r') as infile:
    infile.next()
    reader = csv.reader(infile, delimiter=',', quotechar='"')
    with open(OUTPUT_FILE, 'w') as outfile:
        outfile.truncate()
        outfile.write('"Week","Predicted Points","Actual Points"\n')

        prevWeek = None
        totalPred = 0
        totalActual = 0
        for line in reader:
            year, week, name, pos, sal, predPts = line
            actualPts = getActualPts(name, year, week)
            if prevWeek == None: prevWeek = week

            if week != prevWeek:
                outfile.write('"' + prevWeek + '","' + str(totalPred) + '","' + str(totalActual) + '"\n')
                prevWeek = week
                totalPred = 0
                totalActual = 0
            totalPred += float(predPts)
            totalActual += float(actualPts)
        outfile.write('"' + week + '","' + str(totalPred) + '","' + str(totalActual) + '"\n')





