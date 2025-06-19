#tutte le configurazioni sono state ottenute dopo molti test in cui era presente l'overfitting, sono stati testate molte versioni, reputo che questa versione sia efficace.
#altre configurazioni sono state ottenute da vari tutorial trovati su internet.

#funzione che restituisce i parametri da testare per ogni modello
def get_parametri():
    return {
        'Decision Tree': {
            #limita la profondità per ridurre la complessità del modello
            'max_depth': [4, 6, 8, 10],
            #impone una dimensione minima alle foglie, utile per evitare splitting su pochi dati     
            'min_samples_leaf': [1, 5, 10],
            #pesa le classi in base alla loro frequenza per gestire sbilanciamenti           
            'class_weight': ['balanced']
        },

        #rischio di overfitting su dataset piccoli
        'Random Forest': {
            #numero di alberi nella foresta, più alberi ovvero maggiore stabilità
            'n_estimators': [100, 300, 500],
            #controlla la profondità di ogni albero ovvero meno overfitting
            'max_depth': [6, 10, 12],
            #uguale al Decision Tree
            'min_samples_leaf': [1, 5, 10],
            #limita il numero di feature per split, diversifica gli alberi
            'max_features': ['sqrt', 'log2', None],
            #aiuta con dataset sbilanciati, migliora il recall
            'class_weight': ['balanced']
        },

        #rischio di overfitting se troppi stimatori o learning rate alto
        'AdaBoost': {
            #numero di stadi di boosting
            'n_estimators': [50, 100, 200],
            #tasso di aggiornamento: valori bassi aiutano a ridurre l’overfitting
            'learning_rate': [0.05, 0.1, 0.3, 0.5, 1.0]
        },

        #sensibile a rumore e scala delle feature
        'KNN': {
            #valori medi di k rendono il modello più robusto e meno soggetto ad overfitting
            'n_neighbors': [3, 5, 7, 9, 11, 15, 21]
        },

        #non ha iperparamentri configurabili essendo probabilistico
        'Naive Bayes': {},

        #incline all’overfitting se non regolato
        'XGBoost': {
            #numero di boosting rounds
            'n_estimators': [100, 300],
            #profondità bassa ovvero generalizzazione migliore
            'max_depth': [3, 5, 7],
            #learning rate basso ovvero aggiornamenti più stabili
            'learning_rate': [0.05, 0.1, 0.3],
            #percentuale di dati usata in ogni boosting round         
            'subsample': [0.7, 0.9, 1.0],
            #prcentuale di feature usate per albero implica diversificazione
            'colsample_bytree': [0.7, 1.0],
            #regolarizzazione L1 promuove la sparsità
            'reg_alpha': [0, 1],
            #regolarizzazione L2 penalizza pesi grandi
            'reg_lambda': [1],
            #pesa di più la classe minoritaria (per dataset sbilanciati)
            'scale_pos_weight': [1, 1.5]
        }
    }