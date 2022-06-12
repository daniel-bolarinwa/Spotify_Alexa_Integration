import string
import random
import logging
import requests
import base64
import webbrowser
from src.get_secret import get_creds, store_token
from django.shortcuts import render

CLIENT_ID, CLIENT_SECRET = get_creds("client-credentials")
REDIRECT_URI = "http://127.0.0.1:8000/authenticate"


def home(request):
    return render(request, 'index.html', context=None)


def authorise(request):
    letters = string.ascii_lowercase + string.digits + string.ascii_uppercase
    state = ''.join(random.choice(letters) for i in range(16))
    
    logging.debug('starting the spotify authorisation process')

    auth_url = 'https://accounts.spotify.com/authorize'

    auth_url += "?client_id=" + CLIENT_ID
    auth_url += "&response_type=code"
    auth_url += "&redirect_uri=" + REDIRECT_URI
    auth_url += "&show_dialog=true"
    auth_url += "&state=" + state
    auth_url += "&scope=user-read-currently-playing user-library-modify"

    webbrowser.open(auth_url)

    return render(request, 'authorise.html', context=None)


def authenticate(request):
    logging.debug('starting the spotify authentication process')

    code = request.GET.get('code')

    AUTH_URL = 'https://accounts.spotify.com/api/token'

    secretString = f'{CLIENT_ID}:{CLIENT_SECRET}'
    secretStringBytes = secretString.encode('ascii')
    base64SecretStringBytes = base64.b64encode(secretStringBytes)
    base64SecretString = base64SecretStringBytes.decode('ascii')

    # POST
    try:
        auth_response = requests.post(AUTH_URL, 
        headers={
            "Authorization": f"Basic {base64SecretString}"
        },
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI
        })
    except Exception:
        return render(request, 'auth_failed.html', context=None)

    # convert the response to JSON
    auth_response_data = auth_response.json()

    # save the access token
    try:
        spotify_auth_token = auth_response_data['access_token']
        spotify_refresh_token = auth_response_data['refresh_token']
    except KeyError:
        return render(request, 'auth_failed.html', context=None)

    logging.info('attempt to authenticate with spotify in order to retrieve the access token was successful')

    store_token(spotify_auth_token, spotify_refresh_token)
    return render(request, 'authorise.html', context=None)
