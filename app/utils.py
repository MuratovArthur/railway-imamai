import importlib
import pkgutil
from datetime import datetime
from typing import Any, Callable, Optional, Tuple
from zoneinfo import ZoneInfo

import orjson
from bson.objectid import ObjectId
from pydantic import BaseModel, root_validator

import requests

# Constants (replace with actual IAM token and folder ID)
IAM_TOKEN = 't1.9euelZqVzc2QjZPOjMzJjMjNkovKzu3rnpWayJ2VjpbOnJSXjp3OncfKz53l9PcvfTZS-e9WYGL33fT3bys0UvnvVmBi983n9euelZrNjsiaic_JlJedmJ2djsuUxu_8xeuelZrNjsiaic_JlJedmJ2djsuUxg.mIAhSOI1QR-bCsX3DwcxaJ6a8q0aMbrLd7FwnvR-LMxrNQMsFDsRjQcRvYpDfyH5kFkjK7-3xCOKqOCZ7ZdZAg'
FOLDER_ID = 'b1gog32re13jie3oakvi'


def translate_text(text: str, target_language: str) -> Tuple[str, str]:
    """
    Translate the given text to the target language using Yandex Cloud Translation.

    :param text: Text to be translated.
    :param target_language: Language code to translate the text into.
    :return: A tuple containing the translated text and the detected source language.
    """
    body = {
        "targetLanguageCode": target_language,
        "texts": [text],
        "folderId": FOLDER_ID,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {IAM_TOKEN}"
    }

    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                             json=body, headers=headers)
    response.raise_for_status()
    response_data = response.json()

    translated_text = response_data['translations'][0]['text']
    detected_language = response_data['translations'][0]['detectedLanguageCode']

    return translated_text, detected_language


# Example of calling the function
try:
    translated, detected_lang = translate_text("Hello Arthur!", "ru")
    print(f"Translated Text: {translated}")
    print(f"Detected Language: {detected_lang}")
except requests.RequestException as e:
    print(f"An error occurred: {str(e)}")


def orjson_dumps(v: Any, *, default: Optional[Callable[[Any], Any]]) -> str:
    return orjson.dumps(v, default=default).decode()


def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class AppModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        json_encoders = {datetime: convert_datetime_to_gmt, ObjectId: str}
        allow_population_by_field_name = True

    @root_validator()
    def set_null_microseconds(cls, data: dict[str, Any]) -> dict[str, Any]:
        datetime_fields = {
            k: v.replace(microsecond=0)
            for k, v in data.items()
            if isinstance(k, datetime)
        }

        return {**data, **datetime_fields}


def import_routers(package_name):
    package = importlib.import_module(package_name)
    prefix = package.__name__ + "."

    for _, module_name, _ in pkgutil.iter_modules(package.__path__, prefix):
        if not module_name.startswith(prefix + "router_"):
            continue

        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"Failed to import {module_name}, error: {e}")
