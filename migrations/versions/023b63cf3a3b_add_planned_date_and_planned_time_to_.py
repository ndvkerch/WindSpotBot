"""Add planned_date and planned_time to checkins

Revision ID: 023b63cf3a3b
Revises: 0d3549bcd01a
Create Date: 2025-05-15 15:09:04.066112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '023b63cf3a3b'
down_revision: Union[str, None] = '0d3549bcd01a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Добавляем столбцы planned_date и planned_time в таблицу checkins
    op.add_column('checkins', sa.Column('planned_date', sa.Date(), nullable=True))
    op.add_column('checkins', sa.Column('planned_time', sa.String(length=20), nullable=True))

def downgrade():
    # Удаляем столбцы planned_date и planned_time
    op.drop_column('checkins', 'planned_time')
    op.drop_column('checkins', 'planned_date')
