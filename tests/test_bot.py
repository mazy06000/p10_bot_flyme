import aiounittest
import asynctest
import unittest
from botbuilder.core import ConversationState, MemoryStorage, TurnContext
from botbuilder.core.adapters import TestAdapter
from botbuilder.dialogs import DialogSet, DialogTurnStatus
from botbuilder.schema import Activity, ActivityTypes, Attachment
from botbuilder.dialogs.prompts import (
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext,
    TextPrompt,
)
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext
from dialogs.main_dialog import MainDialog
from dialogs.booking_dialog import BookingDialog
from booking_details import BookingDetails
from config import DefaultConfig
from flight_booking_recognizer import FlightBookingRecognizer
from helpers.luis_helper import LuisHelper
import json
import sys
sys.path.append('../p10_bot_flyme')


class TestLuis(aiounittest.AsyncTestCase):

    async def test_execute_luis_query(self):
        CONFIG = DefaultConfig()
        luis_recognizer = FlightBookingRecognizer(CONFIG)

        async def exec_text(turn_context: TurnContext):
            intent, result = await LuisHelper.execute_luis_query(
                luis_recognizer, turn_context
            )

            await turn_context.send_activity(
                json.dumps({"intent": intent,
                            "booking_details": result.__dict__})
            )

        adapter = TestAdapter(exec_text)

        await adapter.test(
            "I want to book a flight from Marseille to Paris",
            json.dumps({"intent": "book",
                        "booking_details": BookingDetails(
                            or_city="Marseille",
                            dst_city="Paris"
                        ).__dict__})
        )

        await adapter.test(
            "I want to travel from the 12 aug 2022 until 15 september 2022",
            json.dumps({"intent": "book",
                        "booking_details": BookingDetails(
                            str_date="2022-08-12",
                            end_date="2022-09-15"
                        ).__dict__})
        )

        await adapter.test(
            "I want to spend maximun $500",
            json.dumps({"intent": "book",
                        "booking_details": BookingDetails(
                            budget="$ 500",
                        ).__dict__})
        )

        await adapter.test(
            """I want to book a flight from Marseille to Paris
            I want to spend maximun $500
            I want to travel from the 12 aug 2022 until 15 september 2022""",
            json.dumps({"intent": "book",
                        "booking_details": BookingDetails(
                            or_city="Marseille",
                            dst_city="Paris",
                            str_date="2022-08-12",
                            end_date="2022-09-15",
                            budget="$ 500",
                        ).__dict__})
        )


class TestDialog(aiounittest.AsyncTestCase):

    async def test_booking_dialog(self):

        async def exec_test(turn_context: TurnContext):
            dialog_context = await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()
            if results.status == DialogTurnStatus.Empty:
                await main_dialog.intro_step(dialog_context)

            elif results.status == DialogTurnStatus.Complete:
                await main_dialog.act_step(dialog_context)

            await conv_state.save_changes(turn_context)

        

        conv_state = ConversationState(MemoryStorage())
        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet(dialogs_state)
        booking_dialog = BookingDialog()
        main_dialog = MainDialog(
            FlightBookingRecognizer(DefaultConfig()), booking_dialog
        )
        dialogs.add(booking_dialog)

        text_prompt = await main_dialog.find_dialog(TextPrompt.__name__)
        dialogs.add(text_prompt)

        wf_dialog = await main_dialog.find_dialog("WFDialog")
        dialogs.add(wf_dialog)


        adapter = TestAdapter(exec_test)

        await adapter.test('Hello', 'What can I help you with today?')

        await adapter.test('I want to book a fligth', 'From what city will you be travelling?')
        
        await adapter.test('Paris', 'To what city would you like to travel?')

        await adapter.test('Marseille', 'What is your budget for this trip?')

        await adapter.test('$500', 'What is the departure date?')

        await adapter.test('2022-10-10', 'What is the return date?')

        await adapter.test('2022-11-10', """Please confirm your travel details:\n
        - From: Paris\n
        - To: Marseille\n
        - Departure date: 2022-10-10\n
        - Return date: 2022-11-10\n
        - Price: $500
         (1) Yes or (2) No
        """)