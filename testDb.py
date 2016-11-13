from FantasyDB import FantasyDB

from pprint import pprint
from time import time
import numpy as np
import logging

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

db = FantasyDB()

raw_x,raw_y = db.getTrainingExamples('RB',2)

data_X = np.array(raw_x, dtype='float64')
data_Y = np.array(raw_y, dtype='float64')

data, names = db.getPredictionPoints('RB', 2, '2016', 9)

# pipeline = Pipeline([
#     ('reg', RandomForestRegressor()),
# ])

# # uncommenting more parameters will give better exploring power but will
# # increase processing time in a combinatorial way
# parameters = {
#     'reg__n_estimators': (10,20,30,40,50),
#     'reg__max_features': ('auto', 'sqrt','log2'),
#     'reg__max_depth': (None, 1,2,3,4,5,10,15,20,30,40),
#     'reg__min_samples_split': (1,2,3,4,5),
#     'reg__bootstrap': (True, False),
#     'reg__random_state':[42],
#     'reg__criterion': ('mse','mae')
# }

# if __name__ == "__main__":
#     # multiprocessing requires the fork to happen in a __main__ protected
#     # block

#     # find the best parameters for the classifier
#     grid_search = GridSearchCV(pipeline, parameters, n_jobs=-1, verbose=1)

#     print("Performing grid search...")
#     print("parameters:")
#     pprint(parameters)
#     t0 = time()
#     grid_search.fit(data_X, data_Y)
#     print("done in %0.3fs" % (time() - t0))
#     print()

#     print("Best score: %0.3f" % grid_search.best_score_)
#     print("Best parameters set:")
#     best_parameters = grid_search.best_estimator_.get_params()
#     for param_name in sorted(parameters.keys()):
#         print("\t%s: %r" % (param_name, best_parameters[param_name]))