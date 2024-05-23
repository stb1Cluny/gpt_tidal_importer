#PSIT(Put Songs in Tidal) Flask App

""" TODO
- Multi-file - we don't need all these modules
through the whole program flow.
- Error handling - else print is nice but
errors need to be robust
- Add frontend to trigger auth flow. Can use
Flask debug mode for now.
- Eventually move auth to Tidal SDK node service
- CSRF state protection is not implemented correctly.
There's support for this built into Flask already.
 """

from os import urandom
import simplejson as json
import requests
import base64
import hashlib
import secrets
from urllib.parse import urlencode
from flask import Flask, request, redirect

app = Flask(__name__)

# Setting up app variables
def read_secrets(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    client_id = data["CLIENT_ID"]
    client_secret = data["CLIENT_SECRET"]
    redirect_uri = data["REDIRECT_URI"]
    
    return client_id, client_secret, redirect_uri

CLIENT_ID, CLIENT_SECRET, REDIRECT_URI = read_secrets("secrets.json")
AUTHORIZE_URL = 'https://login.tidal.com/oauth2/authorize'
TOKEN_URL = 'https://login.tidal.com/oauth2/token'

# PKCE - Generate a code verifier and code challenge
def generate_pkce_pair():
    code_verifier = secrets.token_urlsafe(128)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).rstrip(b'=').decode('utf-8')
    return code_verifier, code_challenge

code_verifier, code_challenge = generate_pkce_pair()

# Generate "state" token for CSRF protection
# Using os.urandom per Google here: 
# https://developers.google.com/identity/openid-connect/openid-connect?hl=en#python
def generate_state_token():
    state_token = hashlib.sha256(urandom(1024)).hexdigest()
    return state_token

CSRF_state_token = generate_state_token()

@app.route('/')
def home():
    # Redirect the user to Tidal's authorization page with PKCE
    query_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'r_usr w_usr',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
        'state': CSRF_state_token
    }
    auth_url = f"{AUTHORIZE_URL}?{urlencode(query_params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Handle the redirect and get the authorization code from the query parameters
    code = request.args.get('code')
    if not code:
        return 'Error: No authorization code provided', 400

    # Exchange the authorization code for an access token using PKCE
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code_verifier': code_verifier
    }
    response = requests.post(TOKEN_URL, data=token_data)
    
    if response.status_code != 200:
        return f"Error: {response.json()}", response.status_code

    # The response should contain the access token
    token_info = response.json()
    access_token = token_info.get('access_token')
    refresh_token = token_info.get('refresh_token')

    return f"Access Token: {access_token}<br>Refresh Token: {refresh_token}"

if __name__ == '__main__':
    # Step 2: Run the Flask web server to listen for the callback
    app.run(debug=True, port=5000)
