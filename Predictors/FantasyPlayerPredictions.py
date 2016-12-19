from Data import FantasyDB
import MLParams
import csv
import argparse
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import average_precision_score
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import label_binarize
from sklearn.metrics import confusion_matrix
from sklearn.feature_selection import f_classif, mutual_info_classif, SelectPercentile

POSITIONS = ['QB', 'WR', 'RB', 'TE', 'PK', 'Def']
# POSITIONS = ['WR']

CURRENT_YEAR = '2016'

PREDICTIONS_DIR = 'Data/Predictions/Week'

OUTPUT_FIELDS_CLASSIFICATION_LABELS = ['name', 'pos', 'team', 'expectation','salary','prob_0_5',
                                'prob_5_10', 'prob_10_15', 'prob_15_20' ,'prob_20+','label']

class FantasyPredictionModel:

    def __init__(self, target_week):
        self.db = FantasyDB.FantasyDB()      
        self.week = target_week
        self.models = {}
        self.selectors = {}
        self.accuracies = {}
        self.model_params = MLParams.getModelParams()

    def getLearner(self, pos):
        return RandomForestClassifier(n_estimators = self.model_params[pos]['n_estimators'],
                                      max_depth = self.model_params[pos]['max_depth'],
                                      max_features = self.model_params[pos]['max_features'], 
                                      min_samples_split = self.model_params[pos]['min_samples_split'],
                                      class_weight = self.model_params[pos]['class_weights'],
                                      bootstrap = self.model_params[pos]['bootstrap'],
                                      n_jobs=-1)
    def getFeatureSelector(self, pos):
        if pos == 'PK':
            return SelectPercentile(f_classif, percentile=self.model_params[pos]['feature_percent'])
                
        return SelectPercentile(mutual_info_classif, percentile=self.model_params[pos]['feature_percent'])

    def getTrainData(self, pos):
        raw_x,raw_y = self.db.getTrainingExamples(pos,self.model_params[pos]['gamelead'], self.week)
        raw_y_labels = [value[0] for value in raw_y]
        raw_y_values = [value[1] for value in raw_y]
        data_X = np.array(raw_x, dtype='float64')
        data_Y_labels = np.array(raw_y_labels, dtype='float64')
        data_Y_values = np.array(raw_y_values, dtype='float64')
        return data_X, data_Y_labels, data_Y_values

    def getPredData(self, pos):
        raw_data, names, salaries, teams = self.db.getPredictionPoints(pos, self.model_params[pos]['gamelead'], CURRENT_YEAR, self.week)
        for i in xrange(len(raw_data)):
            raw_data[i] = np.array(raw_data[i], dtype='float64') 
        data = np.array(raw_data, dtype='float64')
        return data, names, salaries, teams  
        
    def train(self):
        for pos in POSITIONS:
            print('-----------------------Training %s Model---------------------') %(pos)

            data_X, data_Y_labels, data_Y_values  = self.getTrainData(pos)

            selector = self.getFeatureSelector(pos)
            data_X = selector.fit_transform(data_X, data_Y_labels)
            self.selectors[pos] = selector

            learner = self.getLearner(pos)
            learner.fit(data_X, data_Y_labels)

            self.models[pos] = learner

    def evaluate(self):
        ####
        #### TODO : ADD TRAINDATA FOR REGRESSION TO EVALUATE EXPECTATION AS WELL
        ####
        for pos in POSITIONS:
            print('-----------------------Evaluating %s Model---------------------') %(pos)
            data_X, data_Y_labels, data_Y_values = self.getTrainData(pos)
            learner = self.getLearner(pos)
            data_train, data_test, target_train, target_test = train_test_split(data_X, data_Y_labels, test_size=0.20, random_state=42)
            
            selector = self.getFeatureSelector(pos)
            data_train = selector.fit_transform(data_train, target_train)
            data_test = selector.transform(data_test)
            learner.fit(data_train, target_train)

            preds = learner.predict(data_test)
            
            self.accuracies[pos] = self.evaluateClassificationResults(target_test, preds)
        for pos in POSITIONS:
            print('Roc-Auc Score for %s is : %f') %(pos, self.accuracies[pos])

                 
    def evaluateClassificationResults(self, target_true,target_predicted):
        print('-----------------------Evaluation---------------------------')
        print(classification_report(target_true,target_predicted))
        bin_true = label_binarize(target_true, [0,1,2,3,4])
        bin_preds = label_binarize(target_predicted, [0,1,2,3,4])
        print('The accuracy is {:.2%}'.format(accuracy_score(target_true,target_predicted)))
        print('The ROC-AUC is {:.2%}'.format(roc_auc_score(bin_true, bin_preds)))
        print('The average precision score is {:.2%}'.format(average_precision_score(bin_true,bin_preds)))
        
        # cm = confusion_matrix(target_true,target_predicted)
        # np.set_printoptions(precision=2)
        # print('Confusion matrix, without normalization')
        # print(cm)
        # cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        # print('Normalized confusion matrix')
        # print(cm_normalized)
        # print('\n\n')
        return roc_auc_score(bin_true, bin_preds)
    
    def evaluateRegressionResults(self, target_true, target_predicted, verbose_flag):
        print('-----------------------Evaluation---------------------------')
        errors = {'mean_absolute_error':mean_absolute_error(target_true, target_predicted, multioutput='uniform_average'),
                  'mean_squared_error':mean_squared_error(target_true, target_predicted, multioutput='uniform_average'), 
                  'explained_variance_score':explained_variance_score(target_true, target_predicted, multioutput='uniform_average')}
        for key in errors:
            print('%s : %f') %(key, errors[key])
        return errors

    def predict(self):
        for pos in POSITIONS:
            print('-----------------------Predicting %s-----------------------') %(pos)
            data, names, salaries, teams = self.getPredData(pos)
            if pos in self.models:
                model = self.models[pos]
        
                selector = self.selectors[pos]
                data = selector.transform(data)
                
                preds = model.predict_proba(data)
                labels = model.predict(data)

                results = [{'name':names[i], 'pos':pos, 'team':teams[i],'salary':salaries[i],
                            'prob_0_5':preds[i][0], 'prob_5_10':preds[i][1],
                            'prob_10_15':preds[i][2], 'prob_15_20':preds[i][3],
                            'prob_20+':preds[i][4],
                            'expectation': self.db.computeExpectation(preds[i]),
                            'label': labels[i]}\
                            for i in xrange(len(preds))]

                results = sorted(results, key=lambda x: x['expectation'], reverse=True)

                self.writePreds(results, pos)
            else:
                print('Models must be trained prior to running predictions.')
                return

    def writePreds(self, results, pos):
        filepath = PREDICTIONS_DIR + str(self.week) + '/' + pos + '_preds.csv'
        with open(filepath,'wb') as outfile:    
            outfile.truncate()
            writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS_CLASSIFICATION_LABELS)
            writer.writeheader()
            for result in results:
                writer.writerow(result)

