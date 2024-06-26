import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import webbrowser

# Function to read secrets from secrets.txt
def read_secrets(file_path='secrets.txt'):
    secrets = {}
    with open(file_path, 'r') as file:
        for line in file:
            print(f"Processing line: {line.strip()}")
            parts = line.strip().split('-')
            if len(parts) == 2:
                name, value = parts
                secrets[name] = value
            else:
                print(f"Skipping invalid line: {line.strip()}")
    return secrets

# Read secrets
secrets = read_secrets()
print("Secrets loaded:", secrets)
CLIENT_ID = secrets['CLIENT_ID']
CLIENT_SECRET = secrets['CLIENT_SECRET']
REDIRECT_URI = secrets['REDIRECT_URI']

# Tidal OAuth endpoints
AUTHORIZATION_BASE_URL = 'https://auth.tidal.com/v1/oauth2/authorize'
TOKEN_URL = 'https://auth.tidal.com/v1/oauth2/token'

# Playlist details
PLAYLIST_NAME = 'Beautiful Irish & Gaelic Vocals'
PLAYLIST_DESCRIPTION = 'A collection of Irish and Gaelic songs with beautiful, chilling vocals.'

# List of songs to add to the playlist (song title and artist)
SONGS = [
    ("Oró Sé do Bheatha 'Bhaile", "Sinéad O'Connor"),
    ("Siúil A Rún", "Clannad"),
    ("Níl Sé’n Lá", "Celtic Woman"),
    ("Danny Boy", "Eva Cassidy"),
    ("The Parting Glass", "The High Kings"),
    ("Mná na hÉireann", "Kate Bush"),
    ("Dúlamán", "Altan"),
    ("She Moved Through the Fair", "Loreena McKennitt"),
    ("An Raibh Tú ar an gCarraig?", "Enya"),
    ("Misty Mountains", "The Gothard Sisters"),
    ("Wild Mountain Thyme", "The Chieftains & Van Morrison"),
    ("Taimse Im’ Chodladh", "Iarla Ó Lionáird"),
    ("Caoineadh Cú Chulainn", "The Chieftains"),
    ("Fear a' Bhàta", "Julie Fowlis"),
    ("An Mhaighdean Mhara", "Clannad")
]

def log_response(response):
    print("Status Code:", response.status_code)
    print("Response Body:", response.json())

# Step 1: Redirect user to Tidal for authorization
oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
authorization_url, state = oauth.authorization_url(AUTHORIZATION_BASE_URL)

print('Please go to this URL and authorize access:', authorization_url)
webbrowser.open(authorization_url)

# Step 2: Get the authorization verifier code from the callback URL
redirect_response = input('Paste the full redirect URL here: ')

# Step 3: Fetch the access token
try:
    token = oauth.fetch_token(
        TOKEN_URL,
        authorization_response=redirect_response,
        client_secret=CLIENT_SECRET
    )
except Exception as e:
    print("Error fetching token:", str(e))
    exit()

# Step 4: Use the access token to access the Tidal API
BASE_URL = 'https://api.tidal.com/v1/'

def create_playlist():
    url = BASE_URL + 'playlists'
    headers = {
        'Authorization': f'Bearer {token["access_token"]}'
    }
    data = {
        'title': PLAYLIST_NAME,
        'description': PLAYLIST_DESCRIPTION,
        'type': 'PLAYLIST'
    }
    response = requests.post(url, headers=headers, json=data)
    log_response(response)
    response.raise_for_status()
    return response.json()['uuid']

def search_track(title, artist):
    url = BASE_URL + 'search/tracks'
    headers = {
        'Authorization': f'Bearer {token["access_token"]}'
    }
    params = {
        'query': f'{title} {artist}',
        'limit': 1
    }
    response = requests.get(url, headers=headers, params=params)
    log_response(response)
    response.raise_for_status()
    results = response.json()['items']
    if results:
        return results[0]['id']
    return None

def add_tracks_to_playlist(playlist_id, track_ids):
    url = f'{BASE_URL}playlists/{playlist_id}/items'
    headers = {
        'Authorization': f'Bearer {token["access_token"]}'
    }
    data = {
        'trackIds': ','.join(map(str, track_ids))
    }
    response = requests.post(url, headers=headers, json=data)
    log_response(response)
    response.raise_for_status()

def main():
    playlist_id = create_playlist()
    track_ids = []
    for title, artist in SONGS:
        track_id = search_track(title, artist)
        if track_id:
            track_ids.append(track_id)
        else:
            print(f'Track not found: {title} by {artist}')
    add_tracks_to_playlist(playlist_id, track_ids)
    print(f'Playlist "{PLAYLIST_NAME}" created successfully!')

if __name__ == '__main__':
    main()
