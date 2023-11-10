from typing import Self

from app import db
from app.helpers import DbModelMixin, TimestampMixin


class OIDCLink(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = "oidc_link"

    sub = db.Column(db.String(256), primary_key=True)
    provider = db.Column(db.String(24), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", back_populates="oidc_links")

    @classmethod
    def find_by_ids(cls, sub: str, provider: str) -> Self:
        return cls.query.filter(cls.sub == sub, cls.provider == provider).first()


class OIDCRequest(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = "oidc_request"

    state = db.Column(db.String(256), primary_key=True)
    provider = db.Column(db.String(24), primary_key=True)
    nonce = db.Column(db.String(256), nullable=False)

    @classmethod
    def find_by_state(cls, state: str) -> Self:
        return cls.query.filter(cls.state == state).first()
