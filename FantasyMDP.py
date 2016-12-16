import csv, argparse
from collections import defaultdict

from Data import FantasyProbabilityDB, FantasyDB
from Utility import util

MAX_SALARY = 60000

POSITIONS = ['QB', 'WR', 'RB', 'TE', 'PK', 'Def']
POS_INDECES = {'QB':0, 'WR':1, 'RB':2, 'TE':3, 'PK':4, 'Def':5}

MAX_POSITIONS = {'QB':1, 'WR':3, 'RB':2, 'TE':1, 'PK':1, 'Def':1}
START_LINEUP = [(), (), (), (), (), ()]


EXPECTED_VALUES = {'0_5':2.5, '5_10':7.5, '10_15':12.5, '15_20':17.5, '20_25':22.5, '25_30':27.5, '30+':35}
MAX_ONE_TEAM = 4
OUTPATH = 'Lineups/MDP/Week'
OUTFIELDNAMES = ['Year','Week','Name','Position','Salary','Predicted points']

LINEUP_FILE = 'Lineups/MDP/Week_'
OUTPUT_FILE = 'Evaluations/Evals_greed_2_13.csv'

class FantasyMDP(util.MDP):
    def __init__(self, week, greed_flag, algo):
        self.db = FantasyProbabilityDB.LineupProbDB(week, algo)
        self.algo = algo
        self.week = week
        self.greed = greed_flag
        self.start_state = (False, 0.0, tuple(START_LINEUP), tuple([0 for i in xrange(len(self.db.teams))]), 0.0)

    # Return the start state.
    # Look at this function to learn about the state representation.
    # The state is : ( [Is Final State?], [Salary],
    # [QB:[], WR:[], RB:[], TE:[], PK:[], Def:[]], 
    # [Players taken from each team],
    # [Total Production])
    def startState(self):
        return self.start_state 

    # Return set of actions possible from |state|.
    # You do not need to modify this function.
    # All logic for dealing with end states should be done in succAndProbReward
    def actions(self, state):
        final = state[0]
        current_salary = state[1]
        current_lineup = state[2]
        current_teams = state[3]

        if final and current_salary == 0:
            return ['Quit']
        
        for pos in POSITIONS:
            if len(current_lineup[POS_INDECES[pos]]) < MAX_POSITIONS[pos]:
                full_actions = self.db.getPosData(pos)
                current_players = current_lineup[POS_INDECES[pos]]
                return [k for k in full_actions if k not in current_players]
        return ['End']

    def generateSuccessors(self, current_lineup):
        list_lineup = []
        for position_group in current_lineup:
            for player in position_group:
                list_lineup.append(player)
        if self.greed:
            return []
        else:
            partial_sum_probs = {0:1}

        for player in list_lineup:
            player_data, pos = self.db.getPlayerData(player)
            team, expected_pts, salary, prob_0_5, prob_5_10, prob_10_15, prob_15_20, prob_20_25, prob_25_30, prob_30 = player_data
            
            next_partial_sum_probs = defaultdict(float)
            for prod,prob in partial_sum_probs.iteritems():
                next_partial_sum_probs[prod + EXPECTED_VALUES['0_5']] += prob * prob_0_5
                next_partial_sum_probs[prod + EXPECTED_VALUES['5_10']] += prob * prob_5_10
                next_partial_sum_probs[prod + EXPECTED_VALUES['10_15']] += prob * prob_10_15
                next_partial_sum_probs[prod + EXPECTED_VALUES['15_20']] += prob * prob_15_20
                next_partial_sum_probs[prod + EXPECTED_VALUES['20_25']] += prob * prob_20_25
                next_partial_sum_probs[prod + EXPECTED_VALUES['25_30']] += prob * prob_25_30
                next_partial_sum_probs[prod + EXPECTED_VALUES['30+']] += prob * prob_30
            partial_sum_probs = next_partial_sum_probs


        results = [(prob,prod) for prod, prob in partial_sum_probs.iteritems()]
        return results


    def addPlayerToLineUp(self, current_lineup, action, pos):
        current_lineup = list(current_lineup)
        current_pos_group = list(current_lineup[POS_INDECES[pos]])
        current_pos_group.append(action)
        current_pos_group.sort()
        current_lineup[POS_INDECES[pos]] = tuple(current_pos_group)
        current_lineup = tuple(current_lineup)
        return current_lineup
    
    def setTeamCount(self, current_teams, team):
        team_index = self.db.teams.index(team)
        #Tuple conversion
        current_teams = list(current_teams)
        current_teams[team_index] += 1
        current_teams = tuple(current_teams)
        return current_teams

    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.  Indicate a terminal state (after quitting or
    # busting) by setting the deck to None. 
    # When the probability is 0 for a particular transition, don't include that 
    # in the list returned by succAndProbReward.
    def succAndProbReward(self, state, action):
        final, current_salary, current_lineup, current_teams, current_prod = state
        
        if action == 'Quit':
            return [(state, 1.0, 0.0)]

        if action == 'End':
            return [((True, MAX_SALARY, tuple(START_LINEUP), tuple([0 for i in xrange(len(self.db.teams))]), prod), prob, prod) \
                        for prob, prod in self.generateSuccessors(current_lineup)]

        team, salary, pos = self.db.getPlayerTeamSalaryPos(action)
        
        #Update salary and lineup with new player
        new_salary = salary + current_salary

        current_lineup = self.addPlayerToLineUp(current_lineup, action, pos)

        current_teams = self.setTeamCount(current_teams, team)
        team_index = self.db.teams.index(team)

        #If over salary cap or over team limit-- Lose game
        if new_salary > MAX_SALARY or current_teams[team_index] == MAX_ONE_TEAM:
            return [ ( (True, 0, tuple(START_LINEUP), tuple([0 for i in xrange(len(self.db.teams))]), 0.0) , 1 , -10000 )]

        return [ ( (False, new_salary, current_lineup, current_teams, 0.0), 1 , 0 )]
        

    def discount(self):
        return 1

    def rebuildRoster(self, policy, values):
        roster = {'QB':[], 'RB': [], 'WR': [], 'TE': [], 'PK':[], 'Def':[]}
        roster_points = 0.0
        state = self.start_state
        for i in xrange(9): #9 positions to assign
            final, current_salary, current_lineup, current_teams, current_prod = state
            action = policy[state]
            team, salary, pos = self.db.getPlayerTeamSalaryPos(action)
            new_salary = salary + current_salary
            current_lineup = self.addPlayerToLineUp(current_lineup, action, pos)
            current_teams = self.setTeamCount(current_teams, team)
            player_data, extra_pos = self.db.getPlayerData(action)
            team, expected_pts, salary, prob_0_5, prob_5_10, prob_10_15, prob_15_20, prob_20_25, prob_25_30, prob_30 = player_data
            roster[pos].append((action, team, salary, expected_pts))
            state = (False, new_salary, current_lineup, current_teams, 0.0)
            roster_points += expected_pts
        roster_cost = 0
        if self.greed:
            path_to_write = OUTPATH+'_'+self.algo+'_greed_'+str(self.week)+'.csv'
        else:
            path_to_write = OUTPATH+'_'+self.algo+'_'+str(self.week)+'.csv'
        with open(path_to_write,'wb') as outfile:
            writer = csv.DictWriter(outfile , fieldnames=OUTFIELDNAMES)
            writer.writeheader()
            for pos, player_group in roster.iteritems():
                print(pos)
                for i in xrange(len(player_group)):
                    player = player_group[i]
                    print(str(i+1) + '.' + player[0] + '-' + player[1] + '-' + str(int(player[2])) + '-' + str(player[3]))
                    roster_cost += player[2]
                    row_entry = {'Year':2016, 'Week':self.week, 'Name':player[0], 'Position':pos, 'Salary':player[2], 'Predicted points':player[3]}
                    writer.writerow(row_entry)
        print('Total Roster Cost %d') %(roster_cost)
        print('Total Roster Production %f') %(roster_points)
                
    
    def evaluate(self):
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
            outfile.write('"Week","Predicted Points","Actual Points"\n')
            for week in range(1,self.week):
                with open(LINEUP_FILE + str(week) + '.csv', 'r') as infile:
                    infile.next()
                    reader = csv.reader(infile, delimiter=',', quotechar='"')
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

    def solve(self):
        valIter = util.ValueIteration()
        valIter.solve(self)
        vi_policy = valIter.pi
        values = valIter.V
        self.rebuildRoster(vi_policy, values)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--week', type=int, action='store',help='Week number for predictions', required=True)
    parser.add_argument('--greed', type=str, action='store', help='Use greedy algo or actual probabilities?', default='False')
    parser.add_argument('--all', type=str, action='store', help='Run preds on all weeks up to --week', default='False')
    parser.add_argument('--algo', type=str, action='store', help='Algorithm that generated predictions -- RF/LReg/GDBT', default='RF')
    args = parser.parse_args()
    if args.all == 'True':
        for week in xrange(2,args.week+1):
            print('----------WEEK %d----------') %(week)
            mdp = FantasyMDP(week, args.greed=='True', args.algo)
            mdp.solve()
    else:
        mdp = FantasyMDP(args.week, args.greed=='True', args.algo)
        mdp.solve()