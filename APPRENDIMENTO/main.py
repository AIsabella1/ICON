# --- Importa i 3 principali moduli di analisi ---
from supervised_runner import run_supervised            # Classificazione supervisionata
from clustering_runner import run_clustering            # Clustering base con KMeans
from kmeans_improvement import run_kmeans_improvement   # Clustering migliorato con scelta ottimale di k

# --- Punto di ingresso principale ---
if __name__ == '__main__':
    print("=== ANALISI SUPERVISIONATA ===")
    run_supervised()    # Esegue classificazione + valutazione dei modelli

    print("\n=== ANALISI NON SUPERVISIONATA (KMeans) ===")
    run_clustering()    # Visualizza clustering con k fisso (es. k=3)

    print("\n=== KMeans Clustering Migliorato ===")
    run_kmeans_improvement()    # Trova il miglior k con silhouette score ed elbow