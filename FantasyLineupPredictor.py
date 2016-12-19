import Data
import Predictors
import argparse
import Evaluations
from Evaluations.EvaluateLineups import evaluateMDP

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--week', type=int, action='store',help='Week number for predictions', required=True)
    parser.add_argument('--evalML', type=str, action='store', help='Evaluate Player models? True/False', default='False')
    parser.add_argument('--evalMDP', type=str, action='store', help='Evaluate Lineup MDP? True/False', default='False')
    parser.add_argument('--all', type=str, action='store', help='Run preds on all weeks up to --week', default='False')
    parser.add_argument('--greed', type=str, action='store', help='Use greedy algo or actual probabilities?', default='False')
    parser.add_argument('--trainML', type=str, action='store', help='Retrain player models?', default='False')
    args = parser.parse_args()

    fantasyModels = Predictors.FantasyPlayerPredictions.FantasyPredictionModel(args.week)
    if args.evalML == 'True':
        fantasyModels.evaluate()
    else:
        if args.all == 'True':
            if args.trainML == 'True':    
                for week in xrange(2,args.week + 1):
                    print('----------WEEK %d----------') %(week)                
                    fantasyModels.week = week
                    fantasyModels.train()
                    fantasyModels.predict()
            if args.evalMDP == 'True':
                for week in xrange(10, args.week + 1):
                    print('----------WEEK %d----------') %(week)
                    print('--------------Solving Greedy-------------------')
                    mdp = Predictors.FantasyMDP.FantasyMDP(week, True, True)
                    mdp.solve()
                    print('--------------Solving MDP-------------------')
                    mdp = Predictors.FantasyMDP.FantasyMDP(week, False, True)
                    mdp.solve()
                evaluateMDP(2,args.week, True)
                evaluateMDP(2,args.week, False)
        else:
            if args.trainML == 'True':
                fantasyModels.train()  
                fantasyModels.predict()
            mdp = Predictors.FantasyMDP.FantasyMDP(args.week, args.greed=='True', args.evalMDP == 'True')
            mdp.solve()
