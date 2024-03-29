from alembic import op
import sqlalchemy as sa
from . import schema

# Предполагается, что таблица 'contacts' уже существует.


def upgrade():
    # Добавляем столбец только если его еще нет
    op.add_column(
        "contacts", sa.Column("birthday", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade():
    # Предполагается, что при откате вы хотите удалить добавленный столбец
    op.drop_column("contacts", "birthday")
