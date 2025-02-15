import requests
import uuid

from soupbot_util.constants import AZURE_TRANSLATOR_SECRET_KEY, AZURE_TRANSLATOR_REGION, AZURE_TRANSLATION_KEY


key = AZURE_TRANSLATOR_SECRET_KEY
region = AZURE_TRANSLATOR_REGION

url = "https://api.cognitive.microsofttranslator.com/"

headers = {
    "Ocp-Apim-Subscription-Key": key,
    "Ocp-Apim-Subscription-Region": region,
    "Content-type": "application/json",
    "X-ClientTraceId": str(uuid.uuid4())
}


def azure_translate(text:str, from_lang:str, to_lang:str) -> str:
    params = {"api-version": "3.0", "to": []}
    body = [{"text": text}]

    if from_lang.lower() in AZURE_TRANSLATION_KEY.keys():
        params["from"] = AZURE_TRANSLATION_KEY[from_lang.lower()]
    elif from_lang != "auto":
        return f"source language {from_lang} not a valid language"

    if to_lang.lower() in AZURE_TRANSLATION_KEY.keys():
        params["to"].append(AZURE_TRANSLATION_KEY[to_lang.lower()])
    else:
        return f"target language {to_lang} not a valid language"

    request = requests.post(url + "translate", params=params, headers=headers, json=body)
    response = request.json()

    if len(response) > 0:
        return response[0]["translations"][0]["text"]
    else:
        return "not able to generate a translation"

def azure_detect(text:str):
    params = {"api-version": "3.0"}
    body = [{"text": text}]
    request = requests.post(url + "detect", params=params, headers=headers, json=body)
    response = request.json()

    if len(response) > 0:
        return response[0]["language"].upper()

    return None
