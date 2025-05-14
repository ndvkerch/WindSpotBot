"""Добавление колонки created_by в таблицу spots

Revision ID: 9f3d25a02472
Revises: 7a73061bc6bc
Create Date: 2025-04-21 10:07:37.226375

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f3d25a02472"
down_revision: Union[str, None] = "7a73061bc6bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("spots", sa.Column("created_by", sa.Integer, nullable=False))


def downgrade():
    op.drop_column("spots", "created_by")
