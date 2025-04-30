import csv  # Per estrarre i dati in formato CSV
import os   # Per operazioni su file/cartelle

# --- Funzione per rendere sicure le stringhe per Prolog ---
def safe_string(s):
    return s.replace("'", "\\'").replace('"', '\\"').replace(" ", "_").lower()

# --- Funzione principale: genera un file knowledge_base.pl leggibile da Prolog ---
def genera_kb_prolog(mangalist_path, top_manga_path, output_pl_path):
    with open(output_pl_path, 'w', encoding='utf-8') as f_out:
        
        # --- Sezione 1: Estrae dati da top_manga.csv e scrive fatti Prolog con struttura manga/8 ---
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

                # Scrive: manga(ID, 'titolo', [generi], mean, rank, pop, stato, [autori]).
                f_out.write(f"manga({id_manga}, '{titolo}', {generi}, {mean}, {rank}, {popolarita}, {stato}, {autori}).\n")

        # --- Sezione 2: Estrae dati da mangalist.csv e scrive lettura_utente/5 ---
        with open(mangalist_path, 'r', encoding='utf-8') as f_manga:
            reader = csv.DictReader(f_manga)
            for row in reader:
                id_manga = row['ID']
                titolo = safe_string(row['Titolo'])
                stato_lettura = safe_string(row.get('Stato', 'unknown'))
                punteggio_utente = row.get('Punteggio', '0')
                
                # Normalizza punteggio utente (float, default a 0)
                try:
                    punteggio_utente = float(punteggio_utente)
                except ValueError:
                    punteggio_utente = 0

                generi_raw = row.get('Generi', '')
                generi = [safe_string(g) for g in generi_raw.split(',') if g.strip()]

                # Scrive: lettura_utente(ID, 'titolo', stato, punteggio, [generi]).
                f_out.write(f"lettura_utente({id_manga}, '{titolo}', {stato_lettura}, {punteggio_utente}, {generi}).\n")

    print(f"\n✅ Knowledge Base Prolog salvata come '{output_pl_path}'!")

# === MAIN: definisce i percorsi dei file e avvia la generazione della KB ===
if __name__ == '__main__':
    # Base dataset path
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'DATASET'))
    mangalist_path = os.path.join(base_dir, 'mangalist.csv')
    top_manga_path = os.path.join(base_dir, 'top_manga.csv')

    # Output directory per la KB Prolog
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'KB'))
    os.makedirs(output_dir, exist_ok=True)
    output_pl_path = os.path.join(output_dir, 'knowledge_base.pl')

    # Avvia la generazione
    genera_kb_prolog(mangalist_path, top_manga_path, output_pl_path)
