import csv

positions =  dict()
team = []
lineup = [['QB',1],['RB', 2], ['WR',3],[ 'TE',1], ['K',1], ['D',1]]
budget = 60000
minsalary = 4500
effectivebudget = budget - 8*minsalary

SALARY = 6
RATING = 4


with open('FanDuel-NFL-2016-10-23-16656-players-list.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    reader.next()
    for row in reader:
        pos = row[1]
        if pos in positions:
            rat = float(row[RATING])
            if rat in positions[pos]:
                positions[pos][rat].append(row[:7])
            else:
                positions[pos][rat] = [row[:7]]
        else:
            ratings = dict()
            ratings[float(row[RATING])] = [row[:7]]
            positions[pos] = ratings
        #print positions[pos]



for pos in lineup:
    num = 0
    ratings = positions[pos[0]]
    for rating in sorted(ratings.keys(), reverse=True):
        for i in range(len(ratings[rating])):
            cost = int(ratings[rating][i][SALARY])
            if cost < effectivebudget:
                budget -= cost
                effectivebudget -= cost - minsalary
                team.append(ratings[rating][i])
                num += 1
                if(num == pos[1]):
                    break
        if(num == pos[1]):
            break

print 'Budget remaining: ' + str(budget)
print 'Team: '
for player in team:
    print player


