import logging
import requests
from get_secret import get_creds

def authenticate(secret_name):
    logging.debug('starting the spotify authentication process')
    CLIENT_ID, CLIENT_SECRET = get_creds(secret_name)

    AUTH_URL = 'https://accounts.spotify.com/api/token'

    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    # convert the response to JSON
    auth_response_data = auth_response.json()

    # save the access token
    spotify_token = auth_response_data['access_token']
    logging.info('attempt to authenticate with spotify in order to retrieve the access token was successful')

    return spotify_token