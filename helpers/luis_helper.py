# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext
from dateutil import parser
from booking_details import BookingDetails


class Intent(Enum):
    BOOK_FLIGHT = "book"
    NONE_INTENT = "NoneIntent"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent == Intent.BOOK_FLIGHT.value:
                result = BookingDetails()

                # We need to get the result from the LUIS JSON which at every level returns an array.
                to_entities = recognizer_result.entities.get(
                    "dst_city", []
                )
                if len(to_entities) > 0:
                    if recognizer_result.entities.get("dst_city")[0]:
                        result.dst_city = to_entities[0].capitalize()

                from_entities = recognizer_result.entities.get(
                    "or_city", []
                )
                if len(from_entities) > 0:
                    if recognizer_result.entities.get("or_city")[0]:
                        result.or_city = from_entities[0].capitalize()


                budget_entities = recognizer_result.entities.get(
                    "budget", []
                )
                if len(budget_entities) > 0:
                    if recognizer_result.entities.get("budget")[0]:
                        result.budget = budget_entities[0]     

                start_date_entities = recognizer_result.entities.get(
                    "str_date", []
                )
                if len(start_date_entities) > 0:
                    if recognizer_result.entities.get("str_date")[0]:
                        result.str_date = parser.parse(start_date_entities[0]).strftime("%Y-%m-%d")
                
                end_date_entities = recognizer_result.entities.get(
                    "end_date", []
                )
                if len(end_date_entities) > 0:
                    if recognizer_result.entities.get("end_date")[0]:
                        result.end_date = parser.parse(end_date_entities[0]).strftime("%Y-%m-%d")

                # This value will be a TIMEX. And we are only interested in a Date so grab the first result and drop
                # the Time part. TIMEX is a format that represents DateTime expressions that include some ambiguity.
                # e.g. missing a Year.
                # date_entities = recognizer_result.entities.get("datetime", [])
                # if date_entities:
                #     timex = date_entities[0]["timex"]

                #     if timex:
                #         datetime = timex[0].split("T")[0]

                #         result.travel_date = datetime

                # else:
                #     result.travel_date = None

        except Exception as exception:
            print(exception)

        return intent, result
