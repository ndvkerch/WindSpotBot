"""Create users table

Revision ID: f89b687581a6
Revises: 9f3d25a02472
Create Date: 2025-05-11 22:12:48.468366

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f89b687581a6"
down_revision: Union[str, None] = "9f3d25a02472"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("username", sa.String, nullable=True),
        sa.Column("timezone", sa.String, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.current_timestamp()
        ),
    )


def downgrade():
    op.drop_table("users")
