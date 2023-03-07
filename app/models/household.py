from typing import Self
from app import db
from app.helpers import DbModelMixin, TimestampMixin
from app.helpers.db_list_type import DbListType


class Household(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'household'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    planner_feature = db.Column(db.Boolean(), primary_key=True, default=True)
    expenses_feature = db.Column(db.Boolean(), primary_key=True, default=True)

    view_ordering = db.Column(DbListType(), default=list())

    shoppinglists = db.relationship(
        'Shoppinglist', back_populates='household', cascade="all, delete-orphan")
    member = db.relationship('HouseholdMember', back_populates='household', cascade="all, delete-orphan")


class HouseholdMember(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'household_member'

    household_id = db.Column(db.Integer, db.ForeignKey(
        'household.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    owner = db.Column(db.Boolean(), default=False, nullable=False)
    admin = db.Column(db.Boolean(), default=False, nullable=False)

    expense_balance = db.Column(db.Float(), default=0, nullable=False)

    household = db.relationship("Household", back_populates='member')
    user = db.relationship("User", back_populates='households')

    @classmethod
    def find_by_ids(cls, household_id: int, user_id: int) -> Self:
        return cls.query.filter(cls.household_id == household_id, cls.user_id == user_id).first()
