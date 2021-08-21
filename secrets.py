# Make sure to fill in your spotify client_secret information
import requests

def test():

    CLIENT_ID = 'yourclientid'
    CLIENT_SECRET = 'yourclientsecret'

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
    access_token = auth_response_data['access_token']


    # spotify_token = ""
if __name__ == '__main__':
    test()