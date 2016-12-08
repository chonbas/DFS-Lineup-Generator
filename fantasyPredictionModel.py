from FantasyDB import FantasyDB
import csv
import argparse
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.feature_selection import f_classif, mutual_info_classif, SelectPercentile

POSITIONS = ['QB', 'WR', 'RB', 'TE', 'PK', 'Def']
# POSITIONS = ['TE']

#n_estimators = number of trees in random forest
#max_depth = max depth of individual trees in forest
#max_Features = max number of features to consider for each tree
#min_samples_split = number of sampels to see to branch a leaf in tree 
#feature_percent top % of features to extract using automated feature extraction
#gamelead = number of previous game data to use for feature vector
#class_weights = regularization terms to add extra penalty for errors in certain classes
#bootstrap = whether to build new trees using bootstrapped data from previous trees

QB_PARAMS = {'n_estimators':700, 'max_depth':None, 'max_features':'log2',
            'min_samples_split':2,'feature_percent':32, 'gamelead':13,
            'class_weights':{4:10,5:10},'bootstrap':True}

WR_PARAMS = {'n_estimators':1000, 'max_depth':10, 'max_features':'log2', 
            'min_samples_split':2,'feature_percent':35, 'gamelead':6,
            'class_weights':{4:1.6, 5:2}, 'bootstrap':True}

RB_PARAMS = {'n_estimators':500, 'max_depth':10, 'max_features':'log2',
            'min_samples_split':2,'feature_percent':31, 'gamelead':2,
            'class_weights':{4:2, 5:2}, 'bootstrap':False}

TE_PARAMS = {'n_estimators':500, 'max_depth':10, 'max_features':'log2',
            'min_samples_split':2,'feature_percent':30, 'gamelead':2,
            'class_weights':{4:2,5:3}, 'bootstrap':False}

PK_PARAMS = {'n_estimators':700, 'max_depth':7, 'max_features':'log2',
            'min_samples_split':2, 'feature_percent':35, 'gamelead':2,
            'class_weights':None, 'bootstrap':False}

DEF_PARAMS = {'n_estimators':500, 'max_depth':20, 'max_features':'log2',
            'min_samples_split':2,'feature_percent':75, 'gamelead':3,
            'class_weights':None, 'bootstrap':True}

POS_PARAMS = {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}

CURRENT_YEAR = '2016'

PREDICTIONS_DIR = 'Predictions/Week'
OUTPUT_FIELDS_REGRESSION = ['name', 'pos', 'team', 'prediction', 'salary']
OUTPUT_FIELDS_CLASSIFICATION = ['name', 'pos', 'team', 'expectation','salary','prob_0_5',
                                'prob_5_10', 'prob_10_15', 'prob_15_20' ,'prob_20_25','prob_25+']


