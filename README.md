![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

# ICON: Manga Intelligence Framework

**ICON** è un progetto finalizzato alla costruzione di un sistema ibrido di raccomandazione e analisi nel dominio dei *manga*, che integra:

- **Recupero dati reali** da [MyAnimeList](https://myanimelist.net/) tramite API
- **Apprendimento supervisionato e non supervisionato** con modelli ML
- **Motore logico basato su Prolog** per raccomandazioni simboliche
- **Ontologia OWL** per supporto al ragionamento semantico

---

## Obiettivi del Progetto

1. **Ottenere dataset realistici** e aggiornati sulla base delle preferenze utente
2. **Generare una knowledge base** strutturata in linguaggio Prolog
3. **Realizzare un sistema di raccomandazione** basato su logica e apprendimento automatico
4. **Eseguire analisi visive** sui modelli e sui cluster rilevati
5. **Dimostrare l'uso di tecnologie AI simboliche e subsimboliche**

---

## Struttura del repository

### 📁 `CLUSTERING/`
Script Apprendimento Supervisionato e Non:
- [`clustering_runner.py`](CLUSTERING/clustering_runner.py): clustering base con PCA (k=3)
- [`kmeans_improvement.py`](CLUSTERING/kmeans_improvement.py): ottimizzazione KMeans con silhouette/elbow
- [`main.py`](CLUSTERING/main.py): esecuzione unificata delle analisi
- [`model_builder.py`](CLUSTERING/model_builder.py): factory dei modelli ML
- [`param_config.py`](CLUSTERING/param_config.py): griglia parametri per tuning
- [`plot_tools.py`](CLUSTERING/plot_tools.py): funzioni di visualizzazione dei modelli
- [`preprocessing.py`](CLUSTERING/preprocessing.py): pulizia e codifica del dataset per il clustering (KMeans)
- [`report_utils.py`](CLUSTERING/report_utils.py): valutazione finale modelli (AdaBoost)
- [`supervised_runner.py`](CLUSTERING/supervised_runner.py): pipeline apprendimento supervisionato (classificazione)

### 📁 `DATASET/`
Contiene i CSV generati:
- [`dataset_ml.csv`](DATASET/dataset_ml.csv): dataset unificato con campi numerici e binarizzati
- [`mangalist.csv`](DATASET/mangalist.csv): lista letta dall'utente
- [`top_manga.csv`](DATASET/top_manga.csv): 1000 manga più popolari da MyAnimeList

### 📁 `KB/`
Knowledge base Prolog:
- [`kb_creator.py`](KB/kb_creator.py): genera la KB Prolog
- [`knowledge_base.pl`](KB/knowledge_base.pl): contiene fatti `manga/8` e `lettura_utente/5`
- [`system.pl`](KB/system.pl): menu interattivo in Prolog

### 📁 `OWL/`
Ontologia OWL:
- [`manga.owl`](OWL/manga.owl): struttura semantica con classi `Manga`, `Seinen`, `AwardWinning`
- [`ontology_example.py`](OWL/ontology_example.py): script Python per ragionamento OWL (Hermit)

### 📁 `PNG/`
Grafici generati:
- Accuratezze, metriche per modello, radar chart, clustering PCA, ecc.

### 📁 `PYTHON_DATASET/`
Script estrazione dati da MyAnimeList:
- [`mangalist_extended.py`](PYTHON_DATASET/mangalist_extended.py): versione estesa che arricchisce il dataset con mean, rank, popolarità per ogni manga
- [`top_manga.py`](PYTHON_DATASET/top_manga.py): scarica i manga top da MAL
- [`user_manga.py`](PYTHON_DATASET/user_manga.py): scarica la lista dell'utente da MAL

---

## Requisiti

- Python 3.x
- Librerie: `scikit-learn`, `xgboost`, `seaborn`, `matplotlib`, `owlready2`, `requests`, `pandas`
- Prolog: SWI-Prolog
- Java per reasoner OWL (Hermit)

---

## Esecuzione

1. Autenticarsi su MyAnimeList (browser automatico)
2. Generare CSV e KB con gli script Python (ATTUALMENTE INCLUSI QUELLI GENERATI DA ME MEDESIMO)
3. Eseguire classificazione e clustering con `main.py`

   3.1. Eseguita classificazione con `supervised_runner.py`

   3.2 Eseguita clustering con `clustering_runner.py` o `kmeans_improvement.py`
4. Lanciare motore logico in Prolog con `system.pl`
5. Eseguire ragionamento OWL tramite `ontology_example.py`

---

## Autori

Progetto ICON sviluppato da:
- Antonello Isabella 
  
  Matricola: 737827
  
  Mail: a.isabella1@studenti.uniba.it
