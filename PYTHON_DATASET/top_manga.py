# --- Librerie necessarie ---
import requests             # Per effettuare chiamate HTTP alle API
import webbrowser           # Per aprire l'URL di autorizzazione nel browser
import secrets              # Per generare stringhe sicure (PKCE)
import string               # Per costruire caratteri validi per il code_verifier
from http.server import HTTPServer, BaseHTTPRequestHandler  # Server HTTP locale per ricevere l'autorizzazione
import urllib.parse         # Per analizzare e costruire URL
import csv                  # Per salvare i dati in formato CSV
import time                 # Per aggiungere pause tra le richieste API
import os                   # Per operazioni su file e cartelle

# --- CONFIGURAZIONE ---
CLIENT_ID = '823135212a297d25238a81ee65b9e53b'  # ID applicazione registrata su MAL
CLIENT_SECRET = '5ce0b51e70b4df89c3bc9d9e7102755e46cb679150fc99cb4a0a95a6dd1cdbd1'  # Chiave segreta
REDIRECT_URI = 'http://localhost:8080'  # URI di redirect registrato su MAL

# --- GENERA CODE VERIFIER per PKCE ---
def generate_code_verifier(length=64):
    chars = string.ascii_letters + string.digits + "-._~"
    return ''.join(secrets.choice(chars) for _ in range(length))

# --- SERVER HTTP per ricevere il CODE di autorizzazione ---
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    authorization_code = None # Variabile di classe per salvare il codice

    def do_GET(self):
        # Parse dell'URL ricevuto dal redirect
        parsed_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_path.query)

        # Estrazione del parametro 'code'
        if 'code' in params:
            OAuthCallbackHandler.authorization_code = params['code'][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h1>Autorizzazione completata! Puoi chiudere questa finestra.</h1>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h1>Errore: codice mancante!</h1>")

# --- PASSO 1: Apertura URL per autorizzazione via browser ---
def open_authorization_url(code_verifier):
    auth_url = (
        f"https://myanimelist.net/v1/oauth2/authorize?"
        f"response_type=code&client_id={CLIENT_ID}&state=1234&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"code_challenge={code_verifier}&code_challenge_method=plain"
    )
    print("\nAprendo il browser per autorizzare...")
    webbrowser.open(auth_url)

# --- PASSO 2: Ottenimento access token dal codice ---
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

# --- Richiesta manga dalla classifica ---
def get_top_manga(access_token, max_manga=1000):
    api_url = "https://api.myanimelist.net/v2/manga/ranking"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    all_manga = []
    limit = 500 # MAL permette un massimo di 500 per richiesta

    fields = (
        "id,title,mean,rank,popularity,status,genres,authors{first_name,last_name}"
    )

    # Pagina i risultati ogni 500 voci
    for offset in range(0, max_manga, limit):
        params = {
            "ranking_type": "manga",
            "limit": limit,
            "offset": offset,
            "fields": fields
        }
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json().get('data', [])
            all_manga.extend(data)
            print(f"Recuperati {len(data)} manga da offset {offset}")
        else:
            print(f"Errore: {response.status_code}")
            print(response.text)
            break
        time.sleep(1)  # Rispetta il rate limit dell’API
    print(f"\nTotale manga recuperati: {len(all_manga)}")
    return all_manga

# --- Salva i dati manga in un file CSV ---
def save_manga_to_csv(manga_list, filename="top_manga.csv", folder="DATASET"):
    # Crea la cartella se non esiste
    os.makedirs(folder, exist_ok=True)

    # Percorso completo file
    filepath = os.path.join(folder, filename)

    with open(filepath, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        # Scrive l'intestazione
        writer.writerow([
            "ID", "Titolo", "Generi", "Punteggio Medio",
            "Rank", "Popolarità", "Stato", "Autori"
        ])
        
        for manga in manga_list:
            node = manga['node']
            manga_id = node.get('id', '')
            title = node.get('title', '')
            genres_list = node.get('genres', [])
            genres = ", ".join([genre['name'] for genre in genres_list])
            mean = node.get('mean', '')
            rank = node.get('rank', '')
            popularity = node.get('popularity', '')
            status = node.get('status', '')

            authors_list = node.get('authors', [])
            authors = ", ".join([f"{author['node']['first_name']} {author['node']['last_name']}" for author in authors_list])

            writer.writerow([
                manga_id, title, genres, mean,
                rank, popularity, status, authors
            ])
    
    print(f"\nFile CSV salvato come '{filepath}'")

# --- MAIN: esecuzione del processo completo ---
def main():
    code_verifier = generate_code_verifier()

    # Avvia il server HTTP locale su porta 8080
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, OAuthCallbackHandler)

    open_authorization_url(code_verifier)

    print("In attesa dell'autorizzazione dal browser...")
    while OAuthCallbackHandler.authorization_code is None:
        httpd.handle_request()  # Attende finché non riceve il codice

    httpd.server_close()

    auth_code = OAuthCallbackHandler.authorization_code
    print(f"\nCodice autorizzazione ricevuto: {auth_code}\n")

    access_token = get_access_token(auth_code, code_verifier)

    if access_token:
        manga_data = get_top_manga(access_token)
        save_manga_to_csv(manga_data)

# --- Entry point ---
if __name__ == "__main__":
    main()
