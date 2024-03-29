import csv
# from FantasyMDP import FantasyMDP
# from FantasyCSPConstructor import FantasyCSPConstructor
# from util import ValueIteration
# from BacktrackingSearch import BacktrackingSearch
from Data import FantasyDB
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import accuracy_score


# #Note: really slow. Would not recommend.
# mdp = FantasyMDP()
# alg = ValueIteration()
# alg.solve(mdp, .001)

TYPES = ['regression', 'classification'] #or TYPE == 'classification'
ALGORITHMS = ['LReg']

PRED_PTS_PATH = 'Data/Predictions/Week'
PRED_PTS_FILE_END = '_preds.csv'
OUTPUT_FILE_PATH = 'Evaluations/Players/'
OUTPUT_FILE_END = '_eval.csv'
POSITIONS = ['QB', 'WR', 'RB', 'TE', 'PK', 'Def']
WEEKS = 14
YEAR = '2016'


# Output error on each 



db = FantasyDB.FantasyDB()

def getActualLabel(player, week, pos):
    return db.getClassLabel(getActualPts(player, week, pos))

def getActualPts(player, week, pos):
    pos_data = db.getData(pos)
    try:
        if player in pos_data:
            pts = pos_data[player][YEAR][str(week)]['fd_pts']
            return pts
        else:
            return 0
    except TypeError:
        # print 'Can\'t find player ' + player + ' in week ' + str(week)
        return 0

def getErrorInfo(position, task, algo):
    target_true = []
    target_predicted = []
    classification_true = []
    classification_predicted = []
    for week in range(1, WEEKS+1):
        filename = PRED_PTS_PATH + str(week) + '/' + task + '_' + algo + '_' + position + PRED_PTS_FILE_END
        print filename
        with open(filename, 'r') as infile:
            infile.next()
            reader = csv.reader(infile, delimiter=',', quotechar='"')
            for line in reader:
                name, pos, team, predPts, sal = line[:5]
                if task == 'classification':
                    label = line[-1]
                    classification_predicted.append(label)
                    classification_true.append(getActualLabel(name, week, pos))
                target_predicted.append(predPts)
                target_true.append(getActualPts(name, week, pos))

    true_array = np.array(target_true, dtype='float64')
    pred_array = np.array(target_predicted, dtype='float64')
    mae = mean_absolute_error(true_array, pred_array, multioutput='uniform_average')
    mse = mean_squared_error(true_array, pred_array, multioutput='uniform_average')
    evs = explained_variance_score(true_array, pred_array, multioutput='uniform_average')
    if task == 'classification':
        classif_true_array = np.array(classification_true, dtype='float64')
        classif_pred_array = np.array(classification_predicted, dtype='float64')
        acs = accuracy_score(classif_true_array,classif_pred_array)
    else:
        acs = None
    return mae, mse, evs, acs

for task in TYPES:
    for algo in ALGORITHMS:
        with open(OUTPUT_FILE_PATH + task + '_' + algo + OUTPUT_FILE_END, 'wb') as outfile:
            outfile.truncate()
            if task == 'classification':
                outfile.write('"Position","Mean Absolute Error","Mean Squared Error","Explained Variance Score","Accuracy Score"\n')
            else:
                outfile.write('"Position","Mean Absolute Error","Mean Squared Error","Explained Variance Score"\n')

            for pos in POSITIONS:
                errors = getErrorInfo(pos, task, algo)
                output = '"' + pos
                for error in errors:
                    output += '","' + str(error)
                outfile.write(output + '"\n')



