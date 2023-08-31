from __future__ import annotations
from typing import Self
from app import db
from app.helpers import DbModelMixin, TimestampMixin, DbModelAuthorizeMixin
from .item import Item
from .tag import Tag
from .planner import Planner
from random import randint


class Recipe(db.Model, DbModelMixin, TimestampMixin, DbModelAuthorizeMixin):
    __tablename__ = 'recipe'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.String())
    photo = db.Column(db.String(), db.ForeignKey('file.filename'))
    time = db.Column(db.Integer)
    cook_time = db.Column(db.Integer)
    prep_time = db.Column(db.Integer)
    yields = db.Column(db.Integer)
    source = db.Column(db.String())
    suggestion_score = db.Column(db.Integer, server_default='0')
    suggestion_rank = db.Column(db.Integer, server_default='0')
    household_id = db.Column(db.Integer, db.ForeignKey(
        'household.id'), nullable=False)

    household = db.relationship("Household", uselist=False)
    recipe_history = db.relationship(
        "RecipeHistory", back_populates="recipe", cascade="all, delete-orphan")
    items = db.relationship(
        'RecipeItems', back_populates='recipe', cascade="all, delete-orphan")
    tags = db.relationship(
        'RecipeTags', back_populates='recipe', cascade="all, delete-orphan")
    plans = db.relationship(
        'Planner', back_populates='recipe', cascade="all, delete-orphan")
    photo_file = db.relationship(
        "File", back_populates='recipe', uselist=False)

    def obj_to_dict(self) -> dict:
        res = super().obj_to_dict()
        res['planned'] = len(self.plans) > 0
        res['planned_days'] = [plan.day for plan in self.plans if plan.day >= 0]
        if self.photo_file:
            res['photo_hash'] = self.photo_file.blur_hash
        return res

    def obj_to_full_dict(self) -> dict:
        res = self.obj_to_dict()
        items = RecipeItems.query.filter(RecipeItems.recipe_id == self.id).join(
            RecipeItems.item).order_by(
            Item.name).all()
        res['items'] = [e.obj_to_item_dict() for e in items]
        tags = RecipeTags.query.filter(RecipeTags.recipe_id == self.id).join(
            RecipeTags.tag).order_by(
            Tag.name).all()
        res['tags'] = [e.obj_to_item_dict() for e in tags]
        return res

    def obj_to_export_dict(self) -> dict:
        items = RecipeItems.query.filter(RecipeItems.recipe_id == self.id).join(
            RecipeItems.item).order_by(
            Item.name).all()
        tags = RecipeTags.query.filter(RecipeTags.recipe_id == self.id).join(
            RecipeTags.tag).order_by(
            Tag.name).all()
        res = {
            "name": self.name,
            "description": self.description,
            "time": self.time,
            "photo": self.photo,
            "cook_time": self.cook_time,
            "prep_time": self.prep_time,
            "yields": self.yields,
            "source": self.source,
            "items": [{"name": e.item.name, "description": e.description, "optional": e.optional} for e in items],
            "tags": [e.tag.name for e in tags],
        }
        return res

    @classmethod
    def compute_suggestion_ranking(cls, household_id: int):
        # reset all suggestion ranks
        for r in cls.query.filter(cls.household_id == household_id).all():
            r.suggestion_rank = 0
            db.session.add(r)
        # get all recipes with positive suggestion_score
        recipes = cls.query.filter(
            cls.household_id == household_id, cls.suggestion_score != 0).all()
        # compute the initial sum of all suggestion_scores
        suggestion_sum = 0
        for r in recipes:
            suggestion_sum += r.suggestion_score
        # iteratively assign increasing suggestion rank to random recipes weighted by their score
        current_rank = 1
        while len(recipes) > 0:
            choose = randint(1, suggestion_sum)
            to_be_removed = -1
            for (i, r) in enumerate(recipes):
                choose -= r.suggestion_score
                if choose <= 0:
                    r.suggestion_rank = current_rank
                    current_rank += 1
                    suggestion_sum -= r.suggestion_score
                    to_be_removed = i
                    db.session.add(r)
                    break
            recipes.pop(to_be_removed)
        db.session.commit()

    @classmethod
    def find_suggestions(cls, household_id: int,) -> list[Self]:
        sq = db.session.query(Planner.recipe_id).group_by(
            Planner.recipe_id).scalar_subquery()
        return cls.query.filter(cls.household_id == household_id, cls.id.notin_(sq)).filter(  # noqa
            cls.suggestion_rank > 0).order_by(cls.suggestion_rank).all()

    @classmethod
    def find_by_name(cls, household_id: int, name: str) -> Self:
        return cls.query.filter(cls.household_id == household_id, cls.name == name).first()

    @classmethod
    def find_by_id(cls, id: int) -> Self:
        return cls.query.filter(cls.id == id).first()

    @classmethod
    def search_name(cls, household_id: int, name: str) -> list[Self]:
        if '*' in name or '_' in name:
            looking_for = name.replace('_', '__')\
                .replace('*', '%')\
                .replace('?', '_')
        else:
            looking_for = '%{0}%'.format(name)
        return cls.query.filter(cls.household_id == household_id, cls.name.ilike(looking_for)).order_by(cls.name).all()

    @classmethod
    def all_by_name_with_filter(cls, household_id: int, filter: list[str]) -> list[Self]:
        sq = db.session.query(RecipeTags.recipe_id).join(RecipeTags.tag).filter(
            Tag.name.in_(filter)).subquery()
        return db.session.query(cls).filter(cls.household_id == household_id, cls.id.in_(sq)).order_by(cls.name).all()


class RecipeItems(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'recipe_items'

    recipe_id = db.Column(db.Integer, db.ForeignKey(
        'recipe.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    description = db.Column('description', db.String())
    optional = db.Column('optional', db.Boolean)

    item = db.relationship("Item", back_populates='recipes')
    recipe = db.relationship("Recipe", back_populates='items')

    def obj_to_item_dict(self) -> dict:
        res = self.item.obj_to_dict()
        res['description'] = getattr(self, 'description')
        res['optional'] = getattr(self, 'optional')
        res['created_at'] = getattr(self, 'created_at')
        res['updated_at'] = getattr(self, 'updated_at')
        return res

    def obj_to_recipe_dict(self) -> dict:
        res = self.recipe.obj_to_dict()
        res['items'] = [
            {
                'id': getattr(self, 'item_id'),
                'description': getattr(self, 'description'),
                'optional': getattr(self, 'optional'),
            }
        ]
        return res

    @classmethod
    def find_by_ids(cls, recipe_id: int, item_id: int) -> Self:
        return cls.query.filter(cls.recipe_id == recipe_id, cls.item_id == item_id).first()


class RecipeTags(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'recipe_tags'

    recipe_id = db.Column(db.Integer, db.ForeignKey(
        'recipe.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

    tag = db.relationship("Tag", back_populates='recipes')
    recipe = db.relationship("Recipe", back_populates='tags')

    def obj_to_item_dict(self) -> dict:
        res = self.tag.obj_to_dict()
        res['created_at'] = getattr(self, 'created_at')
        res['updated_at'] = getattr(self, 'updated_at')
        return res

    @classmethod
    def find_by_ids(cls, recipe_id: int, tag_id: int) -> Self:
        return cls.query.filter(cls.recipe_id == recipe_id, cls.tag_id == tag_id).first()
