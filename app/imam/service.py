from app.config import database
from pydantic import BaseSettings
from .repository.repository import ImamRepository


class Service:
    def __init__(
        self,
        repository: ImamRepository,
    ):
        self.repository = repository


def get_service():
    repository = ImamRepository(database)
    svc = Service(repository)
    return svc
