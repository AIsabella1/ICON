import os
os.environ["OWLREADY_HERMIT_JAVA_MEMORY"] = "256M"

from owlready2 import *

# Carica l'ontologia
onto = get_ontology("ontology/manga.owl").load()

# Motore di ragionamento con memoria ridotta
with onto:
    sync_reasoner_hermit()

# Stampa classi e manga premiati
print("\n=== Classi disponibili ===")
for cls in onto.classes():
    print(cls)

print("\n=== Manga premiati ===")
for manga in onto.Manga.instances():
    if onto.hasAward in manga.get_properties():
        for prop in manga.get_properties():
            for value in prop[manga]:
                if "AwardWinning" in str(value):
                    print(manga.name)