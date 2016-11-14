from FantasyMDP import FantasyMDP
from util import ValueIteration


#Note: really slow. Would not recommend.
mdp = FantasyMDP()
alg = ValueIteration()
alg.solve(mdp, .001)