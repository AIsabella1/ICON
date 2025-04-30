
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier

def get_model(name, params):
    if name == 'Decision Tree':
        return DecisionTreeClassifier(max_depth=params['max_depth'], random_state=42)
    if name == 'Random Forest':
        return RandomForestClassifier(n_estimators=params['n_estimators'], max_depth=params['max_depth'], random_state=42)
    if name == 'AdaBoost':
        return AdaBoostClassifier(n_estimators=params['n_estimators'], random_state=42)
    if name == 'KNN':
        return KNeighborsClassifier(n_neighbors=params['n_neighbors'])
    if name == 'Naive Bayes':
        return GaussianNB()
    if name == 'XGBoost':
        return XGBClassifier(n_estimators=params['n_estimators'], eval_metric='logloss')
