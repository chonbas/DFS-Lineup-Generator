from __future__ import print_function

from pprint import pprint
from time import time

from Data import FantasyDB
import csv
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import make_scorer
from sklearn.feature_selection import mutual_info_classif, f_classif, SelectPercentile
from sklearn.preprocessing import label_binarize

CURRENT_WEEK = 15

POSITIONS = ['PK']


MIN_GAME_LEAD = 3
MAX_GAME_LEAD = 3





best_params = {'QB':None, 'WR':None, 'RB':None, 'TE':None, 'PK':None, 'Def':None }

def getTrainData(pos, game_lead):
    raw_x,raw_y_values = db.getTrainingExamples(pos,game_lead, CURRENT_WEEK)
    raw_y = [value[0] for value in raw_y_values]
    raw_y_reg = [value[1] for value in raw_y_values]
    data_X = np.array(raw_x, dtype='float64')
    data_Y = np.array(raw_y, dtype='float64')
    data_Y_reg = np.array(raw_y_reg, dtype='float64')    
    return data_X, data_Y, data_Y_reg

def binaryRocAucScore(y_true, y_pred):
    bin_true = label_binarize(y_true,[0,1,2,3,4])
    bin_pred = label_binarize(y_pred,[0,1,2,3,4])
    return roc_auc_score(bin_true, bin_pred)

def avgPrecision(y_true, y_pred):
    bin_true = label_binarize(y_true,[0,1,2,3,4])
    bin_pred = label_binarize(y_pred,[0,1,2,3,4])
    return average_precision_score(bin_true, bin_pred)

def fitMLParams():
    db = FantasyDB.FantasyDB()
    pipeline = Pipeline([
                ('fs', SelectPercentile()),
                ('clf', RandomForestClassifier())
    ])
    parameters = {
                'fs__percentile': range(10,110,10),
                'fs__score_func': [f_classif],
                'clf__n_estimators': range(100,600,100),
                'clf__max_depth': range(5,30,5),
                'clf__max_features': ['log2'],
                'clf__min_samples_split': [2],
                'clf__bootstrap': [True],
                'clf__class_weight':['balanced'],
                'clf__n_jobs' :[-1]
    }
    rocauc_scorer = make_scorer(binaryRocAucScore, needs_proba=False)
    avgprecision_scorer = make_scorer(avgPrecision, needs_proba=False)
    for pos in POSITIONS:
        current_lead = 0
        current_best = 0
        current_params = None
        for game_lead in xrange(MIN_GAME_LEAD, MAX_GAME_LEAD + 1):
            print('------------- pos: ' + pos + ' -------------------')
            print('------------- game_lead: ' + str(game_lead) + ' -------------------')
            data_X, data_Y = getTrainData(pos, game_lead)

            grid_search = GridSearchCV(pipeline, parameters, n_jobs=-1, verbose=1, scoring=rocauc_scorer, cv=2)

            print('Performing grid search...')
            print('pipeline:', [name for name, _ in pipeline.steps])
            print('parameters:')
            pprint(parameters)
            t0 = time()
            grid_search.fit(data_X, data_Y)
            print('done in %0.3fs' % (time() - t0))
            print()

            print('Best score: %0.3f' % grid_search.best_score_)
            if grid_search.best_score_ > current_best:
                current_best = grid_search.best_score_
                current_lead = game_lead
                current_params = grid_search.best_estimator_.get_params()
            print('Best parameters set:')
            best_parameters = grid_search.best_estimator_.get_params()
            for param_name in sorted(parameters.keys()):
                print('\t%s: %r' % (param_name, best_parameters[param_name]))
        best_params[pos] = [current_lead, current_best, current_params]
    for pos in POSITIONS:
        print('------------------%s-------------------' %pos)
        pos_params = best_params[pos]
        best_lead, best_acc, model_params = pos_params
        
        print('Best Gamelead: %d' % best_lead)
        print('Best Accuracy: %0.4f' % best_acc)
        for param_name in sorted(parameters.keys()):
            print('\t%s: %r' % (param_name, model_params[param_name]))

