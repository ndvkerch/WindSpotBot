"""Добавление таблицы spots

Revision ID: 6fcea6a1e1dc
Revises: 482e02c69153
Create Date: 2025-04-20 10:45:11.516244

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6fcea6a1e1dc"
down_revision: Union[str, None] = "482e02c69153"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "spots",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.UniqueConstraint("name"),  # Уникальность имени
    )


def downgrade():
    op.drop_table("spots")
