"""Добавление таблицы chekins

Revision ID: 7a73061bc6bc
Revises: 6fcea6a1e1dc
Create Date: 2025-04-20 10:52:13.850979

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7a73061bc6bc"
down_revision: Union[str, None] = "6fcea6a1e1dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "checkins",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("spot_id", sa.Integer, nullable=False),
        sa.Column("type", sa.Integer, nullable=False),
        sa.Column("duration", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("active_until", sa.DateTime, nullable=True),
        sa.Column("planned_at", sa.DateTime, nullable=True),
        sa.Column("description", sa.String, nullable=True),
        sa.ForeignKeyConstraint(["spot_id"], ["spots.id"]),
    )


def downgrade():
    op.drop_table("checkins")
