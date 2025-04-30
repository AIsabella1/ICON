import requests
import secrets
import string
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os
import time
import csv

# --- CREDENZIALI ---
CLIENT_ID = '823135212a297d25238a81ee65b9e53b'
CLIENT_SECRET = '5ce0b51e70b4df89c3bc9d9e7102755e46cb679150fc99cb4a0a95a6dd1cdbd1'
REDIRECT_URI = 'http://localhost:8080'

# --- GENERA CODE VERIFIER ---
def generate_code_verifier(length=64):
    chars = string.ascii_letters + string.digits + "-._~"
    return ''.join(secrets.choice(chars) for _ in range(length))

# --- SERVER HTTP PER RICEVERE IL CODE ---
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

# --- APRI BROWSER PER AUTORIZZARE ---
def open_authorization_url(code_verifier):
    auth_url = (
        f"https://myanimelist.net/v1/oauth2/authorize?"
        f"response_type=code&client_id={CLIENT_ID}&state=1234&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"code_challenge={code_verifier}&code_challenge_method=plain"
    )
    print("\nAprendo il browser per autorizzare...")
    webbrowser.open(auth_url)

# --- OTTIENI ACCESS TOKEN ---
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
    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        print("✅ Access Token ottenuto con successo!")
        return response.json()['access_token']
    else:
        print("Errore durante il recupero dell'access token:")
        print(response.status_code, response.text)
        return None

# --- SCARICA LA LISTA MANGA CON DATI ESTESI ---
def get_user_mangalist_extended(username, access_token, max_manga=1000):
    base_url = f'https://api.myanimelist.net/v2/users/{username}/mangalist'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    all_manga = []
    limit = 100

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
                    continue

                manga_id = node.get('id', '')
                title = node.get('title', '')
                genres_list = node.get('genres', [])
                genres = ", ".join([genre['name'] for genre in genres_list])
                score = list_status.get('score', '')
                user_status = list_status.get('status', '')

                # Recupero extra: mean, rank, popularity
                manga_extra_url = f'https://api.myanimelist.net/v2/manga/{manga_id}?fields=mean,rank,popularity'
                extra_response = requests.get(manga_extra_url, headers=headers)

                if extra_response.status_code == 200:
                    extra_data = extra_response.json()
                    mean_score = extra_data.get('mean', '')
                    rank = extra_data.get('rank', '')
                    popularity = extra_data.get('popularity', '')
                else:
                    mean_score = ''
                    rank = ''
                    popularity = ''

                all_manga.append({
                    'ID': manga_id,
                    'Titolo': title,
                    'Generi': genres,
                    'Punteggio_Utente': score,
                    'Stato_Utente': user_status,
                    'Punteggio_Medio': mean_score,
                    'Rank': rank,
                    'Popolarita': popularity
                })

            print(f"✅ Recuperati {len(data)} manga da offset {offset}")
        else:
            print(f"Errore API: {response.status_code}")
            print(response.text)
            break

        time.sleep(1)

    print(f"\nTotale manga recuperati per {username}: {len(all_manga)}")
    return all_manga

# --- SALVA TUTTO IN CSV ---
def save_to_csv(manga_list, filename='dataset_ml.csv', folder='DATASET'):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'ID', 'Titolo', 'Generi', 'Punteggio_Utente', 'Stato_Utente', 
            'Punteggio_Medio', 'Rank', 'Popolarita'
        ])
        writer.writeheader()
        writer.writerows(manga_list)
    print(f"\n✅ File salvato: '{filepath}' con {len(manga_list)} manga.")

# --- MAIN ---
if __name__ == '__main__':
    username = input("Inserisci il tuo username di MyAnimeList: ")
    code_verifier = generate_code_verifier()
    open_authorization_url(code_verifier)
    print("Attesa autorizzazione...")
    with HTTPServer(('localhost', 8080), OAuthCallbackHandler) as httpd:
        httpd.handle_request()
    auth_code = OAuthCallbackHandler.authorization_code
    if auth_code:
        access_token = get_access_token(auth_code, code_verifier)
        if access_token:
            manga_data = get_user_mangalist_extended(username, access_token)
            save_to_csv(manga_data)
    else:
        print("❌ Autorizzazione non completata.")
