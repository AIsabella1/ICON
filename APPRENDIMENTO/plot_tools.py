# Librerie per visualizzazione
import matplotlib.pyplot as plt  # Matplotlib è usata per creare grafici statici (linee, barre, radar, ecc.)
import seaborn as sns            # Seaborn migliora lo stile grafico ed è ideale per heatmap, scatterplot, ecc.
import os                        # Gestione delle cartelle e percorsi
from sklearn.metrics import confusion_matrix  # Calcolo della matrice di confusione per classificazione

# Crea la cartella dove verranno salvati i grafici se non esiste
OUTPUT_DIR = "PNG"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Line plot per confrontare accuracy su train e test in base alle combinazioni di parametri
def plot_accuracy(labels, train_acc, test_acc, model_name):
    plt.figure(figsize=(10, 5))
    plt.plot(labels, train_acc, marker='o', label='Train Accuracy')
    plt.plot(labels, test_acc, marker='s', label='Test Accuracy')
    plt.title(f'Accuracy for {model_name}')
    plt.xlabel('Param combinations')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, f"{model_name.lower().replace(' ', '_')}_accuracy_plot.png"))
    plt.close()

# Visualizza la matrice di confusione come heatmap
def plot_confusion_matrix(y_true, y_pred, model_name="Model"):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'Confusion Matrix - {model_name}')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.savefig(os.path.join(OUTPUT_DIR, f"{model_name.lower().replace(' ', '_')}_confusion_matrix.png"))
    plt.close()

# Visualizza le metriche del Naive Bayes (Accuracy, Precision, Recall, F1...) in un grafico a barre
def plot_bar_chart_naive_bayes(metrics, values):
    plt.figure(figsize=(8, 5))
    plt.bar(metrics, values, color='skyblue')
    plt.title("Naive Bayes - Performance Metrics")
    plt.ylim(0, 1)
    plt.ylabel("Score")
    plt.grid(axis='y')
    plt.savefig(os.path.join(OUTPUT_DIR, "naive_bayes_bar_chart.png"))
    plt.close()

# Radar plot per confrontare più modelli supervisionati su più metriche
def plot_radar_all_models(model_names, metric_labels, data, output_dir="PNG"):
    import numpy as np
    import matplotlib.pyplot as plt
    import os

    os.makedirs(output_dir, exist_ok=True)
    angles = np.linspace(0, 2 * np.pi, len(metric_labels), endpoint=False).tolist()
    angles += angles[:1]    # chiude il cerchio per il radar plot

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    for i, model in enumerate(model_names):
        values = data[i]
        values += values[:1]    # chiude il cerchio per ogni modello
        ax.plot(angles, values, label=model)
        ax.fill(angles, values, alpha=0.1)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), metric_labels)
    ax.set_ylim(0, 1)
    plt.title("Radar Plot - Confronto Modelli Supervisionati")
    plt.legend(loc='lower right', bbox_to_anchor=(1.3, 0.1))
    plt.tight_layout()
    path = os.path.join(output_dir, "radar_plot_supervisionati.png")
    plt.savefig(path)
    plt.close()