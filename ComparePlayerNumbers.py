import csv
# from FantasyMDP import FantasyMDP
# from FantasyCSPConstructor import FantasyCSPConstructor
# from util import ValueIteration
# from BacktrackingSearch import BacktrackingSearch
from Data.FantasyDB import FantasyDB

# #Note: really slow. Would not recommend.
# mdp = FantasyMDP()
# alg = ValueIteration()
# alg.solve(mdp, .001)

NUM_PLAYERS = ['3','4','5','6','7']
LINEUP_FILE = 'Lineups/CSP_week12/regression_'
OUTPUT_FILE = 'Evaluations/CSP_experiment/vary_num_players'



db = FantasyDB()
def getActualPts(player, year, week):
    pos_data = db.getData(pos)
    try:
        pts = pos_data[player][year][week]['fd_pts']
        return pts
    except TypeError:
        print 'Can\'t find player ' + player + ' in week ' + week
        return 0

with open(OUTPUT_FILE + '.csv', 'wb') as outfile:
    outfile.truncate()
    outfile.write('"Num players","Predicted Points","Actual Points"\n')
    for num in NUM_PLAYERS:
        with open(LINEUP_FILE + num + 'players.csv', 'r') as infile:
            infile.next()
            reader = csv.reader(infile, delimiter=',', quotechar='"')
            # prevWeek = None
            totalPred = 0
            totalActual = 0
            for line in reader:
                year, week, name, pos, sal, predPts = line
                actualPts = getActualPts(name, year, week)
                # if prevWeek == None: prevWeek = week

                # if week != prevWeek:
                #     outfile.write('"' + num + '","' + str(totalPred) + '","' + str(totalActual) + '"\n')
                #     prevWeek = week
                #     totalPred = 0
                #     totalActual = 0
                totalPred += float(predPts)
                totalActual += float(actualPts)
            outfile.write('"' + num + '","' + str(totalPred) + '","' + str(totalActual) + '"\n')





