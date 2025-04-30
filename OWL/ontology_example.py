import os
os.environ["OWLREADY_HERMIT_JAVA_MEMORY"] = "256M"  # Limita la memoria per il reasoner HermiT

from owlready2 import * # Importa tutte le funzioni per lavorare con OWL in Python

# --- Caricamento dell'ontologia ---
onto = get_ontology("OWL/manga.owl").load() # Carica l'ontologia OWL dal file specificato

# --- Esecuzione del motore di ragionamento (reasoner HermiT) ---
with onto:
    sync_reasoner_hermit()  # Avvia il reasoner per inferenze logiche (es. AwardWinning)

# --- Stampa delle classi presenti nell'ontologia ---
print("\n=== Classi disponibili ===")
for cls in onto.classes():
    print(cls)  # Stampa ogni classe definita (es. Manga, AwardWinning, ecc.)

# --- Stampa dei manga che hanno ricevuto un premio ---
print("\n=== Manga premiati ===")
for manga in onto.Manga.instances():    # Cicla tutte le istanze della classe Manga
    if onto.hasAward in manga.get_properties(): # Controlla se hanno la proprietà hasAward
        for prop in manga.get_properties():
            for value in prop[manga]:   # Per ogni valore della proprietà
                if "AwardWinning" in str(value):    # Se la stringa contiene AwardWinning
                    print(manga.name)   # Stampa il nome del manga premiato