def getRFParams(classification):
    #n_estimators = number of trees in random forest
    #max_depth = max depth of individual trees in forest
    #max_Features = max number of features to consider for each tree
    #min_samples_split = number of sampels to see to branch a leaf in tree 
    #feature_percent top % of features to extract using automated feature extraction
    #gamelead = number of previous game data to use for feature vector
    #class_weights = regularization terms to add extra penalty for errors in certain classes
    #bootstrap = whether to build new trees using bootstrapped data from previous trees
    if classification:
        QB_PARAMS = {'n_estimators':700, 'max_depth':None, 'max_features':'log2',
                    'min_samples_split':2,'feature_percent':90, 'gamelead':13,
                    'class_weights':None,'bootstrap':True}

        WR_PARAMS = {'n_estimators':1000, 'max_depth':10, 'max_features':'log2', 
                    'min_samples_split':2,'feature_percent':35, 'gamelead':6,
                    'class_weights':None, 'bootstrap':True}

        RB_PARAMS = {'n_estimators':500, 'max_depth':10, 'max_features':'log2',
                    'min_samples_split':2,'feature_percent':31, 'gamelead':3,
                    'class_weights':None, 'bootstrap':False}

        TE_PARAMS = {'n_estimators':500, 'max_depth':10, 'max_features':'log2',
                    'min_samples_split':2,'feature_percent':30, 'gamelead':3,
                    'class_weights':None, 'bootstrap':False}

        PK_PARAMS = {'n_estimators':700, 'max_depth':7, 'max_features':'log2',
                    'min_samples_split':2, 'feature_percent':100, 'gamelead':3,
                    'class_weights':None, 'bootstrap':False}

        DEF_PARAMS = {'n_estimators':500, 'max_depth':20, 'max_features':'log2',
                    'min_samples_split':2,'feature_percent':75, 'gamelead':6,
                    'class_weights':None, 'bootstrap':True}

        return {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}
    else:
        QB_PARAMS = {'n_estimators':700, 'max_depth':None, 'max_features':'log2',
                    'min_samples_split':2,'feature_percent':32, 'gamelead':13,
                    'bootstrap':True, 'criterion':'mse'}

        WR_PARAMS = {'n_estimators':1000, 'max_depth':10, 'max_features':'log2', 
                    'min_samples_split':2,'feature_percent':35, 'gamelead':6,
                    'bootstrap':True, 'criterion':'mse'}

        RB_PARAMS = {'n_estimators':500, 'max_depth':10, 'max_features':'log2',
                    'min_samples_split':2,'feature_percent':31, 'gamelead':3,
                    'bootstrap':False, 'criterion':'mse'}

        TE_PARAMS = {'n_estimators':500, 'max_depth':10, 'max_features':'log2',
                    'min_samples_split':2,'feature_percent':30, 'gamelead':3,
                    'bootstrap':False, 'criterion':'mse'}

        PK_PARAMS = {'n_estimators':700, 'max_depth':7, 'max_features':'log2',
                    'min_samples_split':2, 'feature_percent':100, 'gamelead':3,
                    'bootstrap':False, 'criterion':'mse'}

        DEF_PARAMS = {'n_estimators':500, 'max_depth':20, 'max_features':'log2',
                    'min_samples_split':2,'feature_percent':75, 'gamelead':6,
                    'bootstrap':True, 'criterion':'mse'}

        return {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}

