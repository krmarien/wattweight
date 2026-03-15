from sqlmodel import Session

from wattweight.database import Database


class Core:
    _db: Session | None = None

    @property
    def db(self) -> Session:
        if Core._db is None:
            Core._db = Database.get_instance().get_session()
        return Core._db
