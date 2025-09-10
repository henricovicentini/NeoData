"""add documento_id to raw and clean records

Revision ID: c81e6c2e4b86
Revises: ae19ce005012
Create Date: 2025-09-09 23:25:19.280819

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c81e6c2e4b86'
down_revision = 'ae19ce005012'
branch_labels = None
depends_on = None


def upgrade():
    # clean_records
    with op.batch_alter_table('clean_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('documento_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            'fk_clean_records_documento_id',  # nome da FK
            'documentos', ['documento_id'], ['id']
        )

    # raw_records
    with op.batch_alter_table('raw_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('documento_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            'fk_raw_records_documento_id',  # nome da FK
            'documentos', ['documento_id'], ['id']
        )


def downgrade():
    # raw_records
    with op.batch_alter_table('raw_records', schema=None) as batch_op:
        batch_op.drop_constraint('fk_raw_records_documento_id', type_='foreignkey')
        batch_op.drop_column('documento_id')

    # clean_records
    with op.batch_alter_table('clean_records', schema=None) as batch_op:
        batch_op.drop_constraint('fk_clean_records_documento_id', type_='foreignkey')
        batch_op.drop_column('documento_id')
