#ho sfruttato le seguenti librerie per implementare i vari classificatori
from sklearn.tree import DecisionTreeClassifier #algoritmo ad albero decisionale
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier #RandomForest: ensemble di alberi decisionali, AdaBoost: algoritmo di boosting
from sklearn.neighbors import KNeighborsClassifier #KNN classifica in base ai k esempi più simili nel dataset
from sklearn.naive_bayes import GaussianNB #classificatore probabilistico (basato sul teorema di Bayes)
from xgboost import XGBClassifier   #XGBoost algoritmo di boosting basato su gradienti

#ritorna un modello ML configurato in base al nome e ai parametri
def get_modelli(name, params):
    if name == 'Decision Tree':
        #albero decisionale con controllo su profondità massima e numero minimo di campioni per foglia
        return DecisionTreeClassifier(max_depth=params['max_depth'],min_samples_leaf=params.get('min_samples_leaf', 5),random_state=42)
    if name == 'Random Forest':
        #RandomForest con numero di alberi, profondità e foglie minime specificabili
        return RandomForestClassifier(n_estimators=params['n_estimators'],max_depth=params['max_depth'],min_samples_leaf=params.get('min_samples_leaf', 5),random_state=42)
    if name == 'AdaBoost':
        #AdaBoost con numero di stime e learning rate
        return AdaBoostClassifier(n_estimators=params['n_estimators'],learning_rate=params.get('learning_rate', 1.0),random_state=42)
    if name == 'KNN':
        #KNN con numero di vicini specificato
        return KNeighborsClassifier(n_neighbors=params['n_neighbors'])
    if name == 'Naive Bayes':
        #Gaussian Naive Bayes non ha parametri essendo probabilistico
        return GaussianNB()
    if name == 'XGBoost':
        #XGBoost con numero stimatori, profondità, learning rate
        return XGBClassifier(n_estimators=params['n_estimators'],max_depth=params.get('max_depth', 3),learning_rate=params.get('learning_rate', 0.1),eval_metric='logloss')