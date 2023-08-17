# from datetime import datetime
# from typing import Optional

from bson.objectid import ObjectId
from pymongo.database import Database


class PostRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_post(self, input: dict, language):
        payload = {
            "imageURL": input["imageURL"],
            "title": input["title"],
            "description": input["description"],
        }

        collection_name = "posts_{}".format(language)
        return self.database[collection_name].insert_one(payload).inserted_id

    def get_posts_from_db(self, limit: int, offset: int, language) -> dict:
        if language == "ru" or language == "kk":
            collection_name = "posts"
        else:
            collection_name = "posts_en"

        # Get a cursor pointing to your documents
        cursor = (
            self.database[collection_name]
            .find()
            .sort("_id", -1)
            .skip(offset)
            .limit(limit)
        )

        # Turn the cursor into a list
        posts = list(cursor)

        # Getting the total number of matched documents without applying limit and offset
        total = self.database[collection_name].count_documents({})

        return {"total": total, "objects": posts}
