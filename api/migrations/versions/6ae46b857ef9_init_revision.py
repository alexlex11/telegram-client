"""init revision

Revision ID: 6ae46b857ef9
Revises:
Create Date: 2025-04-17 17:03:20.219946

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "6ae46b857ef9"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
