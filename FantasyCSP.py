
import csv
from Utility.FantasyCSPConstructor import FantasyCSPConstructor
from Utility.BacktrackingSearch import BacktrackingSearch
from Data.LineupDB import LineupDB


FILENAME = 'Lineups/CSP_classification_lineup.csv'
MODEL = 'classification' #regression, classification, or oracle
ALGO = 'RF' #'RF' if regression/classification, '' if oracle
YEAR = 2016
START_WEEK = 2
END_WEEK = 14
MAX_PLAYERS = 6


#Returns list of tuples of (pos, player name) as well as total pts & salary
def get_player_stats(players, week, year=YEAR, toPrint=True):
    db = LineupDB(week, year, MODEL, ALGO, MAX_PLAYERS)

    totalPts = 0
    totalSalary = 0
    playerList = []
    for (pos, j) in players.keys():
        (name, salary) = players[(pos,j)]
        if toPrint:
            print name, "\t", pos, "\t", db.data[pos][name]
        pts = db.data[pos][name][db.pts]
        sal = db.data[pos][name][db.salary]
        totalPts += pts
        totalSalary += sal
        playerList.append('"' + name + '","' + pos + '","' + str(sal) + '","' + str(pts) + '"')
    if toPrint:
        print 'total points expected: ', totalPts
        print 'total salary used: ', totalSalary
    return playerList


with open(FILENAME, 'wb') as outfile:
    outfile.truncate()
    outfile.write('"Year","Week","Name","Position","Salary","Predicted points"\n')
    for week in range(START_WEEK, END_WEEK + 1):
        cspConstructor = FantasyCSPConstructor(week, YEAR, MODEL, ALGO, MAX_PLAYERS, verbose=False)
        csp = cspConstructor.get_csp()
        alg = BacktrackingSearch()
        print '---------------------- Ready to solve week ' + str(week) + '--------------------------\n'
        players = alg.solve(csp, mcv=True, ac3=True)
        print 'Solved!\n'


        playerList = get_player_stats(players, week, YEAR)
        for line in playerList:
            outfile.write('"' + str(YEAR) + '","' + str(week) + '",' + line + '\n')




