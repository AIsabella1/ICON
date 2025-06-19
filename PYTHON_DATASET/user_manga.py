import requests #usato per effettuare le richieste HTTP (per le API)
import secrets  #usato per generare stringhe casuali sicure (usato nel PKCE)
import csv  #usato per scrivere e salvare file in formato CSV
import time #usato per gestire pause tra richieste (rate limiting)
import string   #usato per creare il code_verifier (PKCE)
import webbrowser   #usato per aprire automaticamente un URL nel browser
from http.server import HTTPServer, BaseHTTPRequestHandler  #usato per creare il server locale per ricevere l'OAuth code
import urllib.parse #usato per costruire URL con parametri
import pandas as pd #usato per manipolare il file CSV
import os   #usato per gestire percorsi e directory nel filesystem

#credenziali dell'applicazione, ottenute dal sito myanimelist.net/apiconfig
#ID dell'applicazione fornito da MAL
CLIENT_ID = '823135212a297d25238a81ee65b9e53b'
#secret key privata (tecnicamente da non condividere pubblicamente la lascio nel progetto cosi da poterlo utilizzare senza registrarsi)
CLIENT_SECRET = '5ce0b51e70b4df89c3bc9d9e7102755e46cb679150fc99cb4a0a95a6dd1cdbd1'
#URL dove ricevere la risposta OAuth
REDIRECT_URI = 'http://localhost:8080'

#crea un codice sicuro alfanumerico usato nel PKCE per proteggere lo scambio del token
def generate_code_verifier(length=64):
    chars = string.ascii_letters + string.digits + "-._~"
    return ''.join(secrets.choice(chars) for _ in range(length))

#server locale per catturare il codice di autorizzazione, quando MyAnimeList reindirizza al browser, questo intercetta la richiesta e salva il codice
class OAuthCallbackHandler(BaseHTTPRequestHandler):
    #valore condiviso per salvare il codice
    authorization_code = None
    def do_GET(self):
        #analizza l'URL della richiesta ricevuta
        parsed_path = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_path.query)
        #estrae il parametro 'code'
        if 'code' in params:
            OAuthCallbackHandler.authorization_code = params['code'][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h1>Autorizzazione completata. Chiudi questa finestra.</h1>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h1>Errore codice mancante.</h1>")

#costruisce l’URL di autorizzazione e lo apre nel browser dell’utente
def open_authorization_url(code_verifier):
    auth_url = (f"https://myanimelist.net/v1/oauth2/authorize?"f"response_type=code&client_id={CLIENT_ID}&state=1234&"f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"f"code_challenge={code_verifier}&code_challenge_method=plain")
    print("\nSto aprendo il browser per autorizzare...")
    webbrowser.open(auth_url)

#scambio del codice per ottenere un token di accesso, fa una richiesta(una POST) per ottenere l'access token da MyAnimeList dopo l'autenticazione dell'utente
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
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.post(token_url, data=data, headers=headers)
    if response.status_code == 200:
        print("Access Token ottenuto con successo.")
        return response.json()['access_token']
    else:
        print("Errore durante il recupero dell'access token:")
        print(response.status_code, response.text)
        return None

#recupero della lista manga dell’utente (ho impostato il limite a 25k cosi da poter estrarre liste come quelle dell'utente Stark700)
def get_user_mangalist(username, access_token, max_manga=25000):
    base_url = f'https://api.myanimelist.net/v2/users/{username}/mangalist'
    headers = {
        #usa l’access token per interrogare l’endpoint dell’utente
        'Authorization': f'Bearer {access_token}'
    }
    all_manga = []
    #massimo per singola richiesta, altrimenti il sito blocca la richiesta e/o dispositivo momentaneamente 
    limit = 100
    fields = "id,title,genres,list_status{score,status}"

    #fino a max_manga, usando la paginazione via offset
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
                    #se non c'è list_status, salta il manga, questo avviene per quei manga che attualmente non possono essere estratti da MAL
                    continue
                #estrae ID, titolo, genere, punteggio e stato per ogni manga
                manga_id = node.get('id', '')
                title = node.get('title', '')
                genres_list = node.get('genres', [])
                genres = ", ".join([genre['name'] for genre in genres_list])
                score = list_status.get('score', '')
                status = list_status.get('status', '')

                all_manga.append({'ID': manga_id,'Titolo': title,'Generi': genres,'Punteggio': score,'Stato': status})
            print(f"Recuperati {len(data)} manga da offset {offset}")
        else:
            print(f"Errore: {response.status_code}")
            print(response.text)
            break

        #aspetta 1 secondo tra le richieste per evitare rate-limit. Anche per evitare che il dispositivo venga contrassegnato come possibile Bot, bloccando le possibili richieste per non si sa quante ore.
        time.sleep(1)

    print(f"\nTotale manga recuperati per {username}: {len(all_manga)}")
    return all_manga

#slvataggio del dataset in CSV, salva l’intera lista di manga in un file CSV nella cartella DATASET
def save_to_csv(manga_list, filename='mangalist.csv', folder='DATASET'):
    #crea la cartella se non esiste
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['ID', 'Titolo', 'Generi', 'Punteggio', 'Stato'])
        writer.writeheader()
        writer.writerows(manga_list)
    print(f"\nFile CSV salvato come '{filepath}' con {len(manga_list)} manga.")

#main
if __name__ == '__main__':
    #chiede l'username
    username = input("Inserisci il nome utente di MyAnimeList: ")
    code_verifier = generate_code_verifier()
    #avvia l’autenticazione (OAuth)
    open_authorization_url(code_verifier)
    print("In attesa del codice di autorizzazione...")

    #avvia il server HTTP per ricevere il codice OAuth
    with HTTPServer(('localhost', 8080), OAuthCallbackHandler) as httpd:
        httpd.handle_request()

    auth_code = OAuthCallbackHandler.authorization_code
    if auth_code:
        #ottiene il token
        access_token = get_access_token(auth_code, code_verifier)
        if access_token:
            #recupera la lista manga dell'utente
            manga_data = get_user_mangalist(username, access_token)
            #salva tutto in CSV.
            save_to_csv(manga_data)
            input_csv = 'mangalist.csv'
    else:
        print("Autorizzazione non completata.")