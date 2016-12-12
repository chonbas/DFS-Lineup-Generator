def getRFParams():
    QB_PARAMS = {'n_estimators':700, 'max_depth':None, 'max_features':'log2',
                'min_samples_split':2,'feature_percent':32, 'gamelead':13,
                'class_weights':None,'bootstrap':True}

    WR_PARAMS = {'n_estimators':1000, 'max_depth':10, 'max_features':'log2', 
                'min_samples_split':2,'feature_percent':35, 'gamelead':6,
                'class_weights':None, 'bootstrap':True}

    RB_PARAMS = {'n_estimators':500, 'max_depth':10, 'max_features':'log2',
                'min_samples_split':2,'feature_percent':31, 'gamelead':2,
                'class_weights':None, 'bootstrap':False}

    TE_PARAMS = {'n_estimators':500, 'max_depth':10, 'max_features':'log2',
                'min_samples_split':2,'feature_percent':30, 'gamelead':2,
                'class_weights':None, 'bootstrap':False}

    PK_PARAMS = {'n_estimators':700, 'max_depth':7, 'max_features':'log2',
                'min_samples_split':2, 'feature_percent':100, 'gamelead':2,
                'class_weights':None, 'bootstrap':False}

    DEF_PARAMS = {'n_estimators':500, 'max_depth':20, 'max_features':'log2',
                'min_samples_split':2,'feature_percent':75, 'gamelead':3,
                'class_weights':None, 'bootstrap':True}

    return {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}

def getModelParams(algo):
    if algo == "RF":
        return getRFParams()