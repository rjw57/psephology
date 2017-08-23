"""add log_entries table

Revision ID: 6b238a7f3193
Revises: 92fd539a5ab0
Create Date: 2017-08-23 01:58:34.501463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b238a7f3193'
down_revision = '92fd539a5ab0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('log_entries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('message', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('log_entries', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_log_entries_created_at'), ['created_at'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('log_entries', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_log_entries_created_at'))

    op.drop_table('log_entries')
    # ### end Alembic commands ###
