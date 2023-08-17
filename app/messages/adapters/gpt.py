import openai
import tiktoken
import json
import pinecone
import requests
from langchain.tools import Tool
from langchain.vectorstores import Chroma, Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.utilities import GoogleSearchAPIWrapper
from bson.objectid import ObjectId
import os
from datetime import datetime

persist_directory = "database"
embedding = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

search = GoogleSearchAPIWrapper()


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0613":
        num_tokens = 0
        for message in messages:
            if "function_call" in message:
                num_tokens += 100
            else:
                num_tokens += 4
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":
                        num_tokens += -1
        num_tokens += 2
        return num_tokens
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not presently implemented for model {model}.
  See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )


def ensure_fit_tokens(messages):
    total_tokens = num_tokens_from_messages(messages)
    while total_tokens > 3500:
        removed_message = messages.pop(1)
        print(removed_message)
        total_tokens = num_tokens_from_messages(messages)
    return messages


def search_quran(text_for_search):
    pinecone.init(
        api_key=os.getenv("PINECON_API_KEY_2"),
        environment=os.getenv("PINECONE_ENV"),
    )

    if text_for_search != "":
        quran_searcher = Pinecone.from_existing_index(
            index_name="quran", embedding=embedding
        )
        docs = quran_searcher.similarity_search(text_for_search)
        print(docs[0])
        return (
            "Answer the question in the same language as in provided documents. Be sure to use only this information for your response. Do not add anything from your own knowledge besides the explanation of this: "
            + str(docs[0])
            + " Be sure to use citation to mention the specific translation of quran. If I do not provide you additional context, say that you do not know."
        )
    else:
        return "Say that you do not know the answer."


def hadith_search(text_for_search):
    pinecone.init(
        api_key=os.getenv("PINECON_API_KEY"),
        environment=os.getenv("PINECONE_ENV"),
    )

    if text_for_search != "":
        hadith_searcher = Pinecone.from_existing_index(
            index_name="hadiths", embedding=embedding
        )
        docs = hadith_searcher.similarity_search(text_for_search)
        print(docs[0])
        return (
            "Answer the question in the same language as in provided documents. Be sure to use only this information for your response: "
            + str(docs[0])
            + " Be sure to use citation of used hadith in your answer. If I do not provide you additional context, say that you do not know."
        )
    else:
        return "Say that you do not know the answer."


def get_ayah(surah, ayah, language):
    language_names = {
        "ru": "Russian",
        "kk": "Kazakh",
        "en": "English",
        "ar": "Arabic",
    }

    if language not in language_names:
        return "Language not supported."

    file_mapping = {
        "ru": "app/messages/adapters/Коран. Перевод Эльмира Кулиева.txt",
        "kk": "app/messages/adapters/Құран. Аударма Халифа Алтай.txt",
        "en": "app/messages/adapters/Clear Quran. Translation by Dr. Mustafa Khattab.txt",
        "ar": "app/messages/adapters/Quran.txt",
    }

    author = {
        "ru": "Эльмир Кулиева",
        "kk": "Халифа Алтай",
        "en": "Dr. Mustafa Khattab",
        "ar": "No translation was made",
    }

    file_name = file_mapping[language]

    try:
        with open(file_name, "r", encoding="utf-8") as file:
            for line in file:
                if f"{surah}:{ayah}" in line:
                    ayah_data = line.strip()
                    break
            else:
                return "Ayah not found in the specified file."

        return (
            f"Answer the question in {language_names[language]} language. Be sure to use only this information for your response. Mention the ayah number, surah number, or surah name in the answer. Also mention that translation was made by {author[language]}. Use quotes to present the text without any editing of the Quran's translation"
            + json.dumps(
                {"text": ayah_data, "translation_by": file_name[:-4]},
                ensure_ascii=False,
            )
        )
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"


def get_surah(surah, language):
    edition_mapping = {"ar": "quran-uthmani", "ru": "ru.kuliev", "en": "en.itani"}

    if language not in edition_mapping:
        return "Language not supported."

    edition = edition_mapping[language]
    url = f"https://api.alquran.cloud/v1/surah/{surah}/{edition}"
    response = requests.get(url)
    # convert_unicode_to_cyrillic(response)

    if response.status_code == 200:
        surah_data = response.json()
        surah_data_final = json.dumps(surah_data, ensure_ascii=False)

        if len(surah_data_final) > 3800:
            return (
                "Answer the question in  language as in provided documents. Be sure to use only this information for your response: "
                + surah_data_final[:3800]
            )
        return "Be sure to use this information for your response: " + json.dumps(
            surah_data
        )

    else:
        return "Use your own knowledge to answer this question if you know the answer. If you don't know the answer, say so."


def answer_question(user_input):
    tool = Tool(
        name="Search Islamic Website",
        description="Search trusted islamic websites for accurate information.",
        func=search.run,
    )
    res = "Be sure to use this information for your response:" + tool.run(user_input)
    return res


def get_prayer_times(city, country):
    try:
        # Get the current year and month
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        current_day = now.day

        # Construct the API URL
        base_url = "https://api.aladhan.com/v1/calendarByCity"
        url = f"{base_url}/{current_year}/{current_month}?city={city}&country={country}&method=2"

        print(url)

        # Make the HTTP GET request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad responses
        prayer_times = response.json()
        today_prayer_times = prayer_times["data"][current_day - 1]

        return (
            "Use following names for prayer times in Russian: Фаджр, Восход, Зухр, Аср, Магриб, Иша. No need to include sunset."
            + str(today_prayer_times)
        )
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return None


