# Esegue clustering KMeans con ricerca automatica del miglior numero di cluster
def run_kmeans_improvement():
    # Importazione librerie necessarie 
    import os   # Usata per assicurarsi che la cartella "PNG" esista prima di salvare i grafici.
    import pandas as pd # Fornisce strutture dati flessibili (come DataFrame) per manipolare e visualizzare dataset tabellari.
    import matplotlib.pyplot as plt # 'pyplot' è una sua interfaccia semplice per creare grafici come line plot, scatter plot, ecc.
    import seaborn as sns   # Permette di creare scatterplot, heatmap e altri grafici.
    from sklearn.preprocessing import StandardScaler    # StandardScaler porta ogni feature ad avere media 0 e deviazione standard 1 — fondamentale per KMeans e PCA.
    from sklearn.decomposition import PCA   # Serve per proiettare i dati in uno spazio a 2D (utile per la visualizzazione), mantenendo la maggior parte della varianza.
    from sklearn.cluster import KMeans, AgglomerativeClustering #  AgglomerativeClustering: clustering gerarchico, unisce i punti a coppie in base alla somiglianza.
    from sklearn.mixture import GaussianMixture # A differenza di KMeans, assume che i dati provengano da distribuzioni normali e stima probabilità di appartenenza ai cluster.
    from sklearn.metrics import silhouette_score    # Valori vicini a 1 indicano un buon clustering, vicini a 0 indicano sovrapposizione tra cluster.
    from preprocessing import load_and_preprocess_kmeans    # Si occupa di caricare i dati dal file sorgente e applicare i preprocessing necessari (es. encoding, pulizia, ecc.).

    # Creazione cartella di output per i grafici
    os.makedirs("PNG", exist_ok=True)

    print("\n--- KMeans Clustering con miglioramento ---")

    # 1. Caricamento e normalizzazione
    # Carica i dati pretrattati e li normalizza con StandardScaler
    X, df_original = load_and_preprocess_kmeans()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 2. Ricerca automatica del miglior numero di cluster (k)
    inertia = []     # Misura della compattezza dei cluster
    silhouette = []  # Misura della separazione tra cluster
    k_range = range(2, 20)  # Valori di k da testare (da 2 a 19)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(X_scaled)
        inertia.append(kmeans.inertia_)
        silhouette.append(silhouette_score(X_scaled, kmeans.labels_))

    # 3. Visualizzazione Inertia (Elbow Method)
    plt.figure(figsize=(10, 4))
    plt.plot(k_range, inertia, marker='o')
    plt.title("Elbow Method - Inertia vs Numero di Cluster")
    plt.xlabel("Numero di cluster (k)")
    plt.ylabel("Inertia")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("PNG/elbow_plot.png")

    # 4. Visualizzazione Silhouette Score
    plt.figure(figsize=(10, 4))
    plt.plot(k_range, silhouette, marker='s', color='green')
    plt.title("Silhouette Score vs Numero di Cluster")
    plt.xlabel("Numero di cluster (k)")
    plt.ylabel("Silhouette Score")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("PNG/silhouette_plot.png")

    # 5. Scelta automatica del miglior k
    best_k = k_range[silhouette.index(max(silhouette))]
    print(f"Numero di cluster ottimale (k): {best_k}")

    # 6. Clustering finale con KMeans usando k ottimale
    kmeans_final = KMeans(n_clusters=best_k, random_state=42)
    clusters = kmeans_final.fit_predict(X_scaled)

    # 7. Riduzione della dimensionalità per visualizzazione (PCA 2D)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    # Aggiunge i risultati al DataFrame
    df_original['Cluster'] = clusters
    df_original['PCA1'] = X_pca[:, 0]
    df_original['PCA2'] = X_pca[:, 1]

    # 8. Visualizzazione dei cluster trovati con KMeans
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_original, x='PCA1', y='PCA2', hue='Cluster', palette='tab10', s=70)
    plt.title(f'KMeans Clustering dei Manga (k={best_k}) - PCA 2D')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.legend(title='Cluster')
    plt.tight_layout()
    plt.savefig("PNG/kmeans_cluster_plot_bestk.png")

    # 9. Output informativo
    print("\nDistribuzione dei cluster (KMeans):")
    print(df_original['Cluster'].value_counts())
    print("\nEsempio di manga e cluster assegnato:")
    print(df_original[['Titolo', 'Cluster']].head(10))

    # 10. Clustering alternativo: Gaussian Mixture Model (GMM)
    gmm = GaussianMixture(n_components=best_k, random_state=42)
    clusters_gmm = gmm.fit_predict(X_scaled)
    df_original['Cluster_GMM'] = clusters_gmm

    # Visualizzazione GMM
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_original, x='PCA1', y='PCA2', hue='Cluster_GMM', palette='tab10', s=70)
    plt.title(f'GMM Clustering dei Manga (k={best_k}) - PCA 2D')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.legend(title='Cluster GMM')
    plt.tight_layout()
    plt.savefig("PNG/gmm_cluster_plot_bestk.png")

    print("\nDistribuzione dei cluster (GMM):")
    print(df_original['Cluster_GMM'].value_counts())
    print("\nEsempio cluster GMM assegnati:")
    print(df_original[['Titolo', 'Cluster_GMM']].head(10))

    # 11. Clustering alternativo: Agglomerative
    agg = AgglomerativeClustering(n_clusters=best_k)
    clusters_agg = agg.fit_predict(X_scaled)
    df_original['Cluster_Agg'] = clusters_agg

    # Visualizzazione Agglomerative
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_original, x='PCA1', y='PCA2', hue='Cluster_Agg', palette='tab10', s=70)
    plt.title(f'Agglomerative Clustering dei Manga (k={best_k}) - PCA 2D')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.legend(title='Cluster Agglomerative')
    plt.tight_layout()
    plt.savefig("PNG/agglomerative_cluster_plot.png")

    print("\nDistribuzione dei cluster (Agglomerative):")
    print(df_original['Cluster_Agg'].value_counts())
    print("\nEsempio cluster Agglomerative assegnati:")
    print(df_original[['Titolo', 'Cluster_Agg']].head(10))
