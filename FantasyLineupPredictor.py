import Data
import Predictors
import argparse
import Evaluations
from Evaluations.EvaluateLineups import evaluateMDP

WEEK_RANGE_START = 8


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--week', type=int, action='store',help='Week number for predictions', required=True)
    parser.add_argument('--evalML', type=str, action='store', help='Evaluate Player models? True/False', default='False')
    parser.add_argument('--evalMDP', type=str, action='store', help='Evaluate Lineup MDP? True/False', default='False')
    parser.add_argument('--all', type=str, action='store', help='Run preds on all weeks up to --week', default='False')
    parser.add_argument('--trainML', type=str, action='store', help='Retrain player models?', default='False')
    args = parser.parse_args()

    fantasyModels = Predictors.FantasyPlayerPredictions.FantasyPredictionModel(args.week)
    if args.evalML == 'True':
        fantasyModels.evaluate()
    else:
        if args.all == 'True':
            if args.trainML == 'True':    
                for week in xrange(WEEK_RANGE_START,args.week + 1):
                    print('----------WEEK %d----------') %(week)                
                    fantasyModels.week = week
                    fantasyModels.train()
                    fantasyModels.predict()
            if args.evalMDP == 'True':
                for week in xrange(WEEK_RANGE_START, args.week + 1):
                    print('----------WEEK %d----------') %(week)
                    mdp = Predictors.FantasyMDP.FantasyMDP(week, True)
                    mdp.solve()
                evaluateMDP(WEEK_RANGE_START, args.week)
        else:
            if args.trainML == 'True':
                fantasyModels.train()  
                fantasyModels.predict()
            mdp = Predictors.FantasyMDP.FantasyMDP(args.week, args.evalMDP == 'True')
            mdp.solve()
