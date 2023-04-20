from datetime import datetime
from typing import Self
from app import db
from app.helpers import DbModelMixin, TimestampMixin, DbModelAuthorizeMixin


class Expense(db.Model, DbModelMixin, TimestampMixin, DbModelAuthorizeMixin):
    __tablename__ = 'expense'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    amount = db.Column(db.Float())
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_category.id'))
    photo = db.Column(db.String(), db.ForeignKey('file.filename'))
    paid_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)

    household = db.relationship("Household", uselist=False)
    category = db.relationship("ExpenseCategory")
    paid_by = db.relationship("User")
    paid_for = db.relationship(
        'ExpensePaidFor', back_populates='expense', cascade="all, delete-orphan")
    photo_file = db.relationship("File", back_populates='expense', uselist=False)

    def obj_to_full_dict(self) -> dict:
        res = super().obj_to_dict()
        paidFor = ExpensePaidFor.query.filter(ExpensePaidFor.expense_id == self.id).join(
            ExpensePaidFor.user).order_by(
            ExpensePaidFor.expense_id).all()
        res['paid_for'] = [e.obj_to_dict() for e in paidFor]
        if (self.category):
            res['category'] = self.category.obj_to_full_dict()
        return res

    @classmethod
    def find_by_name(cls, name) -> Self:
        return cls.query.filter(cls.name == name).first()

    @classmethod
    def find_by_id(cls, id) -> Self:
        return cls.query.filter(cls.id == id).join(Expense.category, isouter=True).first()


class ExpensePaidFor(db.Model, DbModelMixin, TimestampMixin):
    __tablename__ = 'expense_paid_for'

    expense_id = db.Column(db.Integer, db.ForeignKey(
        'expense.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    factor = db.Column(db.Integer())

    expense = db.relationship("Expense", back_populates='paid_for')
    user = db.relationship("User", back_populates='expenses_paid_for')

    def obj_to_user_dict(self):
        res = self.user.obj_to_dict()
        res['factor'] = getattr(self, 'factor')
        res['created_at'] = getattr(self, 'created_at')
        res['updated_at'] = getattr(self, 'updated_at')
        return res

    @classmethod
    def find_by_ids(cls, expense_id, user_id) -> list[Self]:
        return cls.query.filter(cls.expense_id == expense_id, cls.user_id == user_id).first()
