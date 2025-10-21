"""create user_full_view

Revision ID: 001
Revises:
Create Date: 2025-10-15

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the user_full_view."""
    op.execute("""
        CREATE OR REPLACE VIEW user_full_view AS
        SELECT 
            e.user_id,
            e.email,
            e.time_joined,
            m.user_metadata::jsonb AS metadata,
            l.last_active_time,
            array_agg(r.role) FILTER (WHERE r.role IS NOT NULL) AS roles
        FROM emailpassword_users e
        LEFT JOIN user_metadata m ON e.user_id = m.user_id
        LEFT JOIN user_last_active l ON e.user_id = l.user_id
        LEFT JOIN user_roles r ON e.user_id = r.user_id
        GROUP BY e.user_id, e.email, e.time_joined, m.user_metadata, l.last_active_time
    """)


def downgrade() -> None:
    """Drop the user_full_view."""
    op.execute("DROP VIEW IF EXISTS user_full_view")
