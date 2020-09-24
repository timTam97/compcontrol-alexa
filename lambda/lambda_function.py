import logging

import ask_sdk_core.utils as ask_utils
import auth
import requests
from ask_sdk_core.dispatch_components import (AbstractExceptionHandler,
                                              AbstractRequestHandler)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speak_output = "Try invoking me with a command."
        return handler_input.response_builder.speak(speak_output).response


class ParentPushbulletIntentHandler(AbstractRequestHandler):
    """Handler for all pushbulet-realted custom intents. """

    def __init__(self, action: str, intent_name: str):
        self.action = action
        self.intent_name = intent_name

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name(self.intent_name)(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        headers = {"Access-Token": auth.TOKEN, "Content-Type": "application/json"}
        data = (
            '{"body":"'
            + self.action
            + '","title":"'
            + auth.COMP_NAME
            + '","type":"note"}'
        )
        requests.post(
            "https://api.pushbullet.com/v2/pushes", data=data.encode(), headers=headers
        )
        return handler_input.response_builder.speak(
            '<audio src="soundbank://soundlibrary/musical/amzn_sfx_bell_short_chime_03"/>'
        ).response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Response:
        logger.error(exception, exc_info=True)
        speak_output = "Sorry, there has been an error. Please try again."
        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ParentPushbulletIntentHandler("sleep", "SleepIntent"))
sb.add_request_handler(ParentPushbulletIntentHandler("lock", "LockIntent"))
sb.add_request_handler(ParentPushbulletIntentHandler("hibernate", "HibernateIntent"))
sb.add_request_handler(ParentPushbulletIntentHandler("shut down", "ShutDownIntent"))
sb.add_request_handler(ParentPushbulletIntentHandler("open vnc", "OpenVNCIntent"))

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