def getGDBTParams(classification):
    if classification:
        QB_PARAMS = {'loss':'deviance', 'learning_rate':0.1, 'n_estimators':700, 'max_depth':None,
                    'min_samples_split':2,'max_features':'log2','subsample':1.0,'gamelead':13,
                    'feature_percent':90, 'class_weight':{5:4,6:3}}

        WR_PARAMS = {'loss':'deviance', 'learning_rate':0.01, 'n_estimators':500, 'max_depth':None,
                    'min_samples_split':2,'max_features':'log2','subsample':1.0,'gamelead':6,
                    'feature_percent':80, 'class_weight':{5:4,6:4}}

        RB_PARAMS = {'loss':'deviance', 'learning_rate':0.1, 'n_estimators':500, 'max_depth':None,
                    'min_samples_split':2,'max_features':'log2','subsample':1.0,'gamelead':3,
                    'feature_percent':80, 'class_weight':None}

        TE_PARAMS = {'loss':'deviance', 'learning_rate':0.1, 'n_estimators':500, 'max_depth':10,
                    'min_samples_split':2,'max_features':'log2','subsample':1.0,'gamelead':3,
                    'feature_percent':100, 'class_weight':None}

        PK_PARAMS = {'loss':'deviance', 'learning_rate':0.1, 'n_estimators':700, 'max_depth':7,
                    'min_samples_split':2,'max_features':'log2','subsample':1.0,'gamelead':3,
                    'feature_percent':100, 'class_weight':None}

        DEF_PARAMS = {'loss':'deviance', 'learning_rate':0.1, 'n_estimators':500, 'max_depth':None,
                    'min_samples_split':2,'max_features':'log2','subsample':1.0,'gamelead':6,
                    'feature_percent':100, 'class_weight':None}

        return {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}
    else:
        QB_PARAMS = {'loss':'ls', 'learning_rate':0.1, 'n_estimators':700, 'max_depth':None,
                    'min_samples_split':2,'max_features':'log2','subsample':1.0,'gamelead':13}

        WR_PARAMS = {'loss':'ls', 'learning_rate':0.1, 'n_estimators':700, 'max_depth':None,
                    'min_samples_split':2,'max_features':'log2','subsample':1.0,'gamelead':13}

        RB_PARAMS = {'loss':'ls', 'learning_rate':0.1, 'n_estimators':700, 'max_depth':None,
                    'min_samples_split':2,'max_features':'log2','subsample':1.0,'gamelead':13}

        TE_PARAMS = {'loss':'ls', 'learning_rate':0.1, 'n_estimators':700, 'max_depth':None,
                    'min_samples_split':2,'max_features':'log2','subsample':1.0,'gamelead':13}
                    
        PK_PARAMS = {'loss':'ls', 'learning_rate':0.1, 'n_estimators':700, 'max_depth':None,
                    'min_samples_split':2,'max_features':'log2','subsample':1.0,'gamelead':13}
                    
        DEF_PARAMS = {'loss':'ls', 'learning_rate':0.1, 'n_estimators':700, 'max_depth':None,
                    'min_samples_split':2,'max_features':'log2','subsample':1.0,'gamelead':13}
                    
        return {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}

def getLRegParams(classification):
    if classification:
        QB_PARAMS = {'fit_intercept':True, 'intercept_scaling':1, 'class_weight':None,
                    'max_iter':1000, 'solver':'lbfgs','tol':0.0001,'multi_class':'multinomial','gamelead':13,
                    'feature_percent':85}

        WR_PARAMS = {'fit_intercept':True, 'intercept_scaling':1, 'class_weight':{4:2, 5:2, 6:2},
                    'max_iter':1000, 'solver':'lbfgs','tol':0.0001,'multi_class':'multinomial','gamelead':5,
                    'feature_percent':90}

        RB_PARAMS = {'fit_intercept':True, 'intercept_scaling':1, 'class_weight':{4:2, 5:2, 6:2},
                    'max_iter':1000, 'solver':'lbfgs','tol':0.0001,'multi_class':'multinomial','gamelead':3,
                    'feature_percent':85}
                    
        TE_PARAMS = {'fit_intercept':True, 'intercept_scaling':1, 'class_weight':{4:2, 5:2, 6:2},
                    'max_iter':1000, 'solver':'lbfgs','tol':0.0001,'multi_class':'multinomial','gamelead':3,
                    'feature_percent':80}

        PK_PARAMS = {'fit_intercept':True, 'intercept_scaling':1, 'class_weight':{3:2},
                    'max_iter':1000, 'solver':'lbfgs','tol':0.0001,'multi_class':'multinomial','gamelead':3,
                    'feature_percent':100}

        DEF_PARAMS = {'fit_intercept':True, 'intercept_scaling':1, 'class_weight':{3:2, 4:2, 5:2, 6:2},
                    'max_iter':1000, 'solver':'lbfgs','tol':0.0001,'multi_class':'multinomial','gamelead':4,
                    'feature_percent':75}

        return {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}
    else:
        QB_PARAMS = {'fit_intercept':None, 'normalize':None,'gamelead':None,'feature_percent':35}

        WR_PARAMS = {'fit_intercept':None, 'normalize':None,'gamelead':None,'feature_percent':35}

        RB_PARAMS = {'fit_intercept':None, 'normalize':None,'gamelead':None,'feature_percent':35}

        TE_PARAMS = {'fit_intercept':None, 'normalize':None,'gamelead':None,'feature_percent':35}

        PK_PARAMS = {'fit_intercept':None, 'normalize':None,'gamelead':None,'feature_percent':35}

        DEF_PARAMS = {'fit_intercept':None, 'normalize':None,'gamelead':None,'feature_percent':35}

        return {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}

def getModelParams(algo, classification):
    if algo == 'RF':
        return getRFParams(classification)
    if algo == 'GDBT':
        return getGDBTParams(classification)
    if algo == 'LReg':
        return getLRegParams(classification)