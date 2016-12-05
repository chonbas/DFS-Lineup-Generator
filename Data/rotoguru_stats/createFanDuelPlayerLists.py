import csv

def convertPosition(pos):
    if pos == 'Def':
        return 'D'
    if pos == 'PK':
        return 'K'
    return pos.upper()

POSITIONS = ['RB', 'WR', 'TE','QB', 'PK', 'Def']
for week in [1,2,3,4,5,6,12]:
    with open('FanDuel-NFL-2016-Week-'+str(week)+'.csv','wb') as outfile:
        outfile.write('"Id","Position","First Name","Nickname","Last Name","FPPG","Played","Salary","Game","Team","Opponent","Injury Indicator","Injury Details","",""\n')
        for pos in POSITIONS:
            with open('roto_'+pos+'.csv') as posfile:
                posfile.next()
                rotoreader = csv.reader(posfile, delimiter=';', quotechar='"')
                for line rotoreader:
                    # '"Id","Position","First Name","Nickname","Last Name","FPPG","Played","Salary","Game","Team","Opponent","Injury Indicator","Injury Details","",""\n'
                    # 0      1   2   3   4    5    6  7      8           9
                    # week;year;GID;name;pos;team;h/a;oppt;fd points;fd salary
                    id = line[2]
                    pos = convertPosition(line[4])
                    first_name, last_name = line[3].split()
                    if line[6] == 'h':
                        game = 
                    outfile.write('"'+line[2]'","'+convertPosition(line[4])+'","'
    