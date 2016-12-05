import csv

FIELDNAMES = ['Year', 'Week', 'Name', 'Pos', 'Team', 'Opp', 'H_A', 'Salary']
POSITIONS = ['RB', 'WR', 'TE','QB', 'PK', 'Def']

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

for week in xrange(1,13):
    with open('fanduel_lists/FanDuel-NFL-2016-Week-'+str(week)+'.csv','wb') as outfile:
        writer = csv.DictWriter(outfile , fieldnames=FIELDNAMES)
        writer.writeheader()
        for pos in POSITIONS:
            with open('rotoguru_stats/roto_'+pos+'.csv') as posfile:
                posfile.next()
                rotoreader = csv.reader(posfile, delimiter=';', quotechar='"')
                for line in rotoreader:
                    # '"Id","Position","First Name","Nickname","Last Name","FPPG","Played","Salary","Game","Team","Opponent","Injury Indicator","Injury Details","",""\n'
                    # 0      1   2   3   4    5    6  7      8           9
                    # week;year;GID;name;pos;team;h/a;oppt;fd points;fd salary
                    wk = line[0]
                    year = line[1]
                    if year == '2016':
                        if int(wk) == week:
                            pos = line[4].upper()
                            if pos == 'DEF':
                                pos = 'Def'
                            name = line[3]
                            team = fixTeamName(line[5].upper())
                            if line[6] == 'h':
                                home = 1
                            else:
                                home = 0
                            opp = fixTeamName(line[7].upper())
                            salary = line[9]
                            entry = {'Year':year, 'Week':wk, 'Name':name, 'Pos':pos, 'Team':team, 'Opp':opp, 'H_A':home, 'Salary':salary}
                            writer.writerow(entry)
                            
    