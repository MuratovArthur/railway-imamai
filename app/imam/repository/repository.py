from datetime import datetime
from typing import Optional
from bson.objectid import ObjectId
from pymongo.database import Database


class ImamRepository:
    def __init__(self, database: Database):
        self.database = database
