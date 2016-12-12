def getRFParams():
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
    else:
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

def getGDBTParams():
    if classification:
        QB_PARAMS = {'loss':, 'learning_rate':, 'n_estimators':, 'max_depth':, 'min_samples_split':,
                    'max_features':,'subsample':,'gamelead':,'feature_percent':35}

        WR_PARAMS = {'loss':, 'learning_rate':, 'n_estimators':, 'max_depth':, 'min_samples_split':,
                    'max_features':,'subsample':,'gamelead':,'feature_percent':35}

        RB_PARAMS = {'loss':, 'learning_rate':, 'n_estimators':, 'max_depth':, 'min_samples_split':,
                    'max_features':,'subsample':,'gamelead':,'feature_percent':35}

        TE_PARAMS = {'loss':, 'learning_rate':, 'n_estimators':, 'max_depth':, 'min_samples_split':,
                    'max_features':,'subsample':,'gamelead':,'feature_percent':35}

        PK_PARAMS = {'loss':, 'learning_rate':, 'n_estimators':, 'max_depth':, 'min_samples_split':,
                    'max_features':,'subsample':,'gamelead':,'feature_percent':35}

        DEF_PARAMS = {'loss':, 'learning_rate':, 'n_estimators':, 'max_depth':, 'min_samples_split':,
                    'max_features':,'subsample':,'gamelead':,'feature_percent':35}

        return {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}
    else:
        QB_PARAMS = {'loss':, 'learning_rate':, 'n_estimators':, 'max_depth':, 'min_samples_split':,
                    'max_features':,'subsample':,'gamelead':,'feature_percent':35}

        WR_PARAMS = {'loss':, 'learning_rate':, 'n_estimators':, 'max_depth':, 'min_samples_split':,
                    'max_features':,'subsample':,'gamelead':,'feature_percent':35}

        RB_PARAMS = {'loss':, 'learning_rate':, 'n_estimators':, 'max_depth':, 'min_samples_split':,
                    'max_features':,'subsample':,'gamelead':,'feature_percent':35}

        TE_PARAMS = {'loss':, 'learning_rate':, 'n_estimators':, 'max_depth':, 'min_samples_split':,
                    'max_features':,'subsample':,'gamelead':,'feature_percent':35}

        PK_PARAMS = {'loss':, 'learning_rate':, 'n_estimators':, 'max_depth':, 'min_samples_split':,
                    'max_features':,'subsample':,'gamelead':,'feature_percent':35}

        DEF_PARAMS = {'loss':, 'learning_rate':, 'n_estimators':, 'max_depth':, 'min_samples_split':,
                    'max_features':,'subsample':,'gamelead':,'feature_percent':35}

        return {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}

def getLRegParams(classification):
    if classification:
        #solver = ‘newton-cg’, ‘sag’ and ‘lbfgs’
        QB_PARAMS = {'fit_intercept':, 'intercept_scaling':, 'class_weight':, 'max_iter':, 'solver':, 
                    'tol':,'multi_class':,'gamelead':,'feature_percent':35}

        WR_PARAMS = {'fit_intercept':, 'intercept_scaling':, 'class_weight':, 'max_iter':, 'solver':, 
                    'tol':,'multi_class':,'gamelead':,'feature_percent':35}

        RB_PARAMS = {'fit_intercept':, 'intercept_scaling':, 'class_weight':, 'max_iter':, 'solver':, 
                    'tol':,'multi_class':,'gamelead':,'feature_percent':35}

        TE_PARAMS = {'fit_intercept':, 'intercept_scaling':, 'class_weight':, 'max_iter':, 'solver':, 
                    'tol':,'multi_class':,'gamelead':,'feature_percent':35}

        PK_PARAMS = {'fit_intercept':, 'intercept_scaling':, 'class_weight':, 'max_iter':, 'solver':, 
                    'tol':,'multi_class':,'gamelead':,'feature_percent':35}

        DEF_PARAMS = {'fit_intercept':, 'intercept_scaling':, 'class_weight':, 'max_iter':, 'solver':, 
                    'tol':,'multi_class':,'gamelead':,'feature_percent':35}

        return {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}
    else:
        QB_PARAMS = {'fit_intercept':, 'normalize':,'gamelead':,'feature_percent':35}

        WR_PARAMS = {'fit_intercept':, 'normalize':,'gamelead':,'feature_percent':35}

        RB_PARAMS = {'fit_intercept':, 'normalize':,'gamelead':,'feature_percent':35}

        TE_PARAMS = {'fit_intercept':, 'normalize':,'gamelead':,'feature_percent':35}

        PK_PARAMS = {'fit_intercept':, 'normalize':,'gamelead':,'feature_percent':35}

        DEF_PARAMS = {'fit_intercept':, 'normalize':,'gamelead':,'feature_percent':35}

        return {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}

def getModelParams(algo, classification):
    if algo == 'RF':
        return getRFParams(classification)
    if algo == 'GDBT':
        return getGDBTParams(classification)
    if algo == 'LReg':
        return getLRegParams(classification)