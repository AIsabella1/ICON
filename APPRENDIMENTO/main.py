# Importa i moduli principali per l'analisi del progetto
from supervised_runner import run_supervised            # Classificazione supervisionata
from clustering_runner import run_clustering            # Clustering base con KMeans
from kmeans_improvement import run_kmeans_improvement   # Clustering migliorato con scelta ottimale di k

# Punto di ingresso principale 
if __name__ == '__main__':
    # Esecuzione dell'analisi supervisionata (classificazione)
    print("=== ANALISI SUPERVISIONATA ===")
    run_supervised()    # Esegue classificazione e stampa metriche di valutazione (accuracy, F1, ecc.)

    # Esecuzione dell'analisi non supervisionata base con KMeans
    print("\n=== ANALISI NON SUPERVISIONATA (KMeans) ===")
    run_clustering()    # Clustering con k fisso (es. k=3) e visualizzazione 2D con PCA

    # Esecuzione del clustering avanzato con KMeans migliorato
    print("\n=== KMeans Clustering Migliorato ===")
    run_kmeans_improvement()    # Ricerca automatica del miglior k e confronto con GMM e Agglomerative