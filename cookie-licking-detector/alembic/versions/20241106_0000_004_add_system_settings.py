"""Add system_settings table for persistent configuration

Revision ID: 004_add_system_settings
Revises: 003_complete_schema
Create Date: 2025-11-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_system_settings'
down_revision = '003_complete_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create system_settings table for database-backed configuration."""
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('claim_timeout_hours', sa.Integer(), nullable=False, server_default='24'),
        sa.Column('max_claims_per_user', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('auto_release_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('webhook_secret', sa.String(length=255), nullable=True),
        sa.Column('notification_settings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('rate_limiting', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('github_integration', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_settings_id'), 'system_settings', ['id'], unique=False)
    
    # Insert default settings row
    op.execute("""
        INSERT INTO system_settings (
            id, 
            claim_timeout_hours, 
            max_claims_per_user, 
            auto_release_enabled,
            notification_settings,
            rate_limiting,
            github_integration
        ) VALUES (
            1,
            24,
            3,
            true,
            '{"email_enabled": false, "slack_enabled": false, "discord_enabled": false}'::json,
            '{"enabled": true, "requests_per_minute": 60}'::json,
            '{"app_id": null, "installation_id": null, "webhook_url": null}'::json
        )
    """)


def downgrade() -> None:
    """Drop system_settings table."""
    op.drop_index(op.f('ix_system_settings_id'), table_name='system_settings')
    op.drop_table('system_settings')
