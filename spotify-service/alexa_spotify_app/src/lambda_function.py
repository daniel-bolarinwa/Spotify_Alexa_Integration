import logging
import prompts
import base64
import requests

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, 
    AbstractExceptionHandler,
    AbstractRequestInterceptor, 
    AbstractResponseInterceptor
)

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

from spotify_client import SpotifyClient
from get_secret import get_creds, store_token

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Built-in Intent Handlers

# Request Handler classes
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")
        handler_input.response_builder.speak(prompts.WELCOME_MESSAGE).ask(
            prompts.HELP_MESSAGE)
        return handler_input.response_builder.response

class LikeSongIntentHandler(AbstractRequestHandler):
    CLIENT_ID, CLIENT_SECRET = get_creds("client-credentials")
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("LaunchRequest")(handler_input) or is_intent_name("LikeSongsIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LikeSongIntentHandler")
        
        logger.info('setting the secret name to retrieve from secrets manager')
        
        spotify_token = get_creds("spotify_access_token")
        validated_token = self.test_api(spotify_token)
        
        logger.debug('creating spotify client object to perform API operations')
        spotify_client = SpotifyClient(validated_token)
        
        logger.debug('getting users current track information')
        current_track_info = spotify_client.get_current_song()
        current_track_song_name = current_track_info['track_name']
        current_track_artist = current_track_info['artist']
        
        logger.info(f"user is currently listening to {current_track_song_name} by {current_track_artist}")
        spotify_song_id = spotify_client.search_song(current_track_artist, current_track_song_name)
        
        if spotify_song_id:
            logger.debug('adding users current playing track to liked songs')
            added_song = spotify_client.add_song_to_spotify(spotify_song_id)
            if added_song:
                logger.info(f"Added {current_track_artist} - {current_track_song_name} to your Spotify Liked Songs")
        
        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.LIKE_SONG_MESSAGE].format(f"{current_track_song_name} by {current_track_artist}")

        handler_input.response_builder.speak(speech).set_card(SimpleCard(data[prompts.SKILL_NAME], f"{current_track_song_name} by {current_track_artist}"))
        return handler_input.response_builder.response
        
    def test_api(self, token):
        query = "https://api.spotify.com/v1/me/player/currently-playing?market=GB"
        response = requests.get(
            query,
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        response_json = response.json()
        if 'error' in response_json:
            logger.debug('token has expired, now refreshing token')

            refresh_token = get_creds("spotify_access_refresh_token")

            AUTH_URL = 'https://accounts.spotify.com/api/token'

            secretString = f'{self.CLIENT_ID}:{self.CLIENT_SECRET}'
            secretStringBytes = secretString.encode('ascii')
            base64SecretStringBytes = base64.b64encode(secretStringBytes)
            base64SecretString = base64SecretStringBytes.decode('ascii')

            # POST
            auth_response = requests.post(
                AUTH_URL, 
                headers={
                    "Authorization": f"Basic {base64SecretString}"
                },
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token
                }
            )

            # convert the response to JSON
            auth_response_data = auth_response.json() # TODO: error handle this response too

            # save the access token
            spotify_auth_token = auth_response_data['access_token']

            logger.info('attempt to authenticate with spotify in order to retrieve the access token was successful')
            response = requests.get(
                query,
                headers={
                    "Authorization": f"Bearer {spotify_auth_token}"
                }
            )

            response_json = response.json() # TODO: error handle this response in case it is not a 200
            store_token(spotify_auth_token, refresh_token)
            return spotify_auth_token
        else:
            return token


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.HELP_MESSAGE]
        reprompt = data[prompts.HELP_REPROMPT]
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(SimpleCard(data[prompts.SKILL_NAME], speech))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.STOP_MESSAGE]
        handler_input.response_builder.speak(speech)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.FALLBACK_MESSAGE]
        reprompt = data[prompts.FALLBACK_REPROMPT]
        handler_input.response_builder.speak(speech).ask(reprompt)
        return handler_input.response_builder.response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak(prompts.EXCEPTION_MESSAGE).ask(prompts.HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(LikeSongIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# Register request and response interceptors
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
