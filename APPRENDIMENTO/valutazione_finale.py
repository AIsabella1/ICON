import matplotlib.pyplot as plt   #per creare grafici e visualizzare la matrice di confusione
import seaborn as sns             #per grafici avanzati con estetica migliorata
from sklearn.metrics import classification_report, confusion_matrix  #classification_repor fornisce precision, recall, F1-score per ogni classe. confusion_matrix crea una tabella con i conteggi delle predizioni corrette/sbagliate
from sklearn.ensemble import AdaBoostClassifier  #algoritmo di boosting che combina classificatori deboli per creare un classificatore forte

#funzione per addestrare e valutare AdaBoost su un dataset
def valuta_modello_finale(X_train, X_test, y_train, y_test):
    #inizializza AdaBoost con 100 stimatori deboli
    model = AdaBoostClassifier(n_estimators=100, random_state=42)
    
    #addestra il modello sul training set
    model.fit(X_train, y_train)

    #predice le classi sul test set
    y_pred = model.predict(X_test)

    #stampa precision, recall, F1-score per ciascuna classe
    print("\nClassification Report (AdaBoost n=100)")
    print(classification_report(y_test, y_pred))

    #crea la matrice di confusione
    plt.figure(figsize=(6,4))
    sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues')
    plt.title("Confusion Matrix - AdaBoost")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()

    #salva la matrice di confusione nella cartella PNG
    plt.savefig('PNG/confusion_matrix_adaboost.png')