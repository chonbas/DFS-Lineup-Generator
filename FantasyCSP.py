
import csv
from Utility.FantasyCSPConstructor import FantasyCSPConstructor
from Utility.BacktrackingSearch import BacktrackingSearch
from Data.LineupDB import LineupDB


FILENAME = 'Lineups/CSP_week12/regression_minSal590.csv'
MODEL = 'regression'
year = 2016



#Returns list of tuples of (pos, player name) as well as total pts & salary
def get_player_stats(players, week, year, toPrint=True):
    db = LineupDB(week=week, year=year, model=MODEL)

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
    for week in range(12, 13):
        cspConstructor = FantasyCSPConstructor(verbose=False, week=week, year=year, model=MODEL)
        csp = cspConstructor.get_csp()
        alg = BacktrackingSearch()
        print '---------------------- Ready to solve week ' + str(week) + '--------------------------\n'
        players = alg.solve(csp, mcv=True, ac3=True)
        print 'Solved!\n'


        playerList = get_player_stats(players, week, year)
        for line in playerList:
            outfile.write('"' + str(year) + '","' + str(week) + '",' + line + '\n')




