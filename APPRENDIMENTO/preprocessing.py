# Import delle librerie
import pandas as pd  # Libreria per manipolazione dati in formato tabellare (DataFrame)
from sklearn.preprocessing import MultiLabelBinarizer  # Converte etichette multiple (liste) in codifica one-hot

# Carica e pre-processa i dati per clustering con KMeans
def load_and_preprocess_kmeans(filepath='DATASET/dataset_ml.csv'):
    # 1. Caricamento del dataset da file CSV
    df = pd.read_csv(filepath)

    # 2. Filtra righe con punteggio utente valido (scarta NaN e <= 0)
    df = df[df['Punteggio_Utente'].notna() & (df['Punteggio_Utente'] > 0)]

    # 3. Pulisce e standardizza la colonna 'Generi':
    #    - divide per virgola
    #    - rimuove spazi e trasforma in lowercase con underscore
    df['Generi'] = df['Generi'].fillna('').apply(
        lambda x: [g.strip().lower().replace(' ', '_') for g in x.split(',') if g]
    )

    # 4. Codifica multilabel dei generi in one-hot encoding
    mlb = MultiLabelBinarizer()
    generi_encoded = pd.DataFrame(mlb.fit_transform(df['Generi']),columns=mlb.classes_,index=df.index)
 
    # 5. Calcola delta tra punteggio utente e punteggio medio
    df['Delta_Score'] = df['Punteggio_Utente'] - df['Punteggio_Medio']

    # 6. Costruisce la matrice X unendo:
    #    - codifica binaria dei generi
    #    - alcune colonne numeriche: Punteggio_Medio, Rank, Popolarità, Delta_Score
    X = pd.concat([generi_encoded,df[['Punteggio_Medio', 'Rank', 'Popolarita', 'Delta_Score']]], axis=1).fillna(0)

    # 7. Ritorna:
    #    - X: feature matrix per clustering
    #    - df: dataframe originale (serve per etichette, visualizzazione, ecc.)
    return X, df
