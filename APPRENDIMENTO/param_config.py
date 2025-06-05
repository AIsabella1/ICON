# Definizione della funzione che restituisce i parametri da testare per ogni modello
def get_param_grid():
    return {
        # Decision Tree: modello semplice, suscettibile all'overfitting
        'Decision Tree': {
            'max_depth': [4, 6, 8, 10],                 # Limita la profondità per ridurre la complessità del modello
            'min_samples_leaf': [1, 5, 10],             # Impone una dimensione minima alle foglie => evita splitting su pochi dati
            'class_weight': ['balanced']                # Pesa le classi in base alla loro frequenza per gestire sbilanciamenti
        },

        # Random Forest: ensemble di alberi => rischio di overfitting su dataset piccoli
        'Random Forest': {
            'n_estimators': [100, 300, 500],            # Numero di alberi nella foresta: più alberi = maggiore stabilità
            'max_depth': [6, 10, 12],                   # Controlla la profondità di ogni albero => meno overfitting
            'min_samples_leaf': [1, 5, 10],             # Stessa logica del Decision Tree
            'max_features': ['sqrt', 'log2', None],     # Limita il numero di feature per split => diversifica gli alberi
            'class_weight': ['balanced']                # Aiuta con dataset sbilanciati, migliora il recall
        },

        # AdaBoost: boosting adattivo, rischio di overfitting se troppi stimatori o learning rate alto
        'AdaBoost': {
            'n_estimators': [50, 100, 200],             # Numero di stadi di boosting
            'learning_rate': [0.05, 0.1, 0.3, 0.5, 1.0] # Tasso di aggiornamento: valori bassi aiutano a ridurre l’overfitting
        },

        # K-Nearest Neighbors: modello non parametrico, sensibile a rumore e scala delle feature
        'KNN': {
            'n_neighbors': [3, 5, 7, 9, 11, 15, 21]     # Valori medi di k rendono il modello più robusto e meno soggetto ad overfitting
        },

        # Naive Bayes: modello semplice, non necessita di tuning
        'Naive Bayes': {},                              # Nessun iperparametro da ottimizzare

        # XGBoost: potente ma incline all’overfitting se non regolato
        'XGBoost': {
            'n_estimators': [100, 300],                 # Numero di boosting rounds
            'max_depth': [3, 5, 7],                     # Profondità bassa = generalizzazione migliore
            'learning_rate': [0.05, 0.1, 0.3],          # Learning rate basso = aggiornamenti più stabili
            'subsample': [0.7, 0.9, 1.0],               # Percentuale di dati usata in ogni boosting round
            'colsample_bytree': [0.7, 1.0],             # Percentuale di feature usate per albero => diversificazione
            'reg_alpha': [0, 1],                        # Regolarizzazione L1 => promuove la sparsità
            'reg_lambda': [1],                          # Regolarizzazione L2 => penalizza pesi grandi
            'scale_pos_weight': [1, 1.5]                # Pesa di più la classe minoritaria (utile in dataset sbilanciati)
        }
    }
