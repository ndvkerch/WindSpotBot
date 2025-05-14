"""add_active_field_to_checkins

Revision ID: 0d3549bcd01a
Revises: f89b687581a6
Create Date: 2025-05-14 15:28:35.238427

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d3549bcd01a'
down_revision: Union[str, None] = 'f89b687581a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Добавление поля active с значением по умолчанию TRUE (1)
    op.add_column('checkins',
                  sa.Column('active', sa.Boolean(), nullable=False, server_default='1'))

def downgrade():
    # Удаление поля active при откате миграции
    op.drop_column('checkins', 'active')
