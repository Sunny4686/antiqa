"""auction listings: end time and current bid

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-10 19:10:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("listings") as batch:
        batch.add_column(sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("current_bid_sek", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("listings") as batch:
        batch.drop_column("current_bid_sek")
        batch.drop_column("ends_at")
