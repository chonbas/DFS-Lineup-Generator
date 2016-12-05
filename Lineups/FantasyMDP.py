from FantasyProbabilityDB import LineupProbDB
import util
from collections import defaultdict


POS_DIR = '../Predictions/'
MAX_SALARY = 60000

POSITIONS = ['QB', 'WR', 'RB', 'TE', 'PK', 'Def']
POS_INDECES = {'QB':0, 'WR':1, 'RB':2, 'TE':3, 'PK':4, 'Def':5}

MAX_POSITIONS = {'QB':1, 'WR':3, 'RB':2, 'TE':1, 'PK':1, 'Def':1}
START_LINEUP = [(), (), (), (), (), ()]

EXPECTED_VALUES = {'0_5':2.5, '5_10':7.5, '10_15':12.5, '15_20':17.5, '20_25':22.5, '25+':27.5}
MAX_ONE_TEAM = 4

class FantasyMDP(util.MDP):
    def __init__(self):
        self.db = LineupProbDB()
        # self.start_state = (False, 0.0, tuple(START_LINEUP), tuple([0 for i in xrange(len(self.db.teams))]), 0.0)
        self.start_state = (False, 0.0, tuple(START_LINEUP), tuple([0 for i in xrange(len(self.db.teams))]))

    # Return the start state.
    # Look at this function to learn about the state representation.
    # The state is : ( [Current Salary Cost]  , 
    # [QB:[], WR:[], RB:[], TE:[], PK:[], Def:[]], 
    # {[Key = Team] : [Value:Count of Players with this Team]})
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

        if current_salary > MAX_SALARY or (final and current_salary == 0):
            return ['Quit']
        
        if final:
            return ['End']
        
        actions = []
        for pos in POSITIONS:
            if len(current_lineup[POS_INDECES[pos]]) < MAX_POSITIONS[pos]:
                full_actions = self.db.getPosData(pos)
                current_players = current_lineup[POS_INDECES[pos]]
                actions = [k for k in full_actions if k not in current_players]
                break
        return actions

    def generateSuccessors(self, current_lineup):
        def recurse(lineup, current_prob, current_prod):
            if len(lineup) == 0:
                return [(current_prob, current_prod)]
            
            player = lineup[-1]

            player_data = self.db.getPlayerData(player)

            team, expected_pts, salary, prob_0_5, prob_5_10, prob_10_15, prob_15_20, prob_20_25, prob_25 = player_data

            results = []
            # prob_0_10 = prob_0_5 + prob_5_10
            # prob_10_20 = prob_10_15 + prob_15_20
            # prob_20_30 = prob_20_25 + prob_25
            # expected_0_10 = prob_0_5 * EXPECTED_VALUES['0_5'] + prob_5_10 * EXPECTED_VALUES['5_10']
            # expected_10_20 = prob_10_15 * EXPECTED_VALUES['10_15'] + prob_15_20 * EXPECTED_VALUES['15_20']
            # expected_20_30 = prob_20_25 * EXPECTED_VALUES['20_25'] + prob_25 * EXPECTED_VALUES['25+']

            # results += recurse(lineup[:-1], current_prob * prob_0_10, current_prod + expected_0_10)
            # results += recurse(lineup[:-1], current_prob * prob_10_20, current_prod + expected_10_20)
            # results += recurse(lineup[:-1], current_prob * prob_20_30, current_prod + expected_20_30)

            results += recurse(lineup[:-1], current_prob * prob_0_5, current_prod + EXPECTED_VALUES['0_5'])
            results += recurse(lineup[:-1], current_prob * prob_5_10, current_prod + EXPECTED_VALUES['5_10'])
            results += recurse(lineup[:-1], current_prob * prob_10_15, current_prod + EXPECTED_VALUES['10_15'])
            results += recurse(lineup[:-1], current_prob * prob_15_20, current_prod + EXPECTED_VALUES['15_20'])
            results += recurse(lineup[:-1], current_prob * prob_20_25, current_prod + EXPECTED_VALUES['20_25'])
            results += recurse(lineup[:-1], current_prob * prob_25, current_prod + EXPECTED_VALUES['25+'])
            return results
            
        list_lineup = []
        for position_group in current_lineup:
            for player in position_group:
                list_lineup.append(player)
        
        results =  recurse(list_lineup, 1.0, 0.0)
        collapsed_prods_probs = defaultdict(float)
        for prob, prod in results:
            collapsed_prods_probs[prod] += prob
        
        results = [(v,k) for k,v in collapsed_prods_probs.iteritems()]
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
        # final, current_salary, current_lineup, current_teams, current_prod = state
        final, current_salary, current_lineup, current_teams = state
        
        if action == 'Quit':
            return [(state, 1.0, 0.0)]

        if action == 'End':
            return [((True, 0.0, tuple(START_LINEUP), tuple([0 for i in xrange(len(self.db.teams))])), prob, prod) \
                        for prob, prod in self.generateSuccessors(current_lineup)]

        team, salary, pos = self.db.getPlayerTeamSalaryPos(action)
        
        #Update salary and lineup with new player
        new_salary = salary + current_salary

        current_lineup = self.addPlayerToLineUp(current_lineup, action, pos)

        current_teams = self.setTeamCount(current_teams, team)
        team_index = self.db.teams.index(team)

        #If over salary cap or over team limit-- Lose game
        if new_salary > MAX_SALARY or current_teams[team_index] == MAX_ONE_TEAM:
            return [ ( (True, 0.0, tuple(START_LINEUP), tuple([0 for i in xrange(len(self.db.teams))])) , 1 , 0 )]

        return [ ( (False, new_salary, current_lineup, current_teams), 1 , 0 )]
        

    def discount(self):
        return 1

    def rebuildRoster(self, policy):
        roster = {'QB':[], 'RB': [], 'WR': [], 'TE': [], 'PK':[], 'Def':[]}
        state = self.start_state
        for i in xrange(9): #9 positions to assign
            final, current_salary, current_lineup, current_teams = state
            action = policy[old_state]
            team, salary, pos = self.db.getPlayerTeamSalaryPos(action)
            new_salary = salary + current_salary
            current_lineup = self.addPlayerToLineUp(current_lineup, action, pos)
            current_teams = self.setTeamCount(current_teams, team)
            roster[pos].append(action)
            state = (False, new_salary, current_lineup, current_teams)
        for pos, player_group in roster.iteritems:
            print(pos)
            for player in player_group:
                print(player)


if __name__ == '__main__':
    mdp = FantasyMDP()
    valIter = util.ValueIteration()
    valIter.solve(mdp)
    vi_policy = valIter.pi
    mdp.rebuildRoster(vi_policy)