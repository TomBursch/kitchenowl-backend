from typing import Self
from app import db
from app.helpers import DbModelMixin, TimestampMixin
from app.helpers.db_list_type import DbListType


class Household(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'household'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    photo = db.Column(db.String())
    language = db.Column(db.String())
    planner_feature = db.Column(db.Boolean(), default=True)
    expenses_feature = db.Column(db.Boolean(), default=True)

    view_ordering = db.Column(DbListType(), default=list())

    shoppinglists = db.relationship(
        'Shoppinglist', back_populates='household', cascade="all, delete-orphan")
    member = db.relationship(
        'HouseholdMember', back_populates='household', cascade="all, delete-orphan")

    def obj_to_dict(self) -> dict:
        res = super().obj_to_dict()
        res['member'] = [m.obj_to_user_dict() for m in getattr(self, 'member')]
        return res


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

    def obj_to_user_dict(self) -> dict:
        res = self.user.obj_to_dict()
        res['owner'] = getattr(self, 'owner')
        res['admin'] = getattr(self, 'admin')
        res['expense_balance'] = getattr(self, 'expense_balance')
        return res

    @classmethod
    def find_by_ids(cls, household_id: int, user_id: int) -> Self:
        return cls.query.filter(cls.household_id == household_id, cls.user_id == user_id).first()

    @classmethod
    def find_by_household(cls, household_id: int) -> list[Self]:
        return cls.query.filter(cls.household_id == household_id).all()

    @classmethod
    def find_by_user(cls, user_id: int) -> list[Self]:
        return cls.query.filter(cls.user_id == user_id).all()
