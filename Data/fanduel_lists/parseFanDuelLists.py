import csv

FIELDNAMES = ['Year', 'Week', 'Name', 'Pos', 'Team', 'Opp', 'H_A', 'Salary']
POSITIONS = ['RB', 'WR', 'TE','QB', 'PK', 'Def']
FANDUEL_LIST_DIR = 'Source_FanDuel/FanDuel-NFL-2016-Week-'
OUTPATH = 'FanDuel-NFL-2016-Week-'

def fixTeamName(team):
    if team == 'STL':
        team = 'LARM'
    if team == 'LAR':
        team = 'LARM'
    if team == 'LA':
        team = 'LARM'
    if team == 'NWE':
        team = 'NE'
    if team == 'SFO':
        team = 'SF'
    if team == 'GNB':
        team = 'GB'
    if team == 'TAM':
        team = 'TB'
    if team == 'SDG':
        team = 'SD'
    if team == 'NOR':
        team = 'NO'
    if team == 'KAN':
        team = 'KC'
    return team

for week in xrange(13,16):
    with open(FANDUEL_LIST_DIR + str(week)+'.csv','rb') as infile:
        with open(OUTPATH + str(week) +'.csv', 'wb') as outfile:
            writer = csv.DictWriter(outfile , fieldnames=FIELDNAMES)
            writer.writeheader()
            infile.next()
            reader = csv.reader(infile, delimiter=',', quotechar='"')
            for line in reader:
                position = line[1].replace('"','')
                if position == 'D':
                    position = 'Def'
                if position == 'K':
                    position = 'PK'
                name = (line[2] + " " + line[4]).replace('"','')
                year = 2016
                team = fixTeamName(line[9].upper().replace('"',''))
                salary = int(line[7].replace('"',''))
                opp = fixTeamName(line[10].upper().replace('"',''))
                game = line[8].replace('"','')
                home_team = game[game.find('@')+1:]
                if home_team == team:
                    h_a = 1
                else:
                    h_a = 0
                entry = {'Year':2016, 'Week':week, 'Name':name, 'Pos':position, 'Team':team, 'Opp':opp, 'H_A':h_a, 'Salary':salary}
                writer.writerow(entry)
                            
    