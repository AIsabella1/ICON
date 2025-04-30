# --- Funzione per eseguire il clustering con KMeans e visualizzazione PCA ---
def run_clustering():
    import matplotlib.pyplot as plt  # Per la visualizzazione
    import seaborn as sns            # Per grafici eleganti
    from sklearn.decomposition import PCA  # Per ridurre dimensionalità
    from sklearn.cluster import KMeans     # Algoritmo di clustering
    from preprocessing import load_and_preprocess_kmeans  # Caricamento dati pre-processati

    # Carica i dati pre-elaborati
    X, df_original = load_and_preprocess_kmeans()

    # Applica PCA per ridurre a 2 dimensioni
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    # Applica KMeans con 3 cluster
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X_pca)

    # Aggiunge i cluster e le componenti PCA al dataframe originale
    df_original['Cluster'] = clusters
    df_original['PCA1'] = X_pca[:, 0]
    df_original['PCA2'] = X_pca[:, 1]

    # Visualizza i risultati del clustering in 2D
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_original, x='PCA1', y='PCA2', hue='Cluster', palette='Set2', s=70)
    plt.title('KMeans Clustering dei Manga (PCA 2D)')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.legend(title='Cluster')
    plt.tight_layout()
    plt.savefig('PNG/kmeans_clustering_plot.png')   # Salva il grafico come immagine PNG

    # Mostra un esempio dei manga assegnati ai cluster
    print("\nEsempio cluster assegnati:")
    print(df_original[['Titolo', 'Cluster']].head(10))
