from FantasyMDP import FantasyMDP
from FantasyCSPConstructor import FantasyCSPConstructor
from util import ValueIteration
from BacktrackingSearch import BacktrackingSearch


# #Note: really slow. Would not recommend.
# mdp = FantasyMDP()
# alg = ValueIteration()
# alg.solve(mdp, .001)


cspConstructor = FantasyCSPConstructor(week=11,year=2016)
csp = cspConstructor.get_csp()
alg = BacktrackingSearch()
print "---------------------- Ready to solve --------------------------\n"
players = alg.solve(csp, mcv=True, ac3=True)
print "Solved!\n"
cspConstructor.print_players(players)