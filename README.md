![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

# Sistema Intelligente di Raccomandazione e Analisi del Dominio Manga

Progetto finalizzato alla costruzione di un sistema ibrido di raccomandazione e analisi nel dominio dei *manga*, che integra:

- **Recupero dati reali** da [MyAnimeList](https://myanimelist.net/) tramite API
- **Apprendimento supervisionato e non supervisionato** con modelli ML
- **Motore logico basato su Prolog** per raccomandazioni simboliche
- **Esempio Ontologia OWL** per supporto al ragionamento semantico

---

## Obiettivi del Progetto

1. **Ottenere dataset realistici** e aggiornati sulla base delle preferenze utente
2. **Generare una knowledge base** strutturata in linguaggio Prolog
3. **Realizzare un sistema di raccomandazione** basato su logica e apprendimento automatico
4. **Eseguire analisi visive** sui modelli e sui cluster rilevati
5. **Dimostrare l'uso di tecnologie AI simboliche e subsimboliche**

---

## Struttura del repository

### 📁 `APPRENDIMENTO/`
Script Apprendimento Supervisionato e Non:
- [`clustering_runner.py`](APPRENDIMENTO/clustering_runner.py): clustering base con PCA (k=3)
- [`kmeans_improvement.py`](APPRENDIMENTO/kmeans_improvement.py): ottimizzazione KMeans con silhouette/elbow
- [`main.py`](APPRENDIMENTO/main.py): esecuzione unificata delle analisi
- [`model_builder.py`](APPRENDIMENTO/model_builder.py): factory dei modelli ML
- [`param_config.py`](APPRENDIMENTO/param_config.py): griglia parametri per tuning
- [`plot_tools.py`](APPRENDIMENTO/plot_tools.py): funzioni di visualizzazione dei modelli
- [`preprocessing.py`](APPRENDIMENTO/preprocessing.py): pulizia e codifica del dataset per il clustering (KMeans)
- [`report_utils.py`](APPRENDIMENTO/report_utils.py): valutazione finale modelli (AdaBoost)
- [`supervised_runner.py`](APPRENDIMENTO/supervised_runner.py): pipeline apprendimento supervisionato (classificazione)

### 📁 `DATASET/`
Contiene i CSV generati:
- [`dataset_ml.csv`](DATASET/dataset_ml.csv): dataset unificato con campi numerici e binarizzati
- [`mangalist.csv`](DATASET/mangalist.csv): lista letta dall'utente
- [`top_manga.csv`](DATASET/top_manga.csv): 1000 manga più popolari da MyAnimeList

### 📁 `DOCUMENTAZIONE/`
Contiene la documentazione nel formato docx e pdf:
- [`Sistema Intelligente di Raccomandazione e Analisi del Dominio Manga.docx`](DOCUMENTAZIONE/Sistema%20Intelligente%20di%20Raccomandazione%20e%20Analisi%20del%20Dominio%20Manga.docx): documentazione nel formato docx
- [`Sistema Intelligente di Raccomandazione e Analisi del Dominio Manga.pdf`](DOCUMENTAZIONE/Sistema%20Intelligente%20di%20Raccomandazione%20e%20Analisi%20del%20Dominio%20Manga.pdf): documentazione nel formato pdf

### 📁 `KB/`
Knowledge base Prolog:
- [`kb_creator.py`](KB/kb_creator.py): genera la KB Prolog
- [`knowledge_base.pl`](KB/knowledge_base.pl): contiene fatti `manga/8` e `lettura_utente/5`
- [`system.pl`](KB/system.pl): menu interattivo in Prolog

### 📁 `OWL/`
Esempio Ontologia OWL:
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

- Python 3.10+
- SWI-Prolog (per esecuzione KB simbolica)
- Librerie Python:
  - `pandas`, `numpy`, `scikit-learn`, `xgboost`, `matplotlib`, `seaborn`, `owlready2`, `requests`
- Java per reasoner OWL (Hermit)

---

## Esecuzione

1. Autenticarsi su MyAnimeList (browser automatico, attualmente nello script sono presenti i codici generati da me medesimo)
2. Generare CSV e KB con gli script Python (rispettivamente nelle cartelle PYTHON_DATASET e KB)
3. Eseguire classificazione e clustering con `main.py` (nella cartella APPRENDIMENTO)

   3.1. Eseguito automaticamente classificazione con `supervised_runner.py`

   3.2 Eseguito automaticamente clustering con `clustering_runner.py` o `kmeans_improvement.py`
4. Lanciare motore logico in Prolog con `system.pl`
5. Eseguire ragionamento OWL tramite `ontology_example.py`

---

## Nota tecnica sull'autenticazione MyAnimeList

Il codice implementa correttamente il flusso OAuth2 con PKCE secondo la [guida ufficiale MyAnimeList](https://myanimelist.net/blog.php?eid=835707).  
Comprende:

- Generazione sicura del `code_verifier`
- Autenticazione via browser (`code_challenge_method=plain`)
- Server HTTP locale per ricezione del `code`
- Scambio `code → access_token` con tutti i parametri richiesti

Tuttavia, a partire dal 1 maggio 2024, MyAnimeList ha introdotto una protezione tramite **AWS WAF** che blocca automaticamente le richieste `POST` al token endpoint, richiedendo una verifica CAPTCHA lato browser. Non so se questa protezione persiste o meno.

I dati necessari (top manga, lista utente) sono stati raccolti **prima dell’introduzione di questo blocco**, e sono presenti nel progetto in formato `.csv`.

Questa protezione server-side **non invalida l'implementazione**, ma impedisce la ri-esecuzione automatica dello script senza intervento umano.

    *AGGIORNAMENTO DEL 29/05/2025*

    Gli script sono nuovamente funzionanti.
    Sono stati estratti i nuovi dataset aggiornati e inseriti nella cartella DATASET/DATASET ESTRATTI 29.05.2025.
    La documentazione fa riferimento ai dataset presenti nella cartella DATASET.

---

## Autore

Progetto ICON sviluppato da:
- Antonello Isabella 
  
  Matricola: 737827
  
  E-Mail: a.isabella1@studenti.uniba.it

---

## Riferimenti utili

Libro: Poole & Mackworth – Artificial Intelligence

MyAnimeList API: https://myanimelist.net/apiconfig

SWI-Prolog: https://www.swi-prolog.org

Owlready2: https://owlready2.readthedocs.io

scikit-learn: https://scikit-learn.org

HermiT: https://www.hermit-reasoner.com
