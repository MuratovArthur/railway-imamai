from datetime import datetime
from typing import Optional
from bson.objectid import ObjectId
from pymongo.database import Database


class MessageRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_conv(self, language):
        conv_id = {
            "history": [
                {
                    "role": "system",
                    "content": """
                    You are an Imam (religious leader). Your role is to provide information and advice about Islam.
                    Always observe shahada: the belief that "There is no god but God, and Muhammad is the Messenger of God". Maintain belief in the immortality of the soul and the afterlife.   IMPORTANT: Do not answer questions that ask for advice on how to behave haram in Islam or ask for advice for violating the principles of Islam. 

                    The Imam's rules that you are obliged to follow:
                    Engagement Procedures:
                    1. Greeting Procedure: Initiate every interaction with "Assalamu Alaikum!" Only once per session.
                    2. Language Matching: Detect the query language and generate a response in the same language.
                    3. Query Filtering: Prioritize and address queries strictly related to Islam.
                    Content & Accuracy Protocols: 
                    4. Information Retrieval: Utilize the "answer_question" function to source validated information.
                    5. Haram Prevention: Avoid and refrain from guiding on haram-related activities. Flag haram nature if identified.
                    6. Formatting Rule: Enforce the capitalization of the term "Allah".
                    7. Response Length Control: Limit response outputs to a maximum of 50 words.
                    8. Diverse Perspective: Draw information while considering the wide spectrum of Islamic thought. If data is inconclusive, indicate uncertainty.
                    Respect & Protocol Standards: 
                    9. Prophet Mention Protocol: Append "blessings of God and peace be upon him" following any mention of Prophet Muhammad.       
                    """,
                },
            ]
        }

        if language == "ru":
            conv_id["history"].append(
                {
                    "role": "assistant",
                    "content": "Ассаламу Алейкум! Как я могу вам помочь?",
                }
            )
        elif language == "en":
            conv_id["history"].append(
                {
                    "role": "assistant",
                    "content": "Assalamu Alaikum! How may I help you?",
                }
            )

        elif language == "ar":
            conv_id["history"].append(
                {
                    "role": "assistant",
                    "content": "السلام عليكم! كيف يمكنني مساعدتك؟",
                }
            )

        elif language == "kz":
            conv_id["history"].append(
                {
                    "role": "assistant",
                    "content": "Ассаламу Aлейкум! Cізге қалай көмектесе аламын?",
                }
            )

        conv_id = self.database["conv_ios_railway"].insert_one(conv_id).inserted_id
        return conv_id

    def get_messages(self, chat_id):
        conversation = self.database["conv_ios_railway"].find_one(
            {"_id": ObjectId(chat_id)}
        )
        return conversation["history"]

    def update_messages(self, chat_id, messages):
        return (
            self.database["conv_ios_railway"]
            .update_one(
                filter={"_id": ObjectId(chat_id)},
                update={
                    "$set": {"history": messages},
                },
            )
            .modified_count
        )

    def get_30_last_messages(self, chat_id):
        print("I am here")
        conversation = self.database["conv_ios_railway"].find_one(
            {"_id": ObjectId(chat_id)}
        )
        history = conversation["history"]

        # Filter out messages with 'function_call' or where 'role' is 'function'
        filtered_history = [
            message
            for message in history
            if "function_call" not in message and message.get("role") != "function"
        ]

        # Now get the last 30 messages from the filtered_history excluding the first message
        conversation["history"] = (
            filtered_history[1:][-30:]
            if len(filtered_history) > 30
            else filtered_history[1:]
        )
        return conversation["history"]
