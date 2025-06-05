# Funzione per eseguire il clustering con KMeans e visualizzazione PCA
def run_clustering():
    # Importazione delle librerie necessarie
    import matplotlib.pyplot as plt  # Per creare grafici
    import seaborn as sns            # Per migliorare l'estetica dei grafici
    from sklearn.decomposition import PCA  # Per ridurre la dimensionalità dei dati
    from sklearn.cluster import KMeans     # Algoritmo KMeans per il clustering
    from preprocessing import load_and_preprocess_kmeans  # Funzione personalizzata per caricare i dati pre-elaborati

    # Caricamento dei dati
    # X: matrice delle feature numeriche pre-processate
    # df_original: DataFrame originale (con titoli manga, ecc.)
    X, df_original = load_and_preprocess_kmeans()

    # Riduzione della dimensionalità con PCA
    # PCA permette di proiettare i dati in uno spazio a 2 dimensioni per visualizzarli
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)  # X_pca ha ora solo 2 colonne: PCA1 e PCA2

    # Clustering con KMeans
    # Applica KMeans per raggruppare i dati in 3 cluster (valore scelto arbitrariamente)
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X_pca)  # Ritorna l’etichetta del cluster assegnato a ciascun punto

    # Aggiunta dei risultati al DataFrame originale
    df_original['Cluster'] = clusters
    df_original['PCA1'] = X_pca[:, 0]
    df_original['PCA2'] = X_pca[:, 1]

    # Visualizzazione dei cluster su un piano 2D
    plt.figure(figsize=(10, 6))  # Imposta la dimensione del grafico
    sns.scatterplot(
        data=df_original,
        x='PCA1', y='PCA2',
        hue='Cluster',  # Colore in base al cluster
        palette='Set2', s=70  # Palette e dimensione punti
    )
    plt.title('KMeans Clustering dei Manga (PCA 2D)')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.legend(title='Cluster')
    plt.tight_layout()
    plt.savefig('PNG/kmeans_clustering_plot.png')  # Salva il grafico come immagine PNG

    # Output di esempio per il terminale
    # Mostra i primi 10 manga con il cluster assegnato
    print("\nEsempio cluster assegnati:")
    print(df_original[['Titolo', 'Cluster']].head(10))