
from supervised_runner import run_supervised
from clustering_runner import run_clustering
from kmeans_improvement import run_kmeans_improvement

if __name__ == '__main__':
    print("=== ANALISI SUPERVISIONATA ===")
    run_supervised()

    print("\n=== ANALISI NON SUPERVISIONATA (KMeans) ===")
    run_clustering()

    print("\n=== KMeans Clustering Migliorato ===")
    run_kmeans_improvement()