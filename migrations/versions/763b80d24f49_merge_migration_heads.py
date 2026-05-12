"""merge migration heads

Revision ID: 763b80d24f49
Revises: 13a17c448fc8, 4d7469d2a726
Create Date: 2026-05-12 14:05:13.954201

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '763b80d24f49'
down_revision = ('13a17c448fc8', '4d7469d2a726')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
