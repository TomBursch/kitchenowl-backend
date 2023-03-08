from __future__ import annotations
from typing import Self
from app import db
from app.helpers import DbModelMixin, TimestampMixin


class Planner(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'planner'

    recipe_id = db.Column(db.Integer, db.ForeignKey(
        'recipe.id'), primary_key=True)
    day = db.Column(db.Integer, primary_key=True)
    yields = db.Column(db.Integer)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)

    recipe = db.relationship("Recipe", back_populates="plans")

    def obj_to_full_dict(self) -> dict:
        res = self.obj_to_dict()
        res['recipe'] = self.recipe.obj_to_full_dict()
        return res

    @classmethod
    def find_by_day(cls, household_id:int, recipe_id: int, day: int) -> Self:
        return cls.query.filter(cls.household_id == household_id, cls.recipe_id == recipe_id, cls.day == day).first()
