import os
from spotify_client import SpotifyClient
# from youtube_client import YoutubeClient
from secrets import spotify_token

def run():
    #youtube_client = YoutubeClient('creds/client_secret.json')
    spotify_client = SpotifyClient(spotify_token)
    #playlists = youtube_client.get_playlists()
    # for index, playlist in enumerate(playlists):
    #     print(f"{index}: {playlist.title}") gjgjggg
    # choice = int(input("Enter your choice: "))
    # chosen_playlist = playlists[choice]
    #print(f"you chose: {chosen_playlist.title}")
    #songs = youtube_client.get_videos_from_playlist(chosen_playlist.id)
    #rint(f"Attempting to add {len(songs)}")
    # for song in songs:
    #     spotify_song_id = spotify_client.search_song(song.artist, song.track)
    #     if spotify_song_id:
    #         added_song = spotify_client.add_song_to_spotify(spotify_song_id)
    #         if added_song:
    #             print(f"Added {song.artist} - {song.track} to your Spotify Liked Songs")

    current_track_info = spotify_client.get_current_song()
    current_track_song_name = current_track_info['track_name']
    current_track_artist = current_track_info['artist']

    print(f"user is currently listening to {current_track_song_name} by {current_track_artist}")

    spotify_song_id = spotify_client.search_song(current_track_artist, current_track_song_name)

    if spotify_song_id:
        added_song = spotify_client.add_song_to_spotify(spotify_song_id)
        if added_song:
            print(f"Added {current_track_artist} - {current_track_song_name} to your Spotify Liked Songs")

if __name__ == '__main__':
    run()
