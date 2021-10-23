import logging
from authenticate import authenticate
from spotify_client import SpotifyClient

def lambda_handler():#event, context):
    logging.info('setting the secret name to retrieve from secrets manager')
    secret_name = "client-credentials"
    spotify_token = authenticate(secret_name)

    logging.debug('creating spotify client object to perform API operations')
    spotify_client = SpotifyClient(spotify_token)

    logging.debug('getting users current track information')
    current_track_info = spotify_client.get_current_song(spotify_token)
    current_track_song_name = current_track_info['track_name']
    current_track_artist = current_track_info['artist']

    logging.info(f"user is currently listening to {current_track_song_name} by {current_track_artist}")

    spotify_song_id = spotify_client.search_song(current_track_artist, current_track_song_name, spotify_token)

    if spotify_song_id:
        logging.debug('adding users current playing track to liked songs')
        added_song = spotify_client.add_song_to_spotify(spotify_song_id, spotify_token)
        if added_song:
            logging.info(f"Added {current_track_artist} - {current_track_song_name} to your Spotify Liked Songs")

if __name__ == '__main__':
    lambda_handler()