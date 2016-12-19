def getModelParams():
    QB_PARAMS = {'n_estimators':500, 'max_depth':5, 'max_features':'log2',
                'min_samples_split':2,'feature_percent':70, 'gamelead':3,
                'class_weights':'balanced','bootstrap':True}

    WR_PARAMS = {'n_estimators':300, 'max_depth':5, 'max_features':'log2',
                'min_samples_split':2,'feature_percent':50, 'gamelead':3,
                'class_weights':'balanced','bootstrap':True}

    RB_PARAMS = {'n_estimators':400, 'max_depth':5, 'max_features':'log2',
                'min_samples_split':2,'feature_percent':30, 'gamelead':3,
                'class_weights':'balanced','bootstrap':True}

    TE_PARAMS = {'n_estimators':100, 'max_depth':5, 'max_features':'log2',
                'min_samples_split':2,'feature_percent':40, 'gamelead':3,
                'class_weights':'balanced','bootstrap':True}

    PK_PARAMS = {'n_estimators':400, 'max_depth':5, 'max_features':'log2',
                'min_samples_split':2,'feature_percent':60, 'gamelead':3,
                'class_weights':'balanced','bootstrap':True}

    DEF_PARAMS = {'n_estimators':200, 'max_depth':5, 'max_features':'log2',
                'min_samples_split':2,'feature_percent':80, 'gamelead':3,
                'class_weights':'balanced','bootstrap':True}

    return {'RB':RB_PARAMS, 'WR': WR_PARAMS, 'TE':TE_PARAMS, 'QB':QB_PARAMS, 'PK':PK_PARAMS, 'Def':DEF_PARAMS}
