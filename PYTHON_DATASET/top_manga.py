import requests #usato per effettuare richieste HTTP (per API)
import webbrowser   #usato per aprire automaticamente un URL nel browser
import secrets  #usato per generare stringhe casuali sicure (in PKCE)
import string   #usato per creare il code_verifier (PKCE)
from http.server import HTTPServer, BaseHTTPRequestHandler  #usato per creare il server locale per ricevere l'OAuth code
import urllib.parse #usato per costruire URL con parametri
import csv  #usato per scrivere e salvare file in formato CSV
import time #usato per gestire pause tra richieste (rate limiting)
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
        #analizza l'URL della richiesta ricevuta dopo il login su MAL
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
            self.wfile.write(b"<h1>Errore: codice mancante.</h1>")

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

#estrae la classifica dei manga (Top 1000 dei manga, modificare max_manga permette di cambiare la Top estratta)
def get_top_manga(access_token, max_manga=1000):
    #richiama l’endpoint manga/ranking
    api_url = "https://api.myanimelist.net/v2/manga/ranking"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    all_manga = []
    #MAL permette un massimo di 500 per questo tipo di richiesta, diverso da quello della lista utente
    limit = 500 
    fields = ("id,title,mean,rank,popularity,status,genres,authors{first_name,last_name}")
    #paginazione tramite offset (ogni 500 risultati)
    for offset in range(0, max_manga, limit):
        params = {
            "ranking_type": "manga",
            "limit": limit,
            "offset": offset,
            #id, titolo, mean, rank, popolarità, status, generi, autori
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
        #aspetta 1 secondo tra le richieste per evitare rate-limit.
        time.sleep(1)  
    print(f"\nTotale manga recuperati: {len(all_manga)}")
    return all_manga

#salvataggio in CSV
def save_manga_to_csv(manga_list, filename="top_manga.csv", folder="DATASET"):
    #crea la cartella se non esiste
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        #scrive l'intestazione
        writer.writerow(["ID", "Titolo", "Generi", "Punteggio Medio","Rank", "Popolarità", "Stato", "Autori"])
        #salva
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
            writer.writerow([manga_id, title, genres, mean,rank, popularity, status, authors])
    
    print(f"\nFile CSV salvato come '{filepath}'")

#main
def main():
    #genera il code_verifier
    code_verifier = generate_code_verifier()

    #avvia il server
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, OAuthCallbackHandler)
    open_authorization_url(code_verifier)
    print("In attesa dell'autorizzazione dal browser...")
    while OAuthCallbackHandler.authorization_code is None:
        #attende finché non ottiene il codice
        httpd.handle_request()  
    httpd.server_close()
    auth_code = OAuthCallbackHandler.authorization_code 

    #ottiene l'access token
    access_token = get_access_token(auth_code, code_verifier)   

    if access_token:
        #scarica i manga top
        manga_data = get_top_manga(access_token)
        #salva il dataset
        save_manga_to_csv(manga_data)   

#main
if __name__ == "__main__":
    main()