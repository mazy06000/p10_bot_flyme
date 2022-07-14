#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os
# from dotenv import load_dotenv
# load_dotenv()

# LUIS_ID  = os.getenv("LUIS_ID")
# LUIS_KEY  = os.getenv("LUIS_KEY")
# LUIS_HOST  = os.getenv("LUIS_HOST")
# INSIGHTS_KEY  = os.getenv("INSIGHTS_KEY")


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 8000 #3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    LUIS_APP_ID = os.environ.get("LuisAppId", os.environ["LUIS_ID"])
    LUIS_API_KEY = os.environ.get("LuisAPIKey", os.environ["LUIS_KEY"])
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", os.environ["LUIS_HOST"])
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", os.environ["INSIGHTS_KEY"]
    )
