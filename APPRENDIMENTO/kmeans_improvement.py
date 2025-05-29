# --- Esegue clustering KMeans con ricerca automatica del miglior k ---
def run_kmeans_improvement():
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from preprocessing import load_and_preprocess_kmeans

    print("\n--- KMeans Clustering con miglioramento ---")

    # 1. Caricamento dataset e normalizzazione
    X, df_original = load_and_preprocess_kmeans()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 2. Elbow Method + Silhouette Score per trovare k ideale
    inertia = []     # misura compattezza (intra-cluster)
    silhouette = []  # misura separabilità tra cluster
    k_range = range(2, 11)  # prova valori di k da 2 a 10

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(X_scaled)
        inertia.append(kmeans.inertia_)
        silhouette.append(silhouette_score(X_scaled, kmeans.labels_))

    # Plot Inertia (Elbow)
    plt.figure(figsize=(10,4))
    plt.plot(k_range, inertia, marker='o')
    plt.title("Elbow Method - Inertia vs k")
    plt.xlabel("Numero di cluster (k)")
    plt.ylabel("Inertia")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("PNG/elbow_plot.png")

    # Plot Silhouette
    plt.figure(figsize=(10,4))
    plt.plot(k_range, silhouette, marker='s', color='green')
    plt.title("Silhouette Score vs k")
    plt.xlabel("Numero di cluster (k)")
    plt.ylabel("Silhouette Score")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("PNG/silhouette_plot.png")

    # 3. Seleziona k migliore (massimo silhouette)
    best_k = k_range[silhouette.index(max(silhouette))]
    print(f"Numero di cluster ottimale (k): {best_k}")

    # 4. Applica clustering con k ottimale
    kmeans_final = KMeans(n_clusters=best_k, random_state=42)
    clusters = kmeans_final.fit_predict(X_scaled)

    # 5. Riduci dimensione per visualizzazione con PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    df_original['Cluster'] = clusters
    df_original['PCA1'] = X_pca[:, 0]
    df_original['PCA2'] = X_pca[:, 1]

    # 6. Scatter plot dei cluster
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_original, x='PCA1', y='PCA2', hue='Cluster', palette='tab10', s=70)
    plt.title(f'KMeans Clustering dei Manga (k={best_k}) - PCA 2D')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.legend(title='Cluster')
    plt.tight_layout()
    plt.savefig("PNG/kmeans_cluster_plot_bestk.png")

    # 7. Stampa primi manga per ogni cluster
    print("\nEsempio di manga e cluster assegnato:")
    print(df_original[['Titolo', 'Cluster']].head(10))
