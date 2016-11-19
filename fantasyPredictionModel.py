from FantasyDB import FantasyDB
import csv
import argparse
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.feature_selection import SelectKBest, chi2


POSITIONS = ['RB', 'WR', 'TE', 'QB', 'PK', 'Def']

RB_PARAMS = {'n_estimators':100, 'max_depth':5, 'max_features':'auto', 'min_samples_split':2}
WR_PARAMS = {'n_estimators':50, 'max_depth':5, 'max_features':'auto', 'min_samples_split':2}
TE_PARAMS = {'n_estimators':100, 'max_depth':5, 'max_features':'auto', 'min_samples_split':2}
QB_PARAMS = {'n_estimators':100, 'max_depth':5, 'max_features':'auto', 'min_samples_split':2}
PK_PARAMS = {'n_estimators':50, 'max_depth':5, 'max_features':'auto', 'min_samples_split':2}
DEF_PARAMS = {'n_estimators':50, 'max_depth':5, 'max_features':'auto', 'min_samples_split':2}

POS_PARAMS = {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}

CURRENT_YEAR = '2016'

PREDICTIONS_DIR = 'Predictions/Week'
OUTPUT_FIELDS_REGRESSION = ['name', 'pos', 'team', 'prediction', 'salary']
OUTPUT_FIELDS_CLASSIFICATION = ['name', 'pos', 'team', 'expectation','prob_0_5', 'prob_5_10', 'prob_10_15', 'prob_15_20' ,'prob_20+', 'salary']


class FantasyPredictionModel:

    def __init__(self, gameLead, target_week, classification):
        self.db = FantasyDB()      
        self.GAME_LEAD = gameLead 
        self.WEEK = target_week
        self.classification = classification
        self.models = {}
    

    def getLearner(self, pos):
        if self.classification:
            return RandomForestClassifier(n_estimators = POS_PARAMS[pos]['n_estimators'],
                                        max_depth = POS_PARAMS[pos]['max_depth'],
                                        max_features= POS_PARAMS[pos]['max_features'], 
                                        min_samples_split=POS_PARAMS[pos]['min_samples_split'])
        else:
            return RandomForestRegressor(n_estimators = POS_PARAMS[pos]['n_estimators'],
                                        max_depth = POS_PARAMS[pos]['max_depth'],
                                        max_features= POS_PARAMS[pos]['max_features'], 
                                        min_samples_split=POS_PARAMS[pos]['min_samples_split'])

    def getTrainData(self, pos):
        raw_x,raw_y = self.db.getTrainingExamples(pos,self.GAME_LEAD, self.classification)
        data_X = np.array(raw_x, dtype='float64')
        data_Y = np.array(raw_y, dtype='float64')
        return data_X, data_Y

    def train(self):
        for pos in POSITIONS:
            print("-----------------------Training %s Model---------------------") %(pos)
            data_X, data_Y = self.getTrainData(pos)
            learner = self.getLearner(pos)
            learner.fit(data_X, data_Y)
            self.models[pos] = learner

    def evaluate(self):
        for pos in POSITIONS:
            print("-----------------------Training %s Model---------------------") %(pos)
            data_X, data_Y = self.getTrainData(pos)
            learner = self.getLearner(pos)
            data_train, data_test, target_train, target_test = train_test_split(data_X, data_Y, test_size=0.20, random_state=42)
           
            learner.fit(data_train, target_train)
            
            preds = learner.predict(data_test)

            if self.classification:
                self.evaluateClassificationResults(target_test, preds, True)
            else:
                self.evaluateRegressionResults(target_test, preds, True)

    def evaluateClassificationResults(self, target_true,target_predicted, verbose_flag):
        print("-----------------------Evaluation---------------------------")
        print(classification_report(target_true,target_predicted))
        print("The accuracy score is {:.2%}".format(accuracy_score(target_true,target_predicted)))
        if verbose_flag:
            cm = confusion_matrix(target_true,target_predicted)
            np.set_printoptions(precision=2)
            print('Confusion matrix, without normalization')
            print(cm)
            cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            print('Normalized confusion matrix')
            print(cm_normalized)
            print("\n\n")
        return accuracy_score(target_true, target_predicted)
    
    def evaluateRegressionResults(self, target_true, target_predicted, verbose_flag):
        print("-----------------------Evaluation---------------------------")

    def predict(self):
        for pos in POSITIONS:
            data, names, salaries, teams = self.db.getPredictionPoints(pos, self.GAME_LEAD, CURRENT_YEAR, self.WEEK)
            if pos in self.models:
                model = self.models[pos]
                if self.classification:
                    preds = model.predict_proba(data)
                    results = [{'name':names[i], 'pos':pos, 'team':teams[i],
                                 'prob_0_5':preds[i][0], 'prob_5_10':preds[i][1],
                                 'prob_10_15':preds[i][2], 'prob_15_20':preds[i][3],
                                 'prob_20+':preds[i][4], 
                                 'expectation': self.db.computeExpectation(preds[i])} \
                                 for i in xrange(len(preds))]
                    
                    results = sorted(results, key=lambda x: x['expectation'], reverse=True)
                else:
                    preds = model.predict(data)
                    results = [{'name':names[i], 'pos':pos, 'team':teams[i], 'prediction':preds[i], 
                            'salary':salaries[i]} \
                            for i in xrange(len(preds))]
                    results = sorted(results, key=lambda x: x['prediction'], reverse=True)
                if self.classification:
                    filepath = PREDICTIONS_DIR + str(self.WEEK) +"/classification_" + pos + "_preds.csv"
                else:
                    filepath = PREDICTIONS_DIR + str(self.WEEK) +"/regression_" + pos + "_preds.csv" 
                with open(filepath,'wb') as outfile:    
                    outfile.truncate()
                    if self.classification:    
                        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS_CLASSIFICATION)
                    else:
                        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS_REGRESSION)
                    writer.writeheader()
                    for result in results:
                        writer.writerow(result)
            else:
                print("Models must be trained prior to running predictions.")
                return
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--classification", type=str, action="store", help="Classification flag? True/False", required=True)
    parser.add_argument("--gamelead", type=int, action="store",help="Number of games before current week to load as training sample", default=3)
    parser.add_argument("--week", type=int, action="store",help="Week number for predictions", required=True)
    parser.add_argument("--eval", type=str, action="store", help="Evaluate models? True/False")
    args = parser.parse_args()

    fantasyModels = FantasyPredictionModel(args.gamelead, args.week, args.classification == 'True')
    if args.eval == "True":
        fantasyModels.evaluate()
    else:
        fantasyModels.train()
        fantasyModels.predict()