from datetime import datetime
from typing import Optional

from bson.objectid import ObjectId
from pymongo.database import Database

from ..utils.security import hash_password


class AuthRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_user(self, user: dict):
        payload = {
            "email": user["email"],
            "password": hash_password(user["password"]),
            "created_at": datetime.utcnow(),
        }

        self.database["users"].insert_one(payload)

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        user = self.database["users"].find_one(
            {
                "_id": ObjectId(user_id),
            }
        )
        return user

    def get_user_by_email(self, email: str) -> Optional[dict]:
        user = self.database["users"].find_one(
            {
                "email": email,
            }
        )
        return user

    def update_user(self, user_id: str, new_data: dict):
        update_result = self.database["users"].update_one(
            filter={"_id": ObjectId(user_id)},
            update={
                "$set": {
                    "phone": new_data["phone"],
                    "name": new_data["name"],
                    "city": new_data["city"],
                }
            },
        )
        return update_result.modified_count

    def add_avatar(self, user_id, avatar_url):
        update_result = self.database["users"].update_one(
            filter={"_id": ObjectId(user_id)},
            update={
                "$set": {
                    "avatar_url": avatar_url,
                }
            },
        )
        return update_result.modified_count

    def delete_media(self, user_id):
        user = self.database["users"].find_one(
            {
                "_id": ObjectId(user_id),
            }
        )
        url_to_be_deleted = user["avatar_url"]

    def remove_avatar_url_user(self, user_id):
        return (
            self.database["users"].update_one(
                filter={"_id": ObjectId(user_id)},
                update={
                    "$set": {
                        "avatar_url": None,
                    }
                },
            )
        ).modified_count
