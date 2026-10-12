"""training batches: import batch name, training flag and the owner's answer key

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-12 10:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("listings") as batch:
        batch.add_column(sa.Column("import_batch", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("training", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column("expected", sa.String(length=256), nullable=True))
        batch.create_index("ix_listings_import_batch", ["import_batch"])


def downgrade() -> None:
    with op.batch_alter_table("listings") as batch:
        batch.drop_index("ix_listings_import_batch")
        batch.drop_column("expected")
        batch.drop_column("training")
        batch.drop_column("import_batch")
