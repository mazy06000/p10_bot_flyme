import sys
sys.path.append('../p10_bot_flyme')

import aiounittest

from botbuilder.core import ConversationState, MemoryStorage, TurnContext
from botbuilder.core.adapters import TestAdapter
from botbuilder.dialogs import DialogSet, DialogTurnStatus
from botbuilder.dialogs.prompts import TextPrompt

from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext
from booking_details import BookingDetails
from flight_booking_recognizer import FlightBookingRecognizer
from helpers.luis_helper import LuisHelper


class TestLuis(aiounittest.AsyncTestCase):

    async def execute_luis_query(self):
        luis_recognizer = FlightBookingRecognizer

        async def exec_test(turn_context: TurnContext):
            intent, result = await LuisHelper.execute_luis_query(
                luis_recognizer, turn_context
            )

            await turn_context.send_activity(
                {"intent": intent,
                "booking_details": result.__dict__}
            )

        adapter = TestAdapter(exec_test)

        await adapter.test(
            "I want to book a flight from Nice to Paris",
            {"intent": "book",
            "booking_details": BookingDetails().__dict__}
        )