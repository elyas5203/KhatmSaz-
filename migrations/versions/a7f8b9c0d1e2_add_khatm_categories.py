"""Add admin-managed khatm content categories (صلوات/لعن/ادعیه) + requests."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "a7f8b9c0d1e2"
down_revision = "q7r8s9t0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    group_enum = postgresql.ENUM("SALAWAT", "LAAN", "DUA", name="khatmcategorygroup", create_type=False)
    group_enum.create(op.get_bind(), checkfirst=True)
    request_status_enum = postgresql.ENUM(
        "PENDING", "FULFILLED", "DECLINED", name="khatmcategoryrequeststatus", create_type=False
    )
    request_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "khatm_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("group", group_enum, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=True),
        sa.Column("source_note", sa.String(length=300), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_khatm_categories_group_active", "khatm_categories", ["group", "is_active"])

    op.create_table(
        "khatm_category_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_title", sa.String(length=200), nullable=False),
        sa.Column("requested_by_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", request_status_enum, nullable=False),
        sa.Column("fulfilled_category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["fulfilled_category_id"], ["khatm_categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_khatm_category_requests_status", "khatm_category_requests", ["status", "created_at"])

    op.add_column("khatms", sa.Column("content_category_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_khatms_content_category_id", "khatms", "khatm_categories", ["content_category_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_khatms_content_category_id", "khatms", type_="foreignkey")
    op.drop_column("khatms", "content_category_id")
    op.drop_index("ix_khatm_category_requests_status", table_name="khatm_category_requests")
    op.drop_table("khatm_category_requests")
    op.drop_index("ix_khatm_categories_group_active", table_name="khatm_categories")
    op.drop_table("khatm_categories")
    op.execute("DROP TYPE IF EXISTS khatmcategoryrequeststatus")
    op.execute("DROP TYPE IF EXISTS khatmcategorygroup")
