#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 3978#8000
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    LUIS_APP_ID = os.environ.get("LuisAppId", "3a14ce88-d39b-47c2-9661-12d37ec4d9e3")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "af8aaf3777144547ae8083d82f1cfd58")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "p10-luis-mazym.cognitiveservices.azure.com/")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "fa7baad5-5706-4dd5-bb13-252d8f8cceb9" #"c42ea6c6-8853-4278-b62b-d6a417481fd5"
    )
