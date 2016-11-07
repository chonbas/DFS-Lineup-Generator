from createTrainDB import FantasyDataDictionary

thing = FantasyDataDictionary()

x,y = thing.getTrainingExamples('Def',2)

for i in xrange(len(x)):
    print len(x[i])
    # if len(x[i]) != 174:
    #     print 'NOPENOPE'
    # print y[i]
