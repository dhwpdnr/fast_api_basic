"""Create Phone number for user column

Revision ID: a98c11e35dff
Revises: 
Create Date: 2024-06-26 19:43:22.888440

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a98c11e35dff'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "phone_number")
