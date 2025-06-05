# Import dei classificatori disponibili
from sklearn.tree import DecisionTreeClassifier # Algoritmo ad albero decisionale. Utile per modelli semplici.
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier # RandomForest: ensemble di alberi decisionali (bagging). AdaBoost: algoritmo di boosting adattivo per migliorare classificatori deboli.
from sklearn.neighbors import KNeighborsClassifier # KNN: classifica in base alla vicinanza con i k esempi più simili nel dataset.
from sklearn.naive_bayes import GaussianNB # Classificatore probabilistico basato su teorema di Bayes, adatto per dati continui e indipendenti.
from xgboost import XGBClassifier   # XGBoost: potente algoritmo di boosting basato su gradienti. Richiede il pacchetto `xgboost` installato separatamente.

# Ritorna un modello ML configurato in base al nome e ai parametri
def get_model(name, params):
    if name == 'Decision Tree':
        # Albero decisionale con controllo su profondità massima e numero minimo di campioni per foglia
        return DecisionTreeClassifier(
            max_depth=params['max_depth'],
            min_samples_leaf=params.get('min_samples_leaf', 5),
            random_state=42
        )
    if name == 'Random Forest':
        # Random Forest con numero di alberi, profondità e foglie minime specificabili
        return RandomForestClassifier(
            n_estimators=params['n_estimators'],
            max_depth=params['max_depth'],
            min_samples_leaf=params.get('min_samples_leaf', 5),
            random_state=42
        )
    if name == 'AdaBoost':
        # AdaBoost con numero di stime e learning rate (default: 1.0)
        return AdaBoostClassifier(
            n_estimators=params['n_estimators'],
            learning_rate=params.get('learning_rate', 1.0),
            random_state=42
        )
    if name == 'KNN':
        # K-Nearest Neighbors con numero di vicini specificato
        return KNeighborsClassifier(n_neighbors=params['n_neighbors'])
    if name == 'Naive Bayes':
        # Gaussian Naive Bayes non ha parametri iperconfigurabili
        return GaussianNB()
    if name == 'XGBoost':
        # Classificatore XGBoost con supporto per tuning: numero stimatori, profondità, learning rate
        return XGBClassifier(
            n_estimators=params['n_estimators'],
            max_depth=params.get('max_depth', 3),
            learning_rate=params.get('learning_rate', 0.1),
            eval_metric='logloss' # evita warning: XGBoost richiede esplicitare la metrica
        )