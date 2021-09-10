import requests
from secrets import spotify_token

class SpotifyClient(object):
    def __init__(self, api_token):
        self.api_token = api_token

    def get_current_song(self):
        query = "https://api.spotify.com/v1/me/player/currently-playing?market=GB"
        response = requests.get(
            query,
            headers={
                "Authorization": f"Bearer {spotify_token}"
            }
        )
        response_json = response.json()

        track_id = response_json['item']['id']
        track_name = response_json['item']['name']
        artist_name = response_json['item']['artists']

        link = response_json['item']['external_urls']['spotify']

        current_track_info = {
            "id": track_id,
            "track_name": track_name,
            "artist": artist_name[0]['name'],
            "link": link
        }

        return current_track_info

    def search_song(self, artist, track):
        query = f"https://api.spotify.com/v1/search?q=track%3A{track}+artist%3A{artist}&type=track&offset=0&limit=20"
        response = requests.get(
            query,
             headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {spotify_token}"
             }
        )
        response_json = response.json()
        results = response_json["tracks"]["items"]
        if results:
            return results[0]["id"]
        else:
            raise Exception(f"No song found for {artist} = {track}")

    def add_song_to_spotify(self, song_id):
        url = "https://api.spotify.com/v1/me/tracks"
        response = requests.put(
            url,
            json={
                "ids": [song_id]
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {spotify_token}"
            }
        )
        return response.ok