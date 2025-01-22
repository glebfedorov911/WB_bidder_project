from alembic import op
import sqlalchemy as sa

revision = '5dede0ba0767'
down_revision = 'cb4a47e3dc0f'
branch_labels = None
depends_on = None

def upgrade():
    token_type_enum = sa.Enum('REFRESH_TOKEN', 'ACCESS_TOKEN', name='typetoken')
    token_type_enum.create(op.get_bind())
    
    op.add_column('tokens', sa.Column('token_type', token_type_enum, nullable=False))

def downgrade():
    op.drop_column('tokens', 'token_type')

    token_type_enum = sa.Enum('REFRESH_TOKEN', 'ACCESS_TOKEN', name='typetoken')
    token_type_enum.drop(op.get_bind())
