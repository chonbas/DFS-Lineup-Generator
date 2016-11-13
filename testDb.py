from FantasyDB import FantasyDB
import csv
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score

POSITIONS = ['RB', 'WR', 'TE', 'QB', 'PK', 'Def']
PREDICTIONS_DIR = 'Predictions/Week'
GAME_LEAD = 3 
WEEK = 9
OUTPUT_FIELDS = ['name', 'pos', 'team', 'prediction', 'salary']

db = FantasyDB()

for pos in POSITIONS:
    raw_x,raw_y = db.getTrainingExamples(pos,GAME_LEAD)

    data_X = np.array(raw_x, dtype='float64')
    data_Y = np.array(raw_y, dtype='float64')

    data, names, salaries, teams = db.getPredictionPoints(pos, GAME_LEAD, '2016', WEEK)

    reg = RandomForestRegressor(n_estimators = 100, max_depth = 15, max_features= 'sqrt', min_samples_split=2)
    #reg =  GradientBoostingRegressor(max_features='log2', n_estimators=50)
    # data_train, data_test, target_train, target_test = train_test_split(data_X, data_Y, test_size=0.20, random_state=42)
    # reg = LogisticRegression(solver='sag', n_jobs=-1, max_iter=1000)
    # reg.fit(data_train, target_train)
    reg.fit(data_X, data_Y)

    # preds = reg.predict(data_test)
    preds = reg.predict(data)
    # prob_preds = reg.predict_proba(data)
    results = [{'name':names[i], 'pos':pos, 'team':teams[i], 'prediction':preds[i], 
                'salary':salaries[i]} \
                for i in xrange(len(preds))]

    results = sorted(results, key=lambda x: x['prediction'], reverse=True)

    with open(PREDICTIONS_DIR + str(WEEK) +"/" + pos + "preds.csv",'wb') as outfile:    
        outfile.truncate()    
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for result in results:
            writer.writerow(result)