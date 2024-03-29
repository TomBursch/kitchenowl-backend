"""empty message

Revision ID: 3d667fcc5581
Revises: ed32086bf606
Create Date: 2023-06-06 14:49:25.133125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d667fcc5581'
down_revision = 'ed32086bf606'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('expense_category', schema=None) as batch_op:
        batch_op.alter_column('color',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('expense_category', schema=None) as batch_op:
        batch_op.alter_column('color',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
