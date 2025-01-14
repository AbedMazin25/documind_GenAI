from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002_documents'
down_revision = '001_initial'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orgs.id'), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('s3_key', sa.String(1000), nullable=False),
        sa.Column('file_size', sa.Integer()),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('chunk_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('indexed_at', sa.DateTime()),
    )
    op.create_index('ix_documents_org_id', 'documents', ['org_id'])

def downgrade():
    op.drop_table('documents')
