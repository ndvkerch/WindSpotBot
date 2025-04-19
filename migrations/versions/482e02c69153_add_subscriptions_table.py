"""Add subscriptions table

Revision ID: 482e02c69153
Revises: 8cdad8ef611d
Create Date: 2025-04-19 22:23:34.430786

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "482e02c69153"
down_revision: Union[str, None] = "8cdad8ef611d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "subscriptions",
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("spot_name", sa.String, nullable=False),
        sa.Column("event_type", sa.String, nullable=False),
        sa.Column("created_at", sa.String, nullable=True),
        sa.PrimaryKeyConstraint("user_id", "spot_name", "event_type"),
    )


def downgrade():
    op.drop_table("subscriptions")
