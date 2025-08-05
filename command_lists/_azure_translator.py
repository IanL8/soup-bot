import requests as _requests
from uuid import uuid4 as _uuid4

import soup_util.constants as _constants


_HEADERS = {
    "Ocp-Apim-Subscription-Key": _constants.AZURE_TRANSLATOR_SECRET_KEY,
    "Ocp-Apim-Subscription-Region": _constants.AZURE_TRANSLATOR_REGION,
    "Content-type": "application/json",
    "X-ClientTraceId": str(_uuid4())
}


def translate(text: str, from_lang: str, to_lang: str) -> str:
    params = {"api-version": "3.0", "to": []}
    body = [{"text": text}]

    if from_lang.lower() in _constants.AZURE_TRANSLATION_KEY.keys():
        params["from"] = _constants.AZURE_TRANSLATION_KEY[from_lang.lower()]
    elif from_lang != "auto":
        return f"Source language {from_lang} is unsupported"

    if to_lang.lower() in _constants.AZURE_TRANSLATION_KEY.keys():
        params["to"].append(_constants.AZURE_TRANSLATION_KEY[to_lang.lower()])
    else:
        return f"Target language {to_lang} is unsupported"

    request = _requests.post("https://api.cognitive.microsofttranslator.com/translate", params=params, headers=_HEADERS, json=body)
    response = request.json()

    if len(response) > 0:
        return response[0]["translations"][0]["text"]
    else:
        return "Not able to generate a translation at this time"

def detect(text: str):
    params = {"api-version": "3.0"}
    body = [{"text": text}]
    request = _requests.post("https://api.cognitive.microsofttranslator.com/detect", params=params, headers=_HEADERS, json=body)
    response = request.json()

    if len(response) > 0:
        return response[0]["language"].upper()

    return None
