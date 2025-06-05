# Librerie necessarie
import requests                # Per effettuare richieste HTTP (usato per chiamare le API)
import secrets                 # Per generare stringhe casuali sicure (usato in PKCE)
import csv                     # Per scrivere e salvare file in formato CSV
import time                    # Per gestire pause tra richieste (rate limiting)
import string                  # Per creare il code_verifier (PKCE)
import webbrowser              # Per aprire automaticamente un URL nel browser
from http.server import HTTPServer, BaseHTTPRequestHandler  # Server locale per ricevere l'OAuth code
import urllib.parse            # Per costruire URL con parametri
import pandas as pd            # Per manipolare file CSV
import os                      # Per gestire percorsi e directory nel filesystem

# Credenziali dell'applicazione
CLIENT_ID = '823135212a297d25238a81ee65b9e53b'  # ID dell'applicazione registrata su MAL
CLIENT_SECRET = '5ce0b51e70b4df89c3bc9d9e7102755e46cb679150fc99cb4a0a95a6dd1cdbd1'  # Secret key privata (tecnicamente da non condividere pubblicamente)
REDIRECT_URI = 'http://localhost:8080'  # URL dove ricevere la risposta OAuth

# Crea un codice sicuro alfanumerico usato nel flusso PKCE per proteggere lo scambio del token
def generate_code_verifier(length=64):
    chars = string.ascii_letters + string.digits + "-._~"
    return ''.join(secrets.choice(chars) for _ in range(length))

# Server locale per catturare il codice di autorizzazione, quando MyAnimeList reindirizza al browser, questo handler intercetta la richiesta e salva il codice
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    authorization_code = None   # Valore condiviso per salvare il codice

    def do_GET(self):
        # Analizza l'URL della richiesta ricevuta dopo il login su MAL
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

# Costruisce l’URL di autorizzazione e lo apre nel browser dell’utente
def open_authorization_url(code_verifier):
    auth_url = (
        f"https://myanimelist.net/v1/oauth2/authorize?"
        f"response_type=code&client_id={CLIENT_ID}&state=1234&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"code_challenge={code_verifier}&code_challenge_method=plain"
    )
    print("\nAprendo il browser per autorizzare...")
    webbrowser.open(auth_url)

# Scambio del codice per ottenere un token di accesso, fa una richiesta POST per ottenere l'access token da MyAnimeList dopo l'autenticazione dell'utente
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

# Recupero della lista manga dell’utente
def get_user_mangalist(username, access_token, max_manga=25000):
    base_url = f'https://api.myanimelist.net/v2/users/{username}/mangalist'
    headers = {
        'Authorization': f'Bearer {access_token}'   # Usa l’access token per interrogare l’endpoint dell’utente
    }
    all_manga = []
    limit = 100  # massimo per singola richiesta

    fields = "id,title,genres,list_status{score,status}"

    # Fino a max_manga, usando la paginazione via offset
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

                # Estrae ID, titolo, genere, punteggio e stato per ciascun manga
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

        time.sleep(1)  # Aspetta 1 secondo tra le richieste per evitare rate-limit.

    print(f"\nTotale manga recuperati per {username}: {len(all_manga)}")
    return all_manga

# Salvataggio del dataset in CSV, salva l’intera lista di manga in un file CSV nella cartella DATASET
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

# Main Script
if __name__ == '__main__':
    username = input("Inserisci il nome utente di MyAnimeList: ") # Chiede l'username
    code_verifier = generate_code_verifier()
    open_authorization_url(code_verifier) # Avvia l’autenticazione (OAuth)
    print("In attesa del codice di autorizzazione...")

    # Avvia il server HTTP per ricevere il codice OAuth
    with HTTPServer(('localhost', 8080), OAuthCallbackHandler) as httpd:
        httpd.handle_request()

    auth_code = OAuthCallbackHandler.authorization_code
    if auth_code:
        access_token = get_access_token(auth_code, code_verifier) # Ottiene il token
        if access_token:
            manga_data = get_user_mangalist(username, access_token) # Recupera la lista manga
            save_to_csv(manga_data) # Salva tutto in CSV.
            input_csv = 'mangalist.csv' 
    else:
        print("Autorizzazione non completata.")