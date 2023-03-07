from typing import Self
from app import db
from app.helpers import DbModelMixin, TimestampMixin


class Shoppinglist(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'shoppinglist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)

    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)

    household = db.relationship("Household", uselist=False)
    items = db.relationship('ShoppinglistItems', cascade="all, delete-orphan")

    @classmethod
    def getDefault(cls) -> Self:
        return cls.find_by_id(1)

    def isDefault(self) -> bool:
        return self.id == 1


class ShoppinglistItems(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'shoppinglist_items'

    shoppinglist_id = db.Column(db.Integer, db.ForeignKey(
        'shoppinglist.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    description = db.Column('description', db.String())

    item = db.relationship("Item", back_populates='shoppinglists')
    shoppinglist = db.relationship("Shoppinglist", back_populates='items')

    def obj_to_item_dict(self) -> dict:
        res = self.item.obj_to_dict()
        res['description'] = getattr(self, 'description')
        res['created_at'] = getattr(self, 'created_at')
        res['updated_at'] = getattr(self, 'updated_at')
        return res

    @classmethod
    def find_by_ids(cls, shoppinglist_id: int, item_id: int) -> Self:
        return cls.query.filter(cls.shoppinglist_id == shoppinglist_id, cls.item_id == item_id).first()
