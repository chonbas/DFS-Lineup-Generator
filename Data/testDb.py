from createTrainDB import FantasyDataDictionary

thing = FantasyDataDictionary()

for k in thing.teams:
    print k
    print thing.teams[k]['2011']
    print '\n'