from asyncio.windows_events import NULL

import logging
import requests
import base64
from spotify_client import SpotifyClient
from get_secret import get_creds, store_token

CLIENT_ID, CLIENT_SECRET = get_creds("client-credentials")

def lambda_handler(event, context):
    logging.info('setting the secret name to retrieve from secrets manager')
    spotify_token = get_creds("spotify_access_token")

    validated_token = test_api(spotify_token)

    logging.debug('creating spotify client object to perform API operations')
    spotify_client = SpotifyClient(validated_token)

    logging.debug('getting users current track information')
    current_track_info = spotify_client.get_current_song()
    current_track_song_name = current_track_info['track_name']
    current_track_artist = current_track_info['artist']

    logging.info(f"user is currently listening to {current_track_song_name} by {current_track_artist}")

    spotify_song_id = spotify_client.search_song(current_track_artist, current_track_song_name)

    if spotify_song_id:
        logging.debug('adding users current playing track to liked songs')
        added_song = spotify_client.add_song_to_spotify(spotify_song_id)
        if added_song:
            logging.info(f"Added {current_track_artist} - {current_track_song_name} to your Spotify Liked Songs")

def test_api(token):
    query = "https://api.spotify.com/v1/me/player/currently-playing?market=GB"
    response = requests.get(
        query,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    response_json = response.json()

    if 'error' in response_json:
        logging.debug('token has expired, now refreshing token')

        refresh_token = get_creds("spotify_access_refresh_token")

        AUTH_URL = 'https://accounts.spotify.com/api/token'

        secretString = f'{CLIENT_ID}:{CLIENT_SECRET}'
        secretStringBytes = secretString.encode('ascii')
        base64SecretStringBytes = base64.b64encode(secretStringBytes)
        base64SecretString = base64SecretStringBytes.decode('ascii')

        # POST
        auth_response = requests.post(AUTH_URL, 
        headers={
            "Authorization": f"Basic {base64SecretString}"
        },
        data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        })
        # convert the response to JSON
        auth_response_data = auth_response.json()

        # save the access token
        spotify_auth_token = auth_response_data['access_token']
        logging.info('attempt to authenticate with spotify in order to retrieve the access token was successful')

        response = requests.get(
        query,
        headers={
            "Authorization": f"Bearer {spotify_auth_token}"
        }
        )
        response_json = response.json()

        store_token(spotify_auth_token, refresh_token)
        return spotify_auth_token
    else:
        return token