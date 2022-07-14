# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

import json
from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from botbuilder.core.bot_telemetry_client import Severity
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog


class BookingDialog(CancelAndHelpDialog):
    """Flight booking implementation."""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client
        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.or_city_step,
                self.dst_city_step,
                self.budget_step,
                self.str_date_step,
                self.end_date_step,
                self.confirm_step,
                self.final_step,
            ],
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(text_prompt)
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            DateResolverDialog("StartDate", self.telemetry_client)
        )
        self.add_dialog(
            DateResolverDialog("EndDate", self.telemetry_client)
        )
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__


    async def or_city_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        booking_details = step_context.options

        if booking_details.or_city is None:
            booking_details.turns.append("From what city will you be travelling?")
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("From what city will you be travelling?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.or_city)

    async def dst_city_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for destination."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.or_city = step_context.result
        booking_details.turns.append(step_context.result)

        if booking_details.dst_city is None:
            booking_details.turns.append("To what city would you like to travel?")
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("To what city would you like to travel?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.dst_city)

    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for travel budget."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.dst_city = step_context.result
        booking_details.turns.append(step_context.result)

        if booking_details.budget is None:
            booking_details.turns.append("What is your budget for this trip?")
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(f"What is your budget for this trip?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.budget)

    async def str_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for travel date.
        This will use the DATE_RESOLVER_DIALOG."""

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.budget = step_context.result
        booking_details.turns.append(step_context.result)

        if not booking_details.str_date or self.is_ambiguous(
            booking_details.str_date
        ):
            booking_details.turns.append("What is the departure date?")
            return await step_context.begin_dialog(
                "StartDate", booking_details.str_date
            )  # pylint: disable=line-too-long

        return await step_context.next(booking_details.str_date)

    async def end_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for travel date.
        This will use the DATE_RESOLVER_DIALOG."""

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.str_date = step_context.result
        booking_details.turns.append(step_context.result)

        if not booking_details.end_date or self.is_ambiguous(
            booking_details.end_date
        ):
            booking_details.turns.append("What is the departure date?")
            return await step_context.begin_dialog(
                "EndDate", booking_details.end_date
            )  # pylint: disable=line-too-long

        return await step_context.next(booking_details.end_date)


    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.end_date = step_context.result
        booking_details.turns.append(step_context.result)

        msg = f"""Please confirm your travel details:\n
        - From: {booking_details.or_city}\n
        - To: {booking_details.dst_city}\n
        - Departure date: {booking_details.str_date}\n
        - Return date: {booking_details.end_date}\n
        - Price: {booking_details.budget}
        """

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction and end the dialog."""

        booking_details = step_context.options

        if step_context.result:
            
            # self.telemetry_client.track_metric(
            #     "booking_accepted",
            #     0,0
            # )

            self.telemetry_client.track_trace(
                "booking_refused",
                properties=booking_details.__dict__,
            )

            with open('performances.json') as json_file:
                performances = json.load(json_file)
     
            performances["successfull"].append(booking_details.__dict__)

            json_string = json.dumps(performances)
            with open("performances.json", "w") as outfile:
                outfile.write(json_string)


            return await step_context.end_dialog(booking_details)
        
        self.telemetry_client.track_trace(
                "booking_refused",
                severity=Severity.warning,
                properties=booking_details.__dict__,
            )


        with open('performances.json') as json_file:
                performances = json.load(json_file)
     
        performances["unsuccessfull"].append(booking_details.__dict__)

        json_string = json.dumps(performances)
        with open("performances.json", "w") as outfile:
            outfile.write(json_string)

        # self.telemetry_client.track_metric(
        #         "booking_refused",
        #         0,0
        #     )

        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
