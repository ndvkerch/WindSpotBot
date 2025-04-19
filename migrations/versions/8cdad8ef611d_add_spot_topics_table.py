"""Add spot_topics table

Revision ID: 8cdad8ef611d
Revises:
Create Date: 2025-04-19 19:51:23.434352

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8cdad8ef611d"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "spot_topics",
        sa.Column("spot_name", sa.String, primary_key=True),
        sa.Column("thread_id", sa.Integer, nullable=False),
    )


def downgrade():
    op.drop_table("spot_topics")
