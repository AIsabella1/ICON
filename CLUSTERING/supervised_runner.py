
def run_supervised():
    import pandas as pd
    import os
    import matplotlib.pyplot as plt
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import MultiLabelBinarizer
    from sklearn.metrics import make_scorer, accuracy_score, precision_score, recall_score, f1_score
    from param_config import get_param_grid
    from model_builder import get_model
    from plot_tools import plot_accuracy, plot_confusion_matrix, plot_bar_chart_naive_bayes, plot_radar_all_models
    from report_utils import evaluate_final_model

    os.makedirs("PNG", exist_ok=True)

    df = pd.read_csv('DATASET/dataset_ml.csv')
    df = df[df['Punteggio_Utente'] > 0]
    df['Piace'] = df['Punteggio_Utente'].apply(lambda x: 1 if x >= 7 else 0)
    df['Generi'] = df['Generi'].fillna('').apply(lambda x: [g.strip().lower().replace(' ', '_') for g in x.split(',') if g])

    mlb = MultiLabelBinarizer()
    generi_encoded = pd.DataFrame(mlb.fit_transform(df['Generi']), columns=mlb.classes_, index=df.index)
    X = pd.concat([generi_encoded, df[['Punteggio_Medio', 'Rank', 'Popolarita']]], axis=1).fillna(0)
    y = df['Piace']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

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

    for model_name, params in param_grid.items():
        print(f"\n--- {model_name} ---")
        train_acc, test_acc, labels = [], [], []

        if model_name == 'Decision Tree':
            for depth in params['max_depth']:
                model = get_model(model_name, {'max_depth': depth})
                model.fit(X_train, y_train)
                train_acc.append(model.score(X_train, y_train))
                test_acc.append(model.score(X_test, y_test))
                labels.append(depth)

        elif model_name == 'Random Forest':
            for n in params['n_estimators']:
                for d in params['max_depth']:
                    model = get_model(model_name, {'n_estimators': n, 'max_depth': d})
                    model.fit(X_train, y_train)
                    train_acc.append(model.score(X_train, y_train))
                    test_acc.append(model.score(X_test, y_test))
                    labels.append(f"{n}|{d}")

        elif model_name == 'AdaBoost':
            for n in params['n_estimators']:
                model = get_model(model_name, {'n_estimators': n})
                model.fit(X_train, y_train)
                train_acc.append(model.score(X_train, y_train))
                test_acc.append(model.score(X_test, y_test))
                labels.append(n)

        elif model_name == 'KNN':
            for k in params['n_neighbors']:
                model = get_model(model_name, {'n_neighbors': k})
                model.fit(X_train, y_train)
                train_acc.append(model.score(X_train, y_train))
                test_acc.append(model.score(X_test, y_test))
                labels.append(k)

        elif model_name == 'XGBoost':
            for n in params['n_estimators']:
                model = get_model(model_name, {'n_estimators': n})
                model.fit(X_train, y_train)
                train_acc.append(model.score(X_train, y_train))
                test_acc.append(model.score(X_test, y_test))
                labels.append(n)

        if model_name != 'Naive Bayes':
            plot_accuracy(labels, train_acc, test_acc, model_name)

        print(f"\n[CV] Inizio valutazione: {model_name}")
        model = get_model(model_name, default_params[model_name])
        acc_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        prec_scores = cross_val_score(model, X, y, cv=5, scoring=make_scorer(precision_score, zero_division=0))
        rec_scores  = cross_val_score(model, X, y, cv=5, scoring=make_scorer(recall_score, zero_division=0))
        f1_scores   = cross_val_score(model, X, y, cv=5, scoring=make_scorer(f1_score, zero_division=0))

        for i in range(5):
            print(f"    Fold {i+1}: Accuracy={acc_scores[i]:.3f} | Precision={prec_scores[i]:.3f} | Recall={rec_scores[i]:.3f} | F1={f1_scores[i]:.3f}")
            # salva bar chart del fold
            metrics = ['Accuracy', 'Precision', 'Recall', 'F1-score']
            values = [acc_scores[i], prec_scores[i], rec_scores[i], f1_scores[i]]
            plt.figure()
            plt.bar(metrics, values, color='lightblue')
            plt.ylim(0, 1)
            plt.title(f'{model_name} - Fold {i+1}')
            safe_name = model_name.replace(" ", "_").lower()
            plt.savefig(f'PNG/{safe_name}_fold_{i+1}.png')
            plt.close()

        print(f"    Media Accuracy:  {acc_scores.mean():.3f}")
        print(f"    Media Precision: {prec_scores.mean():.3f}")
        print(f"    Media Recall:    {rec_scores.mean():.3f}")
        print(f"    Media F1-score:  {f1_scores.mean():.3f}")

        model_names.append(model_name)
        radar_data.append([acc_scores.mean(), prec_scores.mean(), rec_scores.mean(), f1_scores.mean()])

        if model_name == 'Naive Bayes':
            plot_bar_chart_naive_bayes(['Accuracy', 'Precision', 'Recall', 'F1-score'],
                                       [acc_scores.mean(), prec_scores.mean(), rec_scores.mean(), f1_scores.mean()])

    evaluate_final_model(X_train, X_test, y_train, y_test)
    plot_radar_all_models(model_names, ['Accuracy', 'Precision', 'Recall', 'F1-score'], radar_data)
