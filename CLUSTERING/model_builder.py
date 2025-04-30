# --- Import dei classificatori disponibili ---
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier   # Richiede il pacchetto xgboost

# --- Restituisce un modello ML in base al nome e ai parametri specificati ---
def get_model(name, params):
    if name == 'Decision Tree':
        # Classificatore ad albero di decisione con profondità fissata
        return DecisionTreeClassifier(max_depth=params['max_depth'], random_state=42)
    if name == 'Random Forest':
        # Foresta casuale con numero di alberi e profondità massima
        return RandomForestClassifier(n_estimators=params['n_estimators'], max_depth=params['max_depth'], random_state=42)
    if name == 'AdaBoost':
        # Boosting con numero di stimatori specificato
        return AdaBoostClassifier(n_estimators=params['n_estimators'], random_state=42)
    if name == 'KNN':
        # Classificatore basato su k-vicini
        return KNeighborsClassifier(n_neighbors=params['n_neighbors'])
    if name == 'Naive Bayes':
        # Classificatore di Bayes Gaussiano, non ha iperparametri da passare
        return GaussianNB()
    if name == 'XGBoost':
        # XGBoost con numero di stime e metrica di valutazione logloss
        return XGBClassifier(n_estimators=params['n_estimators'], eval_metric='logloss')
