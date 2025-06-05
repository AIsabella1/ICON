# Esegue la pipeline completa di apprendimento supervisionato
def run_supervised():
    # Import delle librerie
    import pandas as pd # Per caricare e manipolare dataset in formato tabellare (CSV, DataFrame)
    import os   # Per gestire directory, creare cartelle, salvare file
    import matplotlib.pyplot as plt # Libreria base per visualizzazione di grafici (linee, barre, scatter)
    from sklearn.model_selection import train_test_split, cross_val_score   # Per suddividere i dati in training/test e per effettuare cross-validation
    from sklearn.preprocessing import MultiLabelBinarizer   # Per trasformare etichette multilabel (es. liste di generi) in codifica one-hot binaria
    from sklearn.metrics import make_scorer, accuracy_score, precision_score, recall_score, f1_score    # Metriche di valutazione del modello (con `make_scorer` per usarle in cross-validation)
    from itertools import product   # Permette di generare tutte le combinazioni possibili tra i valori degli iperparametri (es. grid search manuale)
    from sklearn.utils import resample  # Per effettuare oversampling dei dati (es. duplicare la classe minoritaria)

    # Import moduli interni del progetto
    from param_config import get_param_grid # Restituisce un dizionario con i parametri da testare per ciascun modello (griglie iperparametri)
    from model_builder import get_model # Costruisce e restituisce un classificatore ML in base al nome e ai parametri specificati
    from report_utils import evaluate_final_model   # Funzione per valutazione finale su test set con AdaBoost (include confusion matrix)
    
    # Funzioni di plotting:
    #    - plot_accuracy: linea con performance su train/test
    #    - plot_confusion_matrix: heatmap di predizioni
    #    - plot_bar_chart_naive_bayes: bar chart delle metriche per Naive Bayes
    #    - plot_radar_all_models: radar chart per confronto tra modelli
    from plot_tools import plot_accuracy, plot_confusion_matrix, plot_bar_chart_naive_bayes, plot_radar_all_models  

    os.makedirs("PNG", exist_ok=True)   # Crea cartella per immagini se non esiste

    # Pre-processing del dataset
    df = pd.read_csv('DATASET/dataset_ml.csv')
    df = df[df['Punteggio_Utente'] > 0] # Elimina righe con voti assenti o nulli

    # Etichetta binaria: piace (1) se punteggio utente ≥ 7
    df['Piace'] = df['Punteggio_Utente'].apply(lambda x: 1 if x >= 7 else 0)
    
    # Pulizia e codifica dei generi
    df['Generi'] = df['Generi'].fillna('').apply(lambda x: [g.strip().lower().replace(' ', '_') for g in x.split(',') if g])

    mlb = MultiLabelBinarizer()
    generi_encoded = pd.DataFrame(mlb.fit_transform(df['Generi']), columns=mlb.classes_, index=df.index)

    # Costruzione matrice X (feature) e vettore y (target)
    X = pd.concat([generi_encoded, df[['Punteggio_Medio', 'Rank', 'Popolarita']]], axis=1).fillna(0)
    y = df['Piace']

    # Suddivisione train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Bilanciamento del training set (oversampling classe minoritaria)  
    train_df = pd.concat([X_train, y_train], axis=1)
    # Dividi per classe
    minority = train_df[train_df['Piace'] == 1]
    majority = train_df[train_df['Piace'] == 0]

    # Oversampling della classe minoritaria
    minority_upsampled = resample(minority, replace=True, n_samples=len(majority), random_state=42)

    # Combina di nuovo
    train_balanced = pd.concat([majority, minority_upsampled])
    X_train = train_balanced.drop(columns='Piace')
    y_train = train_balanced['Piace']

    # Configurazione dei modelli e parametri
    param_grid = get_param_grid()
    default_params = {
        'Decision Tree': {'max_depth': 5},
        'Random Forest': {'n_estimators': 300, 'max_depth': 5},
        'AdaBoost': {'n_estimators': 100},
        'KNN': {'n_neighbors': 5},
        'Naive Bayes': {},
        'XGBoost': {'n_estimators': 100}
    }

    model_names = []
    radar_data = []

    # Addestramento e valutazione di ciascun modello
    for model_name, param_grid_model in param_grid.items():
        print(f"\n--- {model_name} ---")
        train_acc, test_acc, labels = [], [], []

        # Genera tutte le combinazioni di iperparametri
        keys, values = zip(*param_grid_model.items()) if param_grid_model else ([], [])
        combinations = [dict(zip(keys, v)) for v in product(*values)] if values else [{}]

        for combo in combinations:
            try:
                model = get_model(model_name, combo)
                model.fit(X_train, y_train)
                train_acc.append(model.score(X_train, y_train))
                test_acc.append(model.score(X_test, y_test))
                labels.append(str(combo))
            except Exception as e:
                print(f"Errore con i parametri {combo}: {e}")

        # Plot accuracy se non è Naive Bayes
        if model_name != 'Naive Bayes':
            plot_accuracy(labels, train_acc, test_acc, model_name)

        # Valutazione con Cross-Validation
        print(f"\n[CV] Inizio valutazione: {model_name}")
        model = get_model(model_name, default_params[model_name])
        acc_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        prec_scores = cross_val_score(model, X, y, cv=5, scoring=make_scorer(precision_score, zero_division=0))
        rec_scores  = cross_val_score(model, X, y, cv=5, scoring=make_scorer(recall_score, zero_division=0))
        f1_scores   = cross_val_score(model, X, y, cv=5, scoring=make_scorer(f1_score, zero_division=0))

        # Stampa metriche fold per fold
        for i in range(5):
            print(f"    Fold {i+1}: Accuracy={acc_scores[i]:.3f} | Precision={prec_scores[i]:.3f} | Recall={rec_scores[i]:.3f} | F1={f1_scores[i]:.3f}")
            metrics = ['Accuracy', 'Precision', 'Recall', 'F1-score']
            values = [acc_scores[i], prec_scores[i], rec_scores[i], f1_scores[i]]
            plt.figure()
            plt.bar(metrics, values, color='lightblue')
            plt.ylim(0, 1)
            plt.title(f'{model_name} - Fold {i+1}')
            safe_name = model_name.replace(" ", "_").lower()
            plt.savefig(f'PNG/{safe_name}_fold_{i+1}.png')
            plt.close()

        # Stampa media CV
        print(f"    Media Accuracy:  {acc_scores.mean():.3f}")
        print(f"    Media Precision: {prec_scores.mean():.3f}")
        print(f"    Media Recall:    {rec_scores.mean():.3f}")
        print(f"    Media F1-score:  {f1_scores.mean():.3f}")

        # Salva dati per radar plot
        model_names.append(model_name)
        radar_data.append([acc_scores.mean(), prec_scores.mean(), rec_scores.mean(), f1_scores.mean()])

        # Grafico a barre per Naive Bayes
        if model_name == 'Naive Bayes':
            plot_bar_chart_naive_bayes(['Accuracy', 'Precision', 'Recall', 'F1-score'],[acc_scores.mean(), prec_scores.mean(), rec_scores.mean(), f1_scores.mean()])

    # Valutazione finale su test set con AdaBoost
    evaluate_final_model(X_train, X_test, y_train, y_test)
    # Radar plot finale per confronto modelli
    plot_radar_all_models(model_names, ['Accuracy', 'Precision', 'Recall', 'F1-score'], radar_data)
