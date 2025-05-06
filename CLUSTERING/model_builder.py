# --- Import dei classificatori disponibili ---
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier   # Richiede il pacchetto xgboost

# --- Restituisce un modello ML in base al nome e ai parametri specificati ---
def get_model(name, params):
    if name == 'Decision Tree':
        # Classificatore ad albero di decisione con profondità e foglie minime
        return DecisionTreeClassifier(
            max_depth=params['max_depth'],
            min_samples_leaf=params.get('min_samples_leaf', 5),
            random_state=42
        )
    if name == 'Random Forest':
        # Foresta casuale con parametri di regolarizzazione
        return RandomForestClassifier(
            n_estimators=params['n_estimators'],
            max_depth=params['max_depth'],
            min_samples_leaf=params.get('min_samples_leaf', 5),
            random_state=42
        )
    if name == 'AdaBoost':
        # Boosting con learning rate regolabile
        return AdaBoostClassifier(
            n_estimators=params['n_estimators'],
            learning_rate=params.get('learning_rate', 1.0),
            random_state=42
        )
    if name == 'KNN':
        # Classificatore basato su k-vicini
        return KNeighborsClassifier(n_neighbors=params['n_neighbors'])
    if name == 'Naive Bayes':
        # Classificatore di Bayes Gaussiano, non ha iperparametri da passare
        return GaussianNB()
    if name == 'XGBoost':
        # XGBoost con iperparametri di regolarizzazione
        return XGBClassifier(
            n_estimators=params['n_estimators'],
            max_depth=params.get('max_depth', 3),
            learning_rate=params.get('learning_rate', 0.1),
            eval_metric='logloss'
        )
