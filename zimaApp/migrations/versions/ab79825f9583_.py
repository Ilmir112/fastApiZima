"""empty message

Revision ID: ab79825f9583
Revises: 6b699adf6b5c, 9bd5cef51db1
Create Date: 2025-06-10 13:01:43.339015

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ab79825f9583"
down_revision: Union[str, None] = ("6b699adf6b5c", "9bd5cef51db1")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
