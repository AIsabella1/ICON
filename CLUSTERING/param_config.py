# --- Definizione della funzione che restituisce i parametri da testare per ogni modello ---
def get_param_grid():
    return {
        # Decision Tree: modello semplice, suscettibile all'overfitting
        'Decision Tree': {
            'max_depth': [3, 4, 5],                   # Limita la profondità per ridurre la complessità del modello
            'min_samples_leaf': [10, 20],             # Impone una dimensione minima alle foglie → evita splitting su pochi dati
            'class_weight': ['balanced']              # Pesa le classi in base alla loro frequenza per gestire sbilanciamenti
        },

        # Random Forest: ensemble di alberi → rischio di overfitting su dataset piccoli
        'Random Forest': {
            'n_estimators': [100, 300],               # Numero di alberi nella foresta: più alberi = maggiore stabilità
            'max_depth': [4, 6],                      # Controlla la profondità di ogni albero → meno overfitting
            'min_samples_leaf': [10, 20],             # Stessa logica del Decision Tree
            'max_features': ['sqrt', 'log2'],         # Limita il numero di feature per split → diversifica gli alberi
            'class_weight': ['balanced']              # Aiuta con dataset sbilanciati, migliora il recall
        },

        # AdaBoost: boosting adattivo, rischio di overfitting se troppi stimatori o learning rate alto
        'AdaBoost': {
            'n_estimators': [50, 100],                # Numero di stadi di boosting
            'learning_rate': [0.05, 0.1, 0.5]         # Tasso di aggiornamento: valori bassi aiutano a ridurre l’overfitting
        },

        # K-Nearest Neighbors: modello non parametrico, sensibile a rumore e scala delle feature
        'KNN': {
            'n_neighbors': [7, 9, 11]                 # Valori medi di k rendono il modello più robusto e meno soggetto ad overfitting
        },

        # Naive Bayes: modello semplice, non necessita di tuning
        'Naive Bayes': {},               # Nessun iperparametro da ottimizzare

        # XGBoost: potente ma incline all’overfitting se non regolato
        'XGBoost': {
            'n_estimators': [50, 100],                # Numero di boosting rounds
            'max_depth': [3, 4],                      # Profondità bassa = generalizzazione migliore
            'learning_rate': [0.05, 0.1],             # Learning rate basso = aggiornamenti più stabili
            'subsample': [0.7],                       # Percentuale di dati usata in ogni boosting round
            'colsample_bytree': [0.7],                # Percentuale di feature usate per albero → diversificazione
            'reg_alpha': [1],                         # Regolarizzazione L1 → promuove la sparsità
            'reg_lambda': [1],                        # Regolarizzazione L2 → penalizza pesi grandi
            'scale_pos_weight': [1.5]                 # Pesa di più la classe minoritaria (utile in dataset sbilanciati)
        }
    }
