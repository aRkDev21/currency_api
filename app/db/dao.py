import json
from typing import Optional

from app.api.schemas.user import User

class DAO:
    def __init__(self):
        with open("db.json") as f:
            raw = json.load(f)
            self._db = {
                k: User(**v) for k, v in raw.items()
            }

    def add_user(self, user: User) -> bool:
        if user.username in self._db:
            return False
        self._db[user.username] = user
        self.save()
        return True

    def get_user(self, username: str) -> Optional[User]:
        return self._db.get(username)

    def save(self):
        with open("db.json", "w") as f:
            json.dump(
                {k: v.model_dump() for k, v in self._db.items()},
                f,
                indent=2
            )

dao = DAO()