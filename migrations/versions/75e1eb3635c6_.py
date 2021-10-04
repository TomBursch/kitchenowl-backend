"""empty message

Revision ID: 75e1eb3635c6
Revises: 3d3333ffb91e
Create Date: 2021-09-29 12:27:21.777936

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75e1eb3635c6'
down_revision = '3d3333ffb91e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('settings',
    sa.Column('planner_feature', sa.Boolean(), nullable=False),
    sa.Column('expenses_feature', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('planner_feature', 'expenses_feature')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('settings')
    # ### end Alembic commands ###