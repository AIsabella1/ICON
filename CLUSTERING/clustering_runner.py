
def run_clustering():
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    from preprocessing import load_and_preprocess_kmeans

    X, df_original = load_and_preprocess_kmeans()

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X_pca)

    df_original['Cluster'] = clusters
    df_original['PCA1'] = X_pca[:, 0]
    df_original['PCA2'] = X_pca[:, 1]

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_original, x='PCA1', y='PCA2', hue='Cluster', palette='Set2', s=70)
    plt.title('KMeans Clustering dei Manga (PCA 2D)')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.legend(title='Cluster')
    plt.tight_layout()
    plt.savefig('PNG/kmeans_clustering_plot.png')

    print("\nEsempio cluster assegnati:")
    print(df_original[['Titolo', 'Cluster']].head(10))
