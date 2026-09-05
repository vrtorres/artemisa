"""Add priority, due date and scope to tasks."""

import sqlalchemy as sa

from alembic import op

revision = "20260905_0002"
down_revision = "20260905_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column(
            "priority",
            sa.Enum("baja", "media", "alta", "urgente", name="taskpriority"),
            server_default="media",
            nullable=False,
        ),
    )
    op.add_column("tasks", sa.Column("due_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "tasks",
        sa.Column(
            "scope",
            sa.Enum(
                "personal",
                "trabajo",
                "familia",
                "emprendimiento",
                name="taskscope",
            ),
            server_default="personal",
            nullable=False,
        ),
    )
    op.create_index("ix_tasks_priority_scope", "tasks", ["priority", "scope"])
    op.create_index("ix_tasks_due_date", "tasks", ["due_date"])


def downgrade() -> None:
    op.drop_index("ix_tasks_due_date", table_name="tasks")
    op.drop_index("ix_tasks_priority_scope", table_name="tasks")
    op.drop_column("tasks", "scope")
    op.drop_column("tasks", "due_date")
    op.drop_column("tasks", "priority")
