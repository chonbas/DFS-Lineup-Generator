from FantasyProbabilityDB import LineupProbDB
import util
from collections import defaultdict


POS_DIR = '../Predictions/'
MAX_SALARY = 60000

POSITIONS = ['QB', 'WR', 'RB', 'TE', 'PK', 'Def']
POS_INDECES = {'QB':0, 'WR':1, 'RB':2, 'TE':3, 'PK':4, 'Def':5}

MAX_POSITIONS = {'QB':1, 'WR':3, 'RB':2, 'TE':1, 'PK':1, 'Def':1}
START_LINEUP = [set(), set(), set(), set(), set(), set()]
EXPECTED_VALUES = {'0_5':2.5, '5_10':7.5, '10_15':12.5, '15_20':17.5, '20_25':22.5, '25+':27.5}
MAX_ONE_TEAM = 4

class FantasyMDP(util.MDP):
    def __init__(self):
        self.db = LineupProbDB()
        

    # Return the start state.
    # Look at this function to learn about the state representation.
    # The state is : ( [Current Salary Cost]  , 
    # {QB:[], WR:[], RB:[], TE:[], PK:[], Def:[]}, 
    # {[Key = Team] : [Value:Count of Players with this Team]})
    def startState(self):
        return (0.0, tuple(START_LINEUP), tuple([0 for i in xrange(len(self.db.teams))]) )  # total, next card (if any), multiplicity for each card

    # Return set of actions possible from |state|.
    # You do not need to modify this function.
    # All logic for dealing with end states should be done in succAndProbReward
    def actions(self, state):
        current_lineup = state[2]
        current_teams = state[3]
        actions = ['End']
        #Check for lineup over salarycap / team limit
        if current_teams is None or current_lineup is None:
            return []
        for pos in POSITIONS:
            if len(current_lineup[POS_INDECES[pos]]) < MAX_POSITIONS[pos]:
                full_actions = self.db.getPosData(pos)
                current_players = set(current_lineup[POS_INDECES[pos]])
                actions = [k for k in full_actions if k not in current_players]
                break
        return actions
    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.  Indicate a terminal state (after quitting or
    # busting) by setting the deck to None. 
    # When the probability is 0 for a particular transition, don't include that 
    # in the list returned by succAndProbReward.
    def succAndProbReward(self, state, action):
        current_salary, current_production, current_lineup, current_teams = state
        
        if action == 'End':
            return [( (current_salary, current_production, current_lineup, None) , 1, current_production )]

        player_data, pos = self.db.getPlayerData(action)
        
        team, expected_pts, salary, prob_0_5, prob_5_10, prob_10_15, prob_15_20, prob_20 = player_data
        
        #Update salary and lineup with new player
        new_salary = salary + current_salary

        #Have to handle tuple conversions no account of hashable requrieemnt
        current_lineup = list(current_lineup)
        # current_pos_players = list(current_lineup[POS_INDECES[pos]])
        # current_pos_players.append(action)
        # current_lineup[POS_INDECES[pos]] = tuple(current_pos_players)
        current_lineup[POS_INDECES[pos]].add(action)
        current_lineup = tuple(current_lineup)

        team_index = self.db.teams.index(team)
        #If over salary cap or over team limit-- Lose game
        if new_salary > MAX_SALARY or current_teams[team_index] == MAX_ONE_TEAM:
            return [ ( (new_salary, 0.0,  None, ()) , 1 , 0 )]
        #Tuple conversion
        current_teams = list(current_teams)
        current_teams[team_index] += 1
        current_teams = tuple(current_teams)
        successors = []

        successors.append( ((new_salary, current_production + EXPECTED_VALUES['0_5'], current_lineup, current_teams), prob_0_5, 0) )
        successors.append( ((new_salary, current_production + EXPECTED_VALUES['5_10'], current_lineup, current_teams), prob_5_10, 0) )
        successors.append( ((new_salary, current_production + EXPECTED_VALUES['10_15'], current_lineup, current_teams), prob_10_15, 0) )
        successors.append( ((new_salary, current_production + EXPECTED_VALUES['15_20'], current_lineup, current_teams), prob_15_20, 0) )
        successors.append( ((new_salary, current_production + EXPECTED_VALUES['20+'], current_lineup, current_teams), prob_20, 0) )

        return successors

    def discount(self):
        return 1

if __name__ == '__main__':
    originalMDP = FantasyMDP()
    valIter = util.ValueIteration()
    valIter.solve(originalMDP)
    vi_policy = valIter.pi
    print vi_policy