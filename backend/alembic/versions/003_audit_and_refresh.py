from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003_audit_and_refresh'
down_revision = '002_documents'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('refresh_token', sa.String(512), nullable=True))
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orgs.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100)),
        sa.Column('resource_id', sa.String(255)),
        sa.Column('extra', postgresql.JSON(), server_default='{}'),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_audit_logs_org_id', 'audit_logs', ['org_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

def downgrade():
    op.drop_table('audit_logs')
    op.drop_column('users', 'refresh_token')
