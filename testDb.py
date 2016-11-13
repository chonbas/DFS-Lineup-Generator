from FantasyDB import FantasyDB

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score

POSITIONS = ['RB', 'WR', 'TE', 'QB', 'PK', 'Def']
GAME_LEAD = 3 
WEEK = 9
db = FantasyDB()

for pos in POSITIONS:
    raw_x,raw_y = db.getTrainingExamples(pos,GAME_LEAD)

    data_X = np.array(raw_x, dtype='float64')
    data_Y = np.array(raw_y, dtype='float64')

    # data, names = db.getPredictionPoints(pos, GAME_LEAD, '2016', WEEK)

    reg = RandomForestRegressor(n_estimators = 100, max_depth = 15, max_features= 'sqrt', min_samples_split=2)
    
    data_train, data_test, target_train, target_test = train_test_split(data_X, data_Y, test_size=0.20, random_state=42)

    reg.fit(data_train, target_train)
    # reg.fit(data_X, data_Y)

    preds = reg.predict(data_test)
    # preds = reg.predict(data)
    # results = [(preds[i], names[i]) for i in xrange(len(preds))]
    # results = sorted(results, key=lambda x: x[0], reverse=True)
    # print pos

    # for player in xrange(len(results)):
    #     print results[player]
    #     if player == 10:
    #         break
    # print results
    print pos + " trained - explained variance:"
    print explained_variance_score(target_test, preds)
    # print pos + " trained - mean absolute error:"
    # print mean_absolute_error(target_test, preds)
    # print pos + " trained - mean squared error:"
    # print mean_squared_error(target_test, preds)



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