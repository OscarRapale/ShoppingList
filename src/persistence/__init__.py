""" This module is responsible for selecting the repository
to be used based on the environment variable REPOSITORY_ENV_VAR."""

import os

from src.persistence.repository import Repository
from utils.constants import REPOSITORY_ENV_VAR

repo: Repository

if os.getenv(key=REPOSITORY_ENV_VAR) == "db":
    from src.persistence.db import DBRepository

    repo = DBRepository()

elif os.getenv(REPOSITORY_ENV_VAR) == "file":
    from src.persistence.file import FileRepository

    repo = FileRepository()

else:
    from src.persistence.memory import MemoryRepository

    repo = MemoryRepository()

print(f"Using {repo.__class__.__name__} as repository")