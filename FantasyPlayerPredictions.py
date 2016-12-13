from Data import FantasyDB
import MLParams
import csv
import argparse
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.feature_selection import f_classif, mutual_info_classif, SelectPercentile

POSITIONS = ['QB', 'WR', 'RB', 'TE', 'PK', 'Def']
# POSITIONS = ['QB']


CURRENT_YEAR = '2016'

PREDICTIONS_DIR = 'Data/Predictions/Week'
OUTPUT_FIELDS_REGRESSION = ['name', 'pos', 'team', 'prediction', 'salary']
OUTPUT_FIELDS_CLASSIFICATION = ['name', 'pos', 'team', 'expectation','salary','prob_0_5',
                                'prob_5_10', 'prob_10_15', 'prob_15_20' ,'prob_20_25','prob_25_30','prob_30+']
OUTPUT_FIELDS_CLASSIFICATION_LABELS = ['name', 'pos', 'team', 'expectation','salary','prob_0_5',
                                'prob_5_10', 'prob_10_15', 'prob_15_20' ,'prob_20_25','prob_25_30','prob_30+','label']



class FantasyPredictionModel:

    def __init__(self, target_week, classification, algo, labels):
        self.db = FantasyDB.FantasyDB()      
        self.week = target_week
        self.classification = classification
        self.models = {}
        self.selectors = {}
        self.accuracies = {}
        self.algo = algo
        self.model_params = MLParams.getModelParams(algo, self.classification)
        self.testingGameleads = False
        self.labels = labels

    

    def getLearner(self, pos):
        if self.classification:
            if self.algo == 'RF':
                return RandomForestClassifier(n_estimators = self.model_params[pos]['n_estimators'],
                                            max_depth = self.model_params[pos]['max_depth'],
                                            max_features = self.model_params[pos]['max_features'], 
                                            min_samples_split = self.model_params[pos]['min_samples_split'],
                                            class_weight = self.model_params[pos]['class_weights'],
                                            bootstrap = self.model_params[pos]['bootstrap'],
                                            n_jobs=-1)
            if self.algo == 'GDBT':
                return GradientBoostingClassifier(loss = self.model_params[pos]['loss'],
                                                  learning_rate = self.model_params[pos]['learning_rate'],
                                                  n_estimators = self.model_params[pos]['n_estimators'],
                                                  max_depth = self.model_params[pos]['max_depth'],
                                                  min_samples_split = self.model_params[pos]['min_samples_split'],
                                                  max_features = self.model_params[pos]['max_features'],
                                                  subsample = self.model_params[pos]['subsample'])
            if self.algo == 'LReg':
                return LogisticRegression(fit_intercept = self.model_params[pos]['fit_intercept'],
                                          intercept_scaling = self.model_params[pos]['intercept_scaling'],
                                          class_weight = self.model_params[pos]['class_weight'],
                                          max_iter = self.model_params[pos]['max_iter'],
                                          solver = self.model_params[pos]['solver'],
                                          tol = self.model_params[pos]['tol'],
                                          multi_class = self.model_params[pos]['multi_class'],
                                          n_jobs = -1)
        else:
            if self.algo == 'GDBT':
                return GradientBoostingRegressor(loss = self.model_params[pos]['loss'],
                                                  learning_rate = self.model_params[pos]['learning_rate'],
                                                  n_estimators = self.model_params[pos]['n_estimators'],
                                                  max_depth = self.model_params[pos]['max_depth'],
                                                  min_samples_split = self.model_params[pos]['min_samples_split'],
                                                  max_features = self.model_params[pos]['max_features'],
                                                  subsample = self.model_params[pos]['subsample'])
            if self.algo == 'RF':
                return RandomForestRegressor(n_estimators = self.model_params[pos]['n_estimators'],
                                        max_depth = self.model_params[pos]['max_depth'],
                                        max_features= self.model_params[pos]['max_features'], 
                                        min_samples_split=self.model_params[pos]['min_samples_split'],
                                        bootstrap = self.model_params[pos]['bootstrap'],
                                        criterion = self.model_params[pos]['criterion'],
                                        n_jobs=-1)
            if self.algo == 'LReg':
                return LinearRegression(fit_intercept = self.model_params[pos]['fit_intercept'],
                                        normalize = self.model_params[pos]['normalize'],
                                        copy_X = True,
                                        n_jobs = -1)
    def getFeatureSelector(self, pos):
        if pos == 'PK':
            return SelectPercentile(f_classif, percentile=self.model_params[pos]['feature_percent'])
                
        return SelectPercentile(mutual_info_classif, percentile=self.model_params[pos]['feature_percent'])

    def getTrainData(self, pos):
        #raw_x, raw_y = None,None
        if self.testingGameleads:
            raw_x, raw_y = self.db.getTrainingExamples(pos,self.gamelead, self.classification)
        else:
            raw_x,raw_y = self.db.getTrainingExamples(pos,self.model_params[pos]['gamelead'], self.classification)
        data_X = np.array(raw_x, dtype='float64')
        data_Y = np.array(raw_y, dtype='float64')
        return data_X, data_Y

    def getPredData(self, pos):
        #raw_x, raw_y = None,None
        if self.testingGameleads:
            raw_x, raw_y = self.db.getTrainingExamples(pos,self.gamelead, self.classification)
        else:
            raw_data, names, salaries, teams = self.db.getPredictionPoints(pos, self.model_params[pos]['gamelead'], CURRENT_YEAR, self.week)
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
            
            print data_X.shape
            learner = self.getLearner(pos)
            learner.fit(data_X, data_Y)

            self.models[pos] = learner

    def evaluate(self):
        for pos in POSITIONS:
            print("-----------------------Evaluating %s Model---------------------") %(pos)
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
            print("-----------------------Predicting %s-----------------------") %(pos)
            data, names, salaries, teams = self.getPredData(pos)
            if pos in self.models:
                model = self.models[pos]
                if self.classification:
                    if self.labels:
                        selector = self.selectors[pos]
                        data = selector.transform(data)
                        
                        preds = model.predict_proba(data)
                        labels = model.predict(data)
                        if pos != 'PK':
                            results = [{'name':names[i], 'pos':pos, 'team':teams[i],'salary':salaries[i],
                                        'prob_0_5':preds[i][0], 'prob_5_10':preds[i][1],
                                        'prob_10_15':preds[i][2], 'prob_15_20':preds[i][3],
                                        'prob_20_25':preds[i][4],
                                        'prob_25_30':preds[i][5],
                                        'prob_30+':preds[i][6], 
                                        'expectation': self.db.computeExpectation(preds[i]),
                                        'label': labels[i]}\
                                        for i in xrange(len(preds))]
                        else:
                            results = [{'name':names[i], 'pos':pos, 'team':teams[i],'salary':salaries[i],
                                        'prob_0_5':preds[i][0], 'prob_5_10':preds[i][1],
                                        'prob_10_15':preds[i][2], 'prob_15_20':preds[i][3],
                                        'prob_20_25':preds[i][4],
                                        'prob_25_30':preds[i][5],
                                        'prob_30+':0.0, #Due to training data, PK training never sees this class so set to 0
                                        'expectation': self.db.computeExpectation(preds[i]),
                                        'label': labels[i]} \
                                        for i in xrange(len(preds))]
                        results = sorted(results, key=lambda x: x['expectation'], reverse=True)
                    else: 
                        selector = self.selectors[pos]
                        data = selector.transform(data)
                        
                        preds = model.predict_proba(data)
                        if pos != 'PK':
                            results = [{'name':names[i], 'pos':pos, 'team':teams[i],'salary':salaries[i],
                                        'prob_0_5':preds[i][0], 'prob_5_10':preds[i][1],
                                        'prob_10_15':preds[i][2], 'prob_15_20':preds[i][3],
                                        'prob_20_25':preds[i][4],
                                        'prob_25_30':preds[i][5],
                                        'prob_30+':preds[i][6], 
                                        'expectation': self.db.computeExpectation(preds[i])}\
                                        for i in xrange(len(preds))]
                        else:
                            results = [{'name':names[i], 'pos':pos, 'team':teams[i],'salary':salaries[i],
                                        'prob_0_5':preds[i][0], 'prob_5_10':preds[i][1],
                                        'prob_10_15':preds[i][2], 'prob_15_20':preds[i][3],
                                        'prob_20_25':preds[i][4],
                                        'prob_25_30':preds[i][5],
                                        'prob_30+':0.0, #Due to training data, PK training never sees this class so set to 0
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
                    filepath = PREDICTIONS_DIR + str(self.week) +"/classification_" + self.algo + "_" + pos + "_preds.csv"
                else:
                    filepath = PREDICTIONS_DIR + str(self.week) +"/regression_" + self.algo + "_" + pos + "_preds.csv" 
                with open(filepath,'wb') as outfile:    
                    outfile.truncate()
                    if self.classification:
                        if self.labels:
                            writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS_CLASSIFICATION_LABELS)
                        else:  
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
    parser.add_argument("--eval", type=str, action="store", help="Evaluate models? True/False", default='False')
    parser.add_argument("--all", type=str, action="store", help="Run preds on all weeks up to --week", default='False')
    parser.add_argument("--algo", type=str, action="store", help="Algorithm to use: RF, GDBT, LReg", default="RF")
    parser.add_argument("--allGameleads", type=str, action="store", help="Check all gameleads? True/False", default="False")
    parser.add_argument("--labels", type=str, action="store", help="Calculate classification labels instead of buckets? True/False", default='False')
    args = parser.parse_args()


    fantasyModels = FantasyPredictionModel(args.week, args.classification == 'True', args.algo, args.labels == 'True')

    if args.allGameleads == 'True':
        fantasyModels.testingGameleads = True
        for i in range(2, 13):
            print('-------------------------- Gamelead = ' + str(i) + ' --------------------------')
            fantasyModels.gamelead = i
            if args.all == 'True':    
                for week in xrange(1,args.week + 1):
                    fantasyModels.week = week
                    fantasyModels.train()
                    fantasyModels.predict()
            else:
                if args.eval == "True":
                    fantasyModels.evaluate()
                else:
                    fantasyModels.train()
                    fantasyModels.predict()
    else: 
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
