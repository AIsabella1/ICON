# Import delle librerie
import matplotlib.pyplot as plt   # Per creare grafici e visualizzare la matrice di confusione
import seaborn as sns             # Per grafici avanzati con estetica migliorata (es. heatmap)
from sklearn.metrics import classification_report, confusion_matrix  # Classification_report: fornisce precision, recall, F1-score per ogni classe. Confusion_matrix: crea una tabella con i conteggi delle predizioni corrette/sbagliate
from sklearn.ensemble import AdaBoostClassifier  # Algoritmo di boosting che combina classificatori deboli per creare un classificatore forte

# Funzione per addestrare e valutare AdaBoost su un dataset
def evaluate_final_model(X_train, X_test, y_train, y_test):
    # 1. Inizializza il classificatore AdaBoost con 100 stimatori deboli
    model = AdaBoostClassifier(n_estimators=100, random_state=42)
    
    # 2. Addestra il modello sul training set
    model.fit(X_train, y_train)

    # 3. Predice le classi sul test set
    y_pred = model.predict(X_test)

    # 4. Stampa il classification report: precision, recall, F1-score per ciascuna classe
    print("\n--- Classification Report (AdaBoost n=100) ---")
    print(classification_report(y_test, y_pred))

    # 5. Crea la matrice di confusione come heatmap
    plt.figure(figsize=(6,4))
    sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues')
    plt.title("Confusion Matrix - AdaBoost")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()

    # 6. Salva la matrice di confusione nella cartella PNG
    plt.savefig('PNG/confusion_matrix_adaboost.png')
