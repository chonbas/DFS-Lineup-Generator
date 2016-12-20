import csv, argparse
from collections import defaultdict
from Data import FantasyProbabilityDB, FantasyDB
from Utility import util

CURRENT_YEAR = '2016'
#Number of players to look at
# MAX_DB_POS = {'QB':6, 'WR':8, 'RB':3, 'TE':6, 'PK':5, 'Def':6} #decent boom
MAX_DB_POS = {'QB':7, 'WR':9, 'RB':6, 'TE':3, 'PK':3, 'Def':3} # Pretty good boom
# MAX_DB_POS = {'QB':6, 'WR':9, 'RB':7, 'TE':4, 'PK':3, 'Def':3} # Pretty good boom
#Constraints
MAX_SALARY = 60000
MAX_ONE_TEAM = 4
LOSE_PENALTY = -10000
#Used to manage states
POSITIONS = ['QB', 'RB' , 'TE', 'PK', 'Def', 'WR']
POS_INDECES = {'QB':0, 'WR':1, 'RB':2, 'TE':3, 'PK':4, 'Def':5}
MAX_POSITIONS = {'QB':1, 'WR':3, 'RB':2, 'TE':1, 'PK':1, 'Def':1}
#Output path and fields
OUTPATH = 'Lineups/MDP/Week'
OUTFIELDNAMES = ['Year','Week','Name','Position','Salary','Predicted points']

LINEUP_FILE = 'Lineups/MDP/Week_'
OUTPUT_FILE = 'Evaluations/Evals_'

START_LINEUP = [(), (), (), (), (), ()]

class FantasyMDP(util.MDP):
    def __init__(self, week, eval_flag):
        self.actual_db = FantasyDB.FantasyDB()
        self.week = week
        self.eval = eval_flag
        self.db = FantasyProbabilityDB.LineupProbDB(week, MAX_DB_POS)
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
        # if self.greed:
        reward = 0.0
        for player in list_lineup:
            player_data, extra_pos = self.db.getPlayerData(player)
            team, expected_pts, salary, prob_0_5, prob_5_10, prob_10_15, prob_15_20, prob_20 = player_data
            reward += expected_pts
        return [(1.0,reward)]

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
    # busting) by setting the deck to Final state flag to True.
    def succAndProbReward(self, state, action):
        final, current_salary, current_lineup, current_teams, current_prod = state
        
        if action == 'Quit':
            return [(state, 1.0, 0)]

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
            return [ ( (True, 0, tuple(START_LINEUP), tuple([0 for i in xrange(len(self.db.teams))]), 0.0) , 1.0 , LOSE_PENALTY )]

        return [ ( (False, new_salary, current_lineup, current_teams, 0.0), 1.0 , 0.0 )]
        

    def discount(self):
        return 1
    
    def getActualPts(self, player, pos):
        pos_data = self.actual_db.getData(pos)
        try:
            pts = pos_data[player][CURRENT_YEAR][str(self.week)]['fd_pts']
            return pts
        except TypeError:
            print 'Can\'t find player ' + player + ' in week ' + str(self.week)
            return 0 
    
    #Gives predicted roster by following the learned policy
    def rebuildRoster(self, policy, values):
        roster = {'QB':[], 'RB': [], 'WR': [], 'TE': [], 'PK':[], 'Def':[]}
        roster_points = 0.0
        state = self.start_state
        if self.eval:
            actual_pts = 0.0
        for i in xrange(9): #9 positions to assign
            final, current_salary, current_lineup, current_teams, current_prod = state
            action = policy[state]
            team, salary, pos = self.db.getPlayerTeamSalaryPos(action)
            new_salary = salary + current_salary
            current_lineup = self.addPlayerToLineUp(current_lineup, action, pos)
            current_teams = self.setTeamCount(current_teams, team)
            player_data, extra_pos = self.db.getPlayerData(action)
            team, expected_pts, salary, prob_0_5, prob_5_10, prob_10_15, prob_15_20, prob_20 = player_data
            roster[pos].append((action, team, salary, expected_pts))
            state = (False, new_salary, current_lineup, current_teams, 0.0)
            roster_points += expected_pts
            if self.eval:
                actual_pts += float(self.getActualPts(action, pos))
        roster_cost = 0
        path_to_write = OUTPATH+'_'+str(self.week)+'.csv'
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
        print('Total Expected Roster Production %f') %(roster_points)
        if self.eval:
            print('Total Actual Roster Production %f') %(actual_pts)    
                
    

    def solve(self):
        valIter = util.ValueIteration()
        valIter.solve(self)
        vi_policy = valIter.pi
        values = valIter.V
        self.rebuildRoster(vi_policy, values)