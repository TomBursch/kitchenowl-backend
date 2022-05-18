from __future__ import annotations
from app import db
from app.helpers import DbModelMixin, TimestampMixin


class ExpenseCategory(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'expense_category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    expenses = db.relationship(
        'Expense', back_populates='category')

    def obj_to_full_dict(self) -> dict:
        res = super().obj_to_dict()
        return res

    @classmethod
    def create_by_name(cls, name) -> ExpenseCategory:
        return cls(
            name=name,
        ).save()

    @classmethod
    def find_by_name(cls, name) -> ExpenseCategory:
        return cls.query.filter(cls.name == name).first()

    @classmethod
    def find_by_id(cls, id) -> ExpenseCategory:
        return cls.query.filter(cls.id == id).first()

    @classmethod
    def delete_by_name(cls, name):
        mc = cls.find_by_name(name)
        if mc:
            mc.delete()
