"""watched import folders: owner-chosen folders and a record of what was imported from them

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-12 18:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("settings") as batch:
        batch.add_column(sa.Column("import_dirs", sa.JSON(), nullable=False, server_default="[]"))
    op.create_table(
        "imported_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("folder", sa.String(length=1024), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("signature", sa.String(length=64), nullable=False),
        sa.Column("imported", sa.Integer(), nullable=False),
        sa.Column("screenshots", sa.Integer(), nullable=False),
        sa.Column("errors", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("folder", "name", "signature"),
    )


def downgrade() -> None:
    op.drop_table("imported_entries")
    with op.batch_alter_table("settings") as batch:
        batch.drop_column("import_dirs")
