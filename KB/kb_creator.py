import csv  # Per leggere i dati da file CSV
import os   # Per costruire e gestire i percorsi dei file

# Funzione per normalizzare le stringhe in formato compatibile con Prolog
def safe_string(s):
    return s.replace("'", "\\'").replace('"', '\\"').replace(" ", "_").lower()
    # Sostituisce apici, virgolette e spazi con caratteri sicuri per Prolog

# Funzione principale: genera un file .pl contenente i fatti Prolog
def genera_kb_prolog(mangalist_path, top_manga_path, output_pl_path):
    with open(output_pl_path, 'w', encoding='utf-8') as f_out:
        
        # Sezione 1: Estrae top_manga.csv e scrive fatti Prolog con arità 8
        # Predicato generato: manga(ID, Titolo, [Generi], Mean, Rank, Pop, Stato, [Autori])
        with open(top_manga_path, 'r', encoding='utf-8') as f_top:
            reader = csv.DictReader(f_top)
            for row in reader:
                id_manga = row['ID']
                titolo = safe_string(row['Titolo'])
                generi = [safe_string(g) for g in row['Generi'].split(',') if g.strip()]
                mean = row.get('Punteggio Medio', 'null')
                rank = row.get('Rank', 'null')
                popolarita = row.get('Popolarità', 'null')
                stato = safe_string(row.get('Stato', 'unknown'))
                autori = [safe_string(a) for a in row.get('Autori', '').split(',') if a.strip()]

                # Scrittura del fatto Prolog: manga/8
                f_out.write(f"manga({id_manga}, '{titolo}', {generi}, {mean}, {rank}, {popolarita}, {stato}, {autori}).\n")

        # Sezione 2: Estrae mangalist.csv e scrive fatti lettura_utente/5
        # Predicato generato: lettura_utente(ID, Titolo, Stato, PunteggioUtente, [Generi])
        with open(mangalist_path, 'r', encoding='utf-8') as f_manga:
            reader = csv.DictReader(f_manga)
            for row in reader:
                id_manga = row['ID']
                titolo = safe_string(row['Titolo'])
                stato_lettura = safe_string(row.get('Stato', 'unknown'))
                punteggio_utente = row.get('Punteggio', '0')
                
                # Converte il punteggio in float, fallback a 0 in caso di errore
                try:
                    punteggio_utente = float(punteggio_utente)
                except ValueError:
                    punteggio_utente = 0

                generi_raw = row.get('Generi', '')
                generi = [safe_string(g) for g in generi_raw.split(',') if g.strip()]

                # Scrittura del fatto Prolog: lettura_utente/5
                f_out.write(f"lettura_utente({id_manga}, '{titolo}', {stato_lettura}, {punteggio_utente}, {generi}).\n")

    print(f"\nKnowledge Base Prolog salvata come '{output_pl_path}'!")

#  MAIN: definisce i percorsi dei file e avvia la generazione della KB
if __name__ == '__main__':
    # Costruisce i percorsi assoluti per i file CSV
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'DATASET'))
    mangalist_path = os.path.join(base_dir, 'mangalist.csv')
    top_manga_path = os.path.join(base_dir, 'top_manga.csv')

    # Crea la directory di output se non esiste
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'KB'))
    os.makedirs(output_dir, exist_ok=True)
    output_pl_path = os.path.join(output_dir, 'knowledge_base.pl')

    # Avvia la generazione della knowledge base Prolog
    genera_kb_prolog(mangalist_path, top_manga_path, output_pl_path)