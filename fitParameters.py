from __future__ import print_function

from pprint import pprint
from time import time

from FantasyDB import FantasyDB
import csv
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression
from sklearn.feature_selection import mutual_info_regression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score


POSITIONS = ['RB', 'WR', 'TE', 'QB', 'PK', 'Def']
GAME_LEAD = 3 
WEEK = 9

pipeline = Pipeline([
    ('reg', RandomForestRegressor()),
])

if __name__ == "__main__":
    # multiprocessing requires the fork to happen in a __main__ protected
    # block

    # find the best parameters for both the feature extraction and the
    # classifier
    db = FantasyDB()
   
    for pos in POSITIONS:
        raw_x,raw_y = db.getTrainingExamples(pos,GAME_LEAD)

        data_X = np.array(raw_x, dtype='float64')
        data_Y = np.array(raw_y, dtype='float64')
        parameters = {
            'reg__n_estimators': (50,75,100,125),
            'reg__max_features': ('auto', 'sqrt', 'log2'),
            'reg__max_depth': (None, 5,10,15,20)
        }
        grid_search = GridSearchCV(pipeline, parameters, n_jobs=-1, verbose=1)

        print("Performing grid search...")
        print("pipeline:", [name for name, _ in pipeline.steps])
        print("parameters:")
        pprint(parameters)
        t0 = time()
        grid_search.fit(data_X, data_Y)
        print("done in %0.3fs" % (time() - t0))
        print()

        print("Best score: %0.3f" % grid_search.best_score_)
        print("Best parameters set:")
        best_parameters = grid_search.best_estimator_.get_params()
        for param_name in sorted(parameters.keys()):
            print("\t%s: %r" % (param_name, best_parameters[param_name]))
