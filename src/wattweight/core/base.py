from sqlmodel import Session

from wattweight.database import Database


class Core:
    @property
    def db(self) -> Session:
        return Database().get_session()
