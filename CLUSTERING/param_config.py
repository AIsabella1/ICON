
def get_param_grid():
    return {
        'Decision Tree': {'max_depth': range(1, 11)},
        'Random Forest': {'n_estimators': range(100, 601, 100), 'max_depth': [3, 5, 7]},
        'AdaBoost': {'n_estimators': range(50, 301, 50)},
        'KNN': {'n_neighbors': range(1, 11)},
        'Naive Bayes': {},  # nessun iperparametro da ottimizzare
        'XGBoost': {'n_estimators': range(50, 301, 50)}
    }