class FantasyPredictionModel:

    def __init__(self, target_week, classification):
        self.db = FantasyDB()      
        self.week = target_week
        self.classification = classification
        self.models = {}
        self.selectors = {}
        self.accuracies = {}
    

    def getLearner(self, pos):
        if self.classification:
            return RandomForestClassifier(n_estimators = POS_PARAMS[pos]['n_estimators'],
                                        max_depth = POS_PARAMS[pos]['max_depth'],
                                        max_features= POS_PARAMS[pos]['max_features'], 
                                        min_samples_split=POS_PARAMS[pos]['min_samples_split'],
                                        random_state=42,
                                        class_weight=POS_PARAMS[pos]['class_weights'],
                                        bootstrap=POS_PARAMS[pos]['bootstrap'],
                                        n_jobs=-1)
        else:
            return RandomForestRegressor(n_estimators = POS_PARAMS[pos]['n_estimators'],
                                        max_depth = POS_PARAMS[pos]['max_depth'],
                                        max_features= POS_PARAMS[pos]['max_features'], 
                                        min_samples_split=POS_PARAMS[pos]['min_samples_split'],
                                        n_jobs=-1)

    def getFeatureSelector(self, pos):
        if pos == 'PK':
            return SelectPercentile(f_classif, percentile=POS_PARAMS[pos]['feature_percent'])
                
        return SelectPercentile(mutual_info_classif, percentile=POS_PARAMS[pos]['feature_percent'])

    def getTrainData(self, pos):
        raw_x,raw_y = self.db.getTrainingExamples(pos,POS_PARAMS[pos]['gamelead'], self.classification)
        data_X = np.array(raw_x, dtype='float64')
        data_Y = np.array(raw_y, dtype='float64')
        return data_X, data_Y

    def getPredData(self, pos):
        raw_data, names, salaries, teams = self.db.getPredictionPoints(pos, POS_PARAMS[pos]['gamelead'], CURRENT_YEAR, self.week)
        for i in xrange(len(raw_data)):
            raw_data[i] = np.array(raw_data[i], dtype='float64') 
        data = np.array(raw_data, dtype='float64')
        return data, names, salaries, teams  
        
    def train(self):
        for pos in POSITIONS:
            print("-----------------------Training %s Model---------------------") %(pos)

            data_X, data_Y = self.getTrainData(pos)
            if self.classification:
                selector = self.getFeatureSelector(pos)
                data_X = selector.fit_transform(data_X, data_Y)
                self.selectors[pos] = selector
            
            learner = self.getLearner(pos)
            learner.fit(data_X, data_Y)

            self.models[pos] = learner

    def evaluate(self):
        for pos in POSITIONS:
            print("-----------------------Training %s Model---------------------") %(pos)
            data_X, data_Y = self.getTrainData(pos)
            learner = self.getLearner(pos)
            data_train, data_test, target_train, target_test = train_test_split(data_X, data_Y, test_size=0.20, random_state=42)
            
            if self.classification:
                selector = self.getFeatureSelector(pos)
                data_train = selector.fit_transform(data_train, target_train)
                data_test = selector.transform(data_test)
            
            learner.fit(data_train, target_train)
            
            preds = learner.predict(data_test)

            if self.classification:
                self.accuracies[pos] = self.evaluateClassificationResults(target_test, preds, True)
            else:
                self.accuracies[pos] = self.evaluateRegressionResults(target_test, preds, True)
        for pos in POSITIONS:
            if self.classification:
                print("Accuracy for %s is : %f") %(pos, self.accuracies[pos])
            else:
                break
                # print("Errors for %s:") %(pos)
                # print(self.accuracies[pos])

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
        errors = {'mean_absolute_error':mean_absolute_error(target_true, target_predicted, multioutput='uniform_average'),
                  'mean_squared_error':mean_squared_error(target_true, target_predicted, multioutput='uniform_average'), 
                  'explained_variance_score':explained_variance_score(target_true, target_predicted, multioutput='uniform_average')}
        for key in errors:
            print("%s : %f") %(key, errors[key])
        return errors

    def predict(self):
        for pos in POSITIONS:
            data, names, salaries, teams = self.getPredData(pos)
            if pos in self.models:
                model = self.models[pos]
                if self.classification:
                    selector = self.selectors[pos]
                    data = selector.transform(data)
                    
                    preds = model.predict_proba(data)
                    results = [{'name':names[i], 'pos':pos, 'team':teams[i],'salary':salaries[i],
                                 'prob_0_5':preds[i][0], 'prob_5_10':preds[i][1],
                                 'prob_10_15':preds[i][2], 'prob_15_20':preds[i][3],
                                 'prob_20_25':preds[i][4],
                                 'prob_25+':preds[i][5], 
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
                    filepath = PREDICTIONS_DIR + str(self.week) +"/classification_" + pos + "_preds.csv"
                else:
                    filepath = PREDICTIONS_DIR + str(self.week) +"/regression_" + pos + "_preds.csv" 
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
    parser.add_argument("--week", type=int, action="store",help="Week number for predictions", required=True)
    parser.add_argument("--eval", type=str, action="store", help="Evaluate models? True/False")
    parser.add_argument("--all", type=str, action="store", help="Run preds on all weeks up to --week", default='False')
    args = parser.parse_args()

    fantasyModels = FantasyPredictionModel(args.week, args.classification == 'True')
    if args.all == 'True':    
        fantasyModels.train()
        for week in xrange(1,args.week + 1):
            fantasyModels.week = week
            fantasyModels.predict()
    else:
        if args.eval == "True":
            fantasyModels.evaluate()
        else:
            fantasyModels.train()
            fantasyModels.predict()
