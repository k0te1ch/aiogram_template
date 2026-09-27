from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from config import DATABASE_URL


class _Database:
    """Lightweight SQLAlchemy wrapper.

    ``Model`` (declarative base) is always available so models import even
    without a configured database. ``engine``/``session`` are only created
    when ``DATABASE_URL`` is set — check ``db.enabled`` before querying.
    """

    def __init__(self, db_url: str | None) -> None:
        self.Model = declarative_base()
        self.enabled = bool(db_url)

        if db_url:
            self.engine = create_engine(db_url)
            self.sessionmaker = sessionmaker(bind=self.engine)
            self.session = scoped_session(self.sessionmaker)
            self.Model.query = self.session.query_property()
            logger.debug("Database is configured")
        else:
            self.engine = None
            self.sessionmaker = None
            self.session = None
            logger.debug("Database isn't configured")

    @property
    def metadata(self):
        return self.Model.metadata


db = _Database(DATABASE_URL)
