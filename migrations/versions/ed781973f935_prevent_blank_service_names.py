"""Prevent blank service names

Revision ID: ed781973f935
Revises: a0499df6bfef
Create Date: 2026-11-01 20:04:43.447117

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed781973f935'
down_revision = 'a0499df6bfef'
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        "services_name_not_blank",
        "services",
        "btrim(name) <> ''"
    )


def downgrade():
    op.drop_constraint(
        "services_name_not_blank",
        "services",
        type_="check"
    )