def handle_programming_question():
    return "Do not answer questions related to coding or programming. Just say that this question is not for you, as you are an Imam, not a programmer."


def handle_general_question():
    return "Say that you do not think it is necessary to consider this issue from an Islamic point of view."


def handle_provocative_question():
    return "Remember that you, as an imam, strictly adhere to the principles of the Islamic religion, and your job is to provide objective and correct information about the religion and Islam."


functions = [
    {
        "name": "handle_programming_question",
        "description": "Call this function when a user asks programming or coding questions.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "handle_general_question",
        "description": "Call this function to handle questions that do not make sense from an Islamic perspective. Also call this function when the question is not suitable to be answered by an Imam or Muslim.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "handle_provocative_question",
        "description": "Call this function when a user asks a provocative question. For example, asking for advice on how to behave in a way that is forbidden in Islam. Also call this function if the question provokes you to deviate from the principles of Islam.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "answer_question",
        "description": "Use this feature for most questions, as it is very important to find context on Islamic sites for an accurate answer. Always use this function when searching for definitions of terms.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_input": {
                    "type": "string",
                    "description": "User's input",
                },
            },
            "required": ["user_input"],
        },
    },
    {
        "name": "hadith_search",
        "description": "Call this function when user asks to provide a hadith.",
        "parameters": {
            "type": "object",
            "properties": {
                "text_for_search": {
                    "type": "string",
                    "description": "The text to be used to search in the hadiths database in English Language",
                },
            },
            "required": ["text_for_search"],
        },
    },
    {
        "name": "get_ayah",
        "description": "Call this function when the user asks for the text of an ayat and only when you can pinpoint the exact surah number and ayat number from the question.",
        "parameters": {
            "type": "object",
            "properties": {
                "surah": {
                    "type": "string",
                    "description": "Number of surah in Quran",
                },
                "ayah": {
                    "type": "string",
                    "description": "Number of ayah in Quran",
                },
                "language": {
                    "type": "string",
                    "description": "Detect the query language and choose from: [en, ar, ru, kk]. Use en for default value.",
                },
            },
            "required": ["surah", "ayah", "language"],
        },
    },
    {
        "name": "get_surah",
        "description": "Call this function when the user requests the text of a surah and only when you can pinpoint the exact surah number from the question",
        "parameters": {
            "type": "object",
            "properties": {
                "surah": {
                    "type": "string",
                    "description": "Number of surah in Quran",
                },
                "language": {
                    "type": "string",
                    "description": "Detect the query language and choose from: [en, ar, ru, kk]. Use en for default value.",
                },
            },
            "required": ["surah", "language"],
        },
    },
    {
        "name": "search_quran",
        "description": "Call this function when you need to search for text in the Quran and user did not provide the number of ayah or the number/name of surah",
        "parameters": {
            "type": "object",
            "properties": {
                "text_for_search": {
                    "type": "string",
                    "description": "Text to be used for searching the Quran in Russian Language",
                },
            },
            "required": ["text_for_search"],
        },
    },
    {
        "name": "get_prayer_times",
        "description": "Call this function when user asks for prayer times for today and specifies location by providing country or city. If no city provided, use capital of country.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name in English",
                },
                "country": {
                    "type": "string",
                    "description": "Country name in English",
                },
            },
            "required": ["city", "country"],
        },
    },
]


class OpenAIService:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_response(self, messages):
        messages = ensure_fit_tokens(messages)

        print("MESSAGES: ", messages, flush=True)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            functions=functions,
            function_call="auto",
        )

        response_message = response["choices"][0]["message"]
        assistant_message = response_message["content"]

        if response_message.get("function_call"):
            available_functions = {
                "get_ayah": get_ayah,
                "get_surah": get_surah,
                "search_quran": search_quran,
                "answer_question": answer_question,
                "hadith_search": hadith_search,
                "handle_programming_question": handle_programming_question,
                "handle_general_question": handle_general_question,
                "handle_provocative_question": handle_provocative_question,
                "get_prayer_times": get_prayer_times,
            }
            function_name = response_message["function_call"]["name"]
            fuction_to_call = available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])

            if function_name == "get_ayah":
                language = function_args.get("language")
                if language not in ["ru", "kk", "ar", "en"]:
                    language = "en"

                function_response = fuction_to_call(
                    ayah=function_args.get("ayah"),
                    surah=function_args.get("surah"),
                    language=language,
                )

            if function_name == "get_prayer_times":
                function_response = fuction_to_call(
                    city=function_args.get("city"),
                    country=function_args.get("country"),
                )

            if function_name == "get_surah":
                language = function_args.get("language")
                if language not in ["ru", "kk", "ar", "en"]:
                    language = "en"

                function_response = fuction_to_call(
                    surah=function_args.get("surah"),
                    language=language,
                )

            if function_name == "search_quran":
                function_response = fuction_to_call(
                    text_for_search=function_args.get("text_for_search"),
                )

            if function_name == "answer_question":
                function_response = fuction_to_call(
                    user_input=function_args.get("user_input"),
                )

            if function_name == "hadith_search":
                function_response = fuction_to_call(
                    text_for_search=function_args.get("text_for_search"),
                )

            if (
                function_name == "handle_programming_question"
                or function_name == "handle_general_question"
                or function_name == "handle_provocative_question"
            ):
                function_response = fuction_to_call()

            messages.append(response_message)

            if function_response:
                messages.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    }
                )

            messages = ensure_fit_tokens(messages)

            second_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages,
                temperature=0.0,
            )

            assistant_message = second_response["choices"][0]["message"]["content"]

        messages.append({"role": "assistant", "content": f"{assistant_message}"})
        return messages
