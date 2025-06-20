def appr_sup():
    import pandas as pd #oer caricare e manipolare dataset in formato tabellare
    import os   #per gestire directory, creare cartelle, salvare file
    import matplotlib.pyplot as plt #libreria base per visualizzazione di grafici
    from sklearn.model_selection import train_test_split, cross_val_score   #per suddividere i dati in training/test e per cross-validation
    from sklearn.preprocessing import MultiLabelBinarizer   #per trasformare etichette multilabel in codifica one-hot binaria
    from sklearn.metrics import make_scorer, accuracy_score, precision_score, recall_score, f1_score    #metriche di valutazione del modello
    from itertools import product   #permette di generare tutte le combinazioni possibili tra i valori degli iperparametri
    from sklearn.utils import resample  #per effettuare oversampling dei dati (duplicare la classe minoritaria)

    #moduli interni del progetto
    from config_parametri import get_parametri #restituisce un dizionario con i parametri da testare per ciascun modello
    from crea_modello import get_modelli #costruisce e restituisce un classificatore ML in base al nome e ai parametri specificati
    from valutazione_finale import valuta_modello_finale   #funzione per valutazione finale su test set con AdaBoost (utile per vedere tp,tn,fp,fn)
    
    #funzioni di plotting
    from grafici_modelli import plot_accuracy, plot_confusion_matrix, plot_bar_chart_naive_bayes, plot_radar_all_models  

    os.makedirs("PNG", exist_ok=True)

    #pre-processing del dataset
    df = pd.read_csv('DATASET/dataset_ml.csv')
    #elimina righe con voti assenti o nulli
    df = df[df['Punteggio_Utente'] > 0]

    #etichetta binaria: piace (1) se punteggio utente ≥ 7
    df['Piace'] = df['Punteggio_Utente'].apply(lambda x: 1 if x >= 7 else 0)
    
    #pulizia e codifica dei generi
    df['Generi'] = df['Generi'].fillna('').apply(lambda x: [g.strip().lower().replace(' ', '_') for g in x.split(',') if g])

    #per assegnare più generi contemporaneamente a un singolo esempio
    mlb = MultiLabelBinarizer()
    generi_encoded = pd.DataFrame(mlb.fit_transform(df['Generi']), columns=mlb.classes_, index=df.index)

    #costruzione matrice X (feature) e vettore y (target)
    X = pd.concat([generi_encoded, df[['Punteggio_Medio', 'Rank', 'Popolarita']]], axis=1).fillna(0)
    y = df['Piace']

    #suddivisione train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #bilanciamento del training set (oversampling)
    train_df = pd.concat([X_train, y_train], axis=1)
    #divide per classe
    minority = train_df[train_df['Piace'] == 1]
    majority = train_df[train_df['Piace'] == 0]

    #oversampling della classe minoritaria (ci sono pochi esempi con punteggio maggiore di 7)
    minority_upsampled = resample(minority, replace=True, n_samples=len(majority), random_state=42)

    #combina di nuovo
    train_balanced = pd.concat([majority, minority_upsampled])
    X_train = train_balanced.drop(columns='Piace')
    y_train = train_balanced['Piace']

    #configurazione dei modelli e parametri
    param_grid = get_parametri()
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

    #addestramento e valutazione di ciascun modello
    for model_name, param_grid_model in param_grid.items():
        print(f"\n{model_name}")
        train_acc, test_acc, labels = [], [], []

        #genera tutte le combinazioni di iperparametri
        keys, values = zip(*param_grid_model.items()) if param_grid_model else ([], [])
        combinations = [dict(zip(keys, v)) for v in product(*values)] if values else [{}]

        for combo in combinations:
            try:
                model = get_modelli(model_name, combo)
                model.fit(X_train, y_train)
                train_acc.append(model.score(X_train, y_train))
                test_acc.append(model.score(X_test, y_test))
                labels.append(str(combo))
            except Exception as e:
                print(f"Errore con i parametri {combo}: {e}")

        #plot accuracy se non è Naive Bayes
        if model_name != 'Naive Bayes':
            plot_accuracy(labels, train_acc, test_acc, model_name)

        #valutazione con Cross-Validation
        print(f"\n[Cross Validation]: {model_name}")
        model = get_modelli(model_name, default_params[model_name])
        acc_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        prec_scores = cross_val_score(model, X, y, cv=5, scoring=make_scorer(precision_score, zero_division=0))
        rec_scores  = cross_val_score(model, X, y, cv=5, scoring=make_scorer(recall_score, zero_division=0))
        f1_scores   = cross_val_score(model, X, y, cv=5, scoring=make_scorer(f1_score, zero_division=0))

        #stampa metriche fold per fold
        for i in range(5):
            print(f"    Fold {i+1}: Accuracy={acc_scores[i]:.3f} & Precision={prec_scores[i]:.3f} & Recall={rec_scores[i]:.3f} & F1={f1_scores[i]:.3f}")
            metrics = ['Accuracy', 'Precision', 'Recall', 'F1-score']
            values = [acc_scores[i], prec_scores[i], rec_scores[i], f1_scores[i]]
            plt.figure()
            plt.bar(metrics, values, color='lightblue')
            plt.ylim(0, 1)
            plt.title(f'{model_name} - Fold {i+1}')
            safe_name = model_name.replace(" ", "_").lower()
            plt.savefig(f'PNG/{safe_name}_fold_{i+1}.png')
            plt.close()

        #stampa media CV
        print(f"    Media Accuracy:  {acc_scores.mean():.3f} ± {acc_scores.std():.3f}")
        print(f"    Media Precision: {prec_scores.mean():.3f} ± {prec_scores.std():.3f}")
        print(f"    Media Recall:    {rec_scores.mean():.3f} ± {rec_scores.std():.3f}")
        print(f"    Media F1-score:  {f1_scores.mean():.3f} ± {f1_scores.std():.3f}")

        #salva dati per radar plot
        model_names.append(model_name)
        radar_data.append([acc_scores.mean(), prec_scores.mean(), rec_scores.mean(), f1_scores.mean()])

        #grafico a barre per Naive Bayes
        if model_name == 'Naive Bayes':
            plot_bar_chart_naive_bayes(['Accuracy', 'Precision', 'Recall', 'F1-score'],[acc_scores.mean(), prec_scores.mean(), rec_scores.mean(), f1_scores.mean()])

    #valutazione finale su test set con AdaBoost
    valuta_modello_finale(X_train, X_test, y_train, y_test)
    #radar plot finale per confronto modelli
    plot_radar_all_models(model_names, ['Accuracy', 'Precision', 'Recall', 'F1-score'], radar_data)