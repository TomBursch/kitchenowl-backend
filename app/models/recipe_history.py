from __future__ import annotations
from app import db
from app.helpers import DbModelMixin, TimestampMixin
from .recipe import Recipe
from sqlalchemy import func

import enum


class Status(enum.Enum):
    ADDED = 1
    DROPPED = -1


class RecipeHistory(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'recipe_history'

    id = db.Column(db.Integer, primary_key=True)

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))

    recipe = db.relationship("Recipe", uselist=False,
                             back_populates="recipe_history")

    status = db.Column(db.Enum(Status))

    @classmethod
    def create_added(cls, recipe: Recipe) -> RecipeHistory:
        return cls(
            recipe_id=recipe.id,
            status=Status.ADDED
        ).save()

    @classmethod
    def create_dropped(cls, recipe: Recipe) -> RecipeHistory:
        return cls(
            recipe_id=recipe.id,
            status=Status.DROPPED
        ).save()

    def obj_to_item_dict(self) -> dict:
        res = self.item.obj_to_dict()
        res['timestamp'] = getattr(self, 'created_at')
        return res

    @classmethod
    def find_added(cls) -> list[RecipeHistory]:
        return cls.query.filter(cls.status == Status.ADDED).all()

    @classmethod
    def find_dropped(cls) -> list[RecipeHistory]:
        return cls.query.filter(cls.status == Status.DROPPED).all()

    @classmethod
    def find_all(cls) -> list[RecipeHistory]:
        return cls.query.all()

    @classmethod
    def get_recent(cls) -> list[RecipeHistory]:
        sq = db.session.query(Recipe.id).filter(
            Recipe.planned).subquery().select(Recipe.id)
        sq2 = db.session.query(func.max(cls.id)).filter(cls.status == Status.DROPPED).filter(
            cls.recipe_id.notin_(sq)).group_by(cls.recipe_id).join(cls.recipe).subquery().select(cls.id)
        return cls.query.filter(cls.id.in_(sq2)).order_by(cls.id.desc()).limit(9)
