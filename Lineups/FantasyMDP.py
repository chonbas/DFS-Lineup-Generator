from LineupDB import LineupDB
import util

POSITIONS = ['RB', 'WR', 'TE', 'QB', 'PK', 'Def']
POS_DIR = '../Predictions/'
#LINEUP = [['QB',1],['RB', 2], ['WR',3],[ 'TE',1], ['PK',1], ['Def',1]]
LINEUP = [2, 3, 1, 1, 1, 1]
GAME_LEAD = 3 
MAX_SALARY = 60000
db = LineupDB()

YEAR = 2016
WEEK = 9




class FantasyMDP(util.MDP):
    def __init__(self):
        self.counter = 0
    #     """
    #     cardValues: array of card values for each card type
    #     multiplicity: number of each card type
    #     threshold: maximum total before going bust
    #     peekCost: how much it costs to peek at the next card
    #     """
    #     self.dataset = dataset
    #     self.lineup = lineup
    #     self.salary = salary

    # Return the start state.
    # Look at this function to learn about the state representation.
    # The first element of the tuple is the sum of the cards in the player's
    # hand.
    # The second element is the index (not the value) of the next card, if the player peeked in the
    # last action.  If they didn't peek, this will be None.
    # The final element is the current deck.
    def startState(self):
        lineup = []
        for i, num in enumerate(LINEUP):
            for j in range(num):
                lineup.append(POSITIONS[i])

        return (tuple(lineup), (), MAX_SALARY)  # total, next card (if any), multiplicity for each card

    # Return set of actions possible from |state|.
    # You do not need to modify this function.
    # All logic for dealing with end states should be done in succAndProbReward
    def actions(self, state):
        if len(state[0]) == 0:
            return []
        cur_pos = state[0][0];
        actions = []
        for player in db.data[cur_pos]:
            if db.data[cur_pos][player][db.salary] < state[2]:
                if (player, db.data[cur_pos][player]) not in state[1]:
                    actions.append(player)
        return actions

    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.  Indicate a terminal state (after quitting or
    # busting) by setting the deck to None. 
    # When the probability is 0 for a particular transition, don't include that 
    # in the list returned by succAndProbReward.
    def succAndProbReward(self, state, action):
        self.counter += 1
        if self.counter % 10000 == 0:
            print self.counter
            print len(state[0])
            print state[1]
        lineup_remaining = list(state[0])
        if len(lineup_remaining) == 0:
            return []

        pos = lineup_remaining.pop(0)

        entry = db.data[pos][action]

        lineup_set = list(state[1])
        lineup_set.append((action, entry))
        new_sal = state[2] - entry[db.salary]

        state = (tuple(lineup_remaining), tuple(lineup_set), new_sal)
        if(state[2] < 0):
            return [(state, 1, -1000)]
        return [(state, 1, entry[db.pts])]

        

        # END_YOUR_CODE
    def discount(self):
        return 1