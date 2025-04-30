# --- Definizione della funzione che restituisce i parametri da testare per ogni modello ---
def get_param_grid():
    return {
        'Decision Tree': {'max_depth': range(1, 11)},   # DecisionTreeClassifier: prova profondità da 1 a 10
        'Random Forest': {'n_estimators': range(100, 601, 100), 'max_depth': [3, 5, 7]},    # Numero di alberi: 100, 200, ..., 600 e profondità massima dell'albero
        'AdaBoost': {'n_estimators': range(50, 301, 50)},   # Numero di stime deboli: da 50 a 300
        'KNN': {'n_neighbors': range(1, 11)},   # Numero di vicini: da 1 a 10
        'Naive Bayes': {},  # Nessun iperparametro da ottimizzare per GaussianNB
        'XGBoost': {'n_estimators': range(50, 301, 50)} # Numero di alberi (boosting rounds)
    }
