# --- Librerie necessarie ---
import requests                # Per effettuare chiamate HTTP alle API
import base64                  # (Importata ma non usata qui) per codifiche base64
import secrets                 # Per generare stringhe sicure (PKCE)
import hashlib                 # (Importata ma non usata qui) per hashing
import csv                     # Per scrivere i dati in formato CSV
import time                    # Per rate limiting tra richieste API
import string                  # Per creare code_verifier
import webbrowser              # Per aprire automaticamente l'URL nel browser
from http.server import HTTPServer, BaseHTTPRequestHandler  # Per ricevere il codice OAuth
from urllib.parse import urlparse, parse_qs                 # Per analizzare URL e parametri
import urllib.parse            # Per costruire e codificare URL
import pandas as pd            # Per gestire e filtrare file CSV
import os                      # Per gestire percorsi file e directory

# --- Credenziali dell'applicazione ---
CLIENT_ID = '823135212a297d25238a81ee65b9e53b'  # ID applicazione registrata su MAL
CLIENT_SECRET = '5ce0b51e70b4df89c3bc9d9e7102755e46cb679150fc99cb4a0a95a6dd1cdbd1'  # Chiave segreta
REDIRECT_URI = 'http://localhost:8080'  # URI di redirect registrato su MAL

# --- Genera code_verifier per PKCE ---
def generate_code_verifier(length=64):
    chars = string.ascii_letters + string.digits + "-._~"
    return ''.join(secrets.choice(chars) for _ in range(length))

# --- Server HTTP per intercettare la redirect OAuth ---
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    authorization_code = None

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_path.query)

        if 'code' in params:
            OAuthCallbackHandler.authorization_code = params['code'][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h1>Autorizzazione completata! Puoi chiudere questa finestra.</h1>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h1>Errore: codice mancante!</h1>")

# --- Passo 1: Apertura URL per autorizzazione via browser ---
def open_authorization_url(code_verifier):
    auth_url = (
        f"https://myanimelist.net/v1/oauth2/authorize?"
        f"response_type=code&client_id={CLIENT_ID}&state=1234&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"code_challenge={code_verifier}&code_challenge_method=plain"
    )
    print("\nAprendo il browser per autorizzare...")
    webbrowser.open(auth_url)

# --- Passo 2: Scambio del codice per ottenere l'access token ---
def get_access_token(auth_code, code_verifier):
    token_url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'code_verifier': code_verifier
    }
    print("Payload inviato:")
    print(data)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.post(token_url, data=data, headers=headers)

    if response.status_code == 200:
        print("Access Token ottenuto con successo!")
        return response.json()['access_token']
    else:
        print("Errore durante il recupero dell'access token:")
        print(response.status_code, response.text)
        return None

# --- Passo 3: Recupero della lista manga di un utente ---
def get_user_mangalist(username, access_token, max_manga=2000):
    base_url = f'https://api.myanimelist.net/v2/users/{username}/mangalist'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    all_manga = []
    limit = 100  # massimo per singola richiesta

    fields = "id,title,genres,list_status{score,status}"

    for offset in range(0, max_manga, limit):
        params = {
            'limit': limit,
            'offset': offset,
            'fields': fields
        }
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json().get('data', [])
            if not data:
                print(f"Fine dei dati a offset {offset}")
                break
            for entry in data:
                node = entry.get('node', {})
                list_status = entry.get('list_status', {})

                if not list_status:
                    # Se non c'è list_status, salta il manga
                    continue

                manga_id = node.get('id', '')
                title = node.get('title', '')
                genres_list = node.get('genres', [])
                genres = ", ".join([genre['name'] for genre in genres_list])
                score = list_status.get('score', '')
                status = list_status.get('status', '')

                all_manga.append({
                    'ID': manga_id,
                    'Titolo': title,
                    'Generi': genres,
                    'Punteggio': score,
                    'Stato': status
                })

            print(f"Recuperati {len(data)} manga da offset {offset}")
        else:
            print(f"Errore: {response.status_code}")
            print(response.text)
            break

        time.sleep(1)  # Rispetta i limiti API

    print(f"\nTotale manga recuperati per {username}: {len(all_manga)}")
    return all_manga

# --- Passo 4: Salvataggio dei dati in CSV ---
def save_to_csv(manga_list, filename='mangalist.csv', folder='DATASET'):
    # Crea la cartella se non esiste
    os.makedirs(folder, exist_ok=True)

    # Percorso completo file
    filepath = os.path.join(folder, filename)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['ID', 'Titolo', 'Generi', 'Punteggio', 'Stato'])
        writer.writeheader()
        writer.writerows(manga_list)
    print(f"\nFile CSV salvato come '{filepath}' con {len(manga_list)} manga.")

# --- Utility: separa il file CSV per stato ---
def split_manga_by_status(input_csv_path, folder='DATASET'):
    # Crea la cartella se non esiste
    os.makedirs(folder, exist_ok=True)

    # Carica il file
    df = pd.read_csv(input_csv_path)

    # Crea una mappa tra status e nomi file
    file_names = {
        'reading': 'mangalist_reading.csv',
        'completed': 'mangalist_completed.csv',
        'on_hold': 'mangalist_on_hold.csv',
        'dropped': 'mangalist_dropped.csv',
        'plan_to_read': 'mangalist_plan_to_read.csv'
    }

    # Per ogni status crea un file CSV separato
    for status, file_name in file_names.items():
        filtered_df = df[df['Stato'] == status]
        filepath = os.path.join(folder, file_name)
        if not filtered_df.empty:
            filtered_df.to_csv(filepath, index=False)
            print(f"Creato il file: {filepath} con {len(filtered_df)} manga.")
        else:
            print(f"Nessun manga trovato con stato '{status}', file non creato.")


# --- Main script ---
if __name__ == '__main__':
    username = input("Inserisci il nome utente di MyAnimeList: ")
    code_verifier = generate_code_verifier()
    open_authorization_url(code_verifier)
    print("In attesa del codice di autorizzazione...")
    with HTTPServer(('localhost', 8080), OAuthCallbackHandler) as httpd:
        httpd.handle_request()
    auth_code = OAuthCallbackHandler.authorization_code
    if auth_code:
        access_token = get_access_token(auth_code, code_verifier)
        if access_token:
            manga_data = get_user_mangalist(username, access_token)
            save_to_csv(manga_data)
            input_csv = 'mangalist.csv'  # Modifica qui se il file ha un altro nome
    else:
        print("Autorizzazione non completata.")
