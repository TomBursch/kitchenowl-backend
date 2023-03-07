from typing import Self
from app import db
from app.helpers import DbModelMixin, TimestampMixin
from app.helpers.db_list_type import DbListType


class Settings(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get(cls) -> Self:
        settings = cls.query.first()
        if not settings:
            settings = cls()
            settings.save()
        return settings
