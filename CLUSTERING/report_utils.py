# --- Import delle librerie ---
import matplotlib.pyplot as plt  # Per visualizzare la matrice di confusione
import seaborn as sns            # Per visualizzazioni con heatmap
from sklearn.metrics import classification_report, confusion_matrix  # Metriche di valutazione
from sklearn.ensemble import AdaBoostClassifier  # Modello di boosting

# --- Funzione per addestrare e valutare AdaBoost su un dataset ---
def evaluate_final_model(X_train, X_test, y_train, y_test):
    # Inizializza il classificatore AdaBoost con 100 stimatori
    model = AdaBoostClassifier(n_estimators=100, random_state=42)
    
    # Addestramento del modello
    model.fit(X_train, y_train)

    # Predizioni sul set di test
    y_pred = model.predict(X_test)

    # Stampa report dettagliato con precision, recall, f1-score
    print("\n--- Classification Report (AdaBoost n=100) ---")
    print(classification_report(y_test, y_pred))

    # Visualizza matrice di confusione con annotazioni
    plt.figure(figsize=(6,4))
    sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues')
    plt.title("Confusion Matrix - AdaBoost")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()

    # Salva la figura nella cartella PNG
    plt.savefig('PNG/confusion_matrix_adaboost.png')
