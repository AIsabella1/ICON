![Python](https://img.shields.io/badge/python-3.10+-blue.svg)

# Sistema Intelligente di Raccomandazione e Analisi del Dominio Manga

Finalizzato alla costruzione di un sistema di raccomandazione e analisi nel dominio dei manga, che integra:

- **Recupero dati reali** da [MyAnimeList](https://myanimelist.net/) tramite API
- **Apprendimento supervisionato** con modelli ML
- **Motore logico basato su Prolog** per raccomandazioni basate su regole

---

## Obiettivi del Progetto

1. **Ottenere dataset realistici** e aggiornati sulla base delle preferenze utente
2. **Generare una knowledge base**
3. **Realizzare un sistema di raccomandazione** basato su logica e apprendimento automatico
4. **Eseguire analisi visive** sui modelli

---

## Struttura del repository

### `APPRENDIMENTO/`
Script Apprendimento Supervisionato:
- [`main.py`](APPRENDIMENTO/main.py): esegue il flusso ML
- [`model_builder.py`](APPRENDIMENTO/model_builder.py): factory dei modelli ML
- [`param_config.py`](APPRENDIMENTO/param_config.py): iperparametri per ogni modello
- [`plot_tools.py`](APPRENDIMENTO/plot_tools.py): radar, heatmap, bar chart, ecc.
- [`report_utils.py`](APPRENDIMENTO/report_utils.py): AdaBoost finale e confusion matrix
- [`supervised_runner.py`](APPRENDIMENTO/supervised_runner.py): classificazione con cross-validation

### `DATASET/`
Contiene i CSV generati:
- [`dataset_ml.csv`](DATASET/dataset_ml.csv): dataset finale per ML
- [`mangalist.csv`](DATASET/mangalist.csv): dataset finale per KB
- [`top_manga.csv`](DATASET/top_manga.csv):  top manga da MAL

### `DOCUMENTAZIONE/`
Contiene la documentazione nel formato docx e pdf:
- [`Sistema Intelligente di Raccomandazione e Analisi del Dominio Manga.docx`](DOCUMENTAZIONE/Sistema%20Intelligente%20di%20Raccomandazione%20e%20Analisi%20del%20Dominio%20Manga.docx): documentazione nel formato docx
- [`Sistema Intelligente di Raccomandazione e Analisi del Dominio Manga.pdf`](DOCUMENTAZIONE/Sistema%20Intelligente%20di%20Raccomandazione%20e%20Analisi%20del%20Dominio%20Manga.pdf): documentazione nel formato pdf

### `KB/`
Knowledge base Prolog:
- [`kb_creator.py`](KB/kb_creator.py): genera knowledge_base.pl
- [`knowledge_base.pl`](KB/knowledge_base.pl): fatti `manga/8` e `lettura_utente/5`
- [`system.pl`](KB/system.pl): regole di raccomandazione Prolog + menu

### `PNG/`
Grafici generati:
- Accuratezze, metriche per modello, radar chart, clustering PCA, ecc.

### `PYTHON_DATASET/`
Script estrazione dati da MyAnimeList:
- [`mangalist_extended.py`](PYTHON_DATASET/mangalist_extended.py): versione arricchita (mean, rank, popolarità)
- [`top_manga.py`](PYTHON_DATASET/top_manga.py): classifica top 1000 da MAL
- [`user_manga.py`](PYTHON_DATASET/user_manga.py): lista manga utente semplice

---

## Requisiti

- Python 3.10+
- SWI-Prolog (per esecuzione KB)
- Librerie Python:
  - `pandas`, `scikit-learn`, `xgboost`, `matplotlib`, `seaborn`, `requests`, `numpy`

---

## Esecuzione

1. Autenticarsi su MyAnimeList (browser automatico, attualmente nello script sono presenti i codici generati da me medesimo)
2. Generare CSV e KB con gli script Python (rispettivamente nelle cartelle PYTHON_DATASET e KB)
3. Eseguire classificazione con `main.py` (nella cartella APPRENDIMENTO)
4. Lanciare motore logico in Prolog con `system.pl`

---

## Nota tecnica sull'autenticazione MyAnimeList

Il codice implementa correttamente il flusso OAuth2 con PKCE secondo la [guida ufficiale MyAnimeList](https://myanimelist.net/blog.php?eid=835707).  
Comprende:

- Generazione sicura del `code_verifier`
- Autenticazione via browser (`code_challenge_method=plain`)
- Server HTTP locale per ricezione del `code`
- Scambio `code => access_token` con tutti i parametri richiesti

Il sistema implementa correttamente il flusso OAuth2 + PKCE.

Aggiornamento 29/05/2025: Gli script sono nuovamente funzionanti. Dataset aggiornati e salvati in DATASET/.

---

## Autore

Antonello Isabella 
  
Matricola: 737827
  
E-Mail: a.isabella1@studenti.uniba.it

---

## Riferimenti utili

Libro: Poole & Mackworth – Artificial Intelligence

MyAnimeList API – https://myanimelist.net/apiconfig 

SWI-Prolog – https://www.swi-prolog.org/ 

Scikit-learn – https://scikit-learn.org/ 

XGBoost – https://xgboost.ai/ 

Pandas – https://pandas.pydata.org/ 

Matplotlib – https://matplotlib.org/ 

Seaborn – https://seaborn.pydata.org/ 

NumPy – https://numpy.org/ 
