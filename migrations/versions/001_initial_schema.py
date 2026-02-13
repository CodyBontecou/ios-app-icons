"""Initial database schema.

Revision ID: 001
Revises:
Create Date: 2026-01-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed')")
    op.execute("CREATE TYPE plan_tier AS ENUM ('free', 'pro', 'business', 'enterprise')")
    op.execute("CREATE TYPE subscription_status AS ENUM ('active', 'canceled', 'past_due')")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('avatar_url', sa.String(512), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('status', postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='job_status', create_type=False), nullable=False, server_default='pending', index=True),
        sa.Column('params', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create icons table
    op.create_table(
        'icons',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('variant_number', sa.Integer(), nullable=False),
        sa.Column('storage_url', sa.String(512), nullable=False),
        sa.Column('sizes', postgresql.JSON(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True, index=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True, unique=True),
        sa.Column('plan_tier', postgresql.ENUM('free', 'pro', 'business', 'enterprise', name='plan_tier', create_type=False), nullable=False, server_default='free'),
        sa.Column('status', postgresql.ENUM('active', 'canceled', 'past_due', name='subscription_status', create_type=False), nullable=False, server_default='active'),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Create usage table
    op.create_table(
        'usage',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('year_month', sa.String(7), nullable=False),
        sa.Column('generations_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('user_id', 'year_month', name='uq_usage_user_month'),
    )

    # Create composite index on usage table
    op.create_index('ix_usage_user_month', 'usage', ['user_id', 'year_month'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_usage_user_month', table_name='usage')
    op.drop_table('usage')
    op.drop_table('subscriptions')
    op.drop_table('icons')
    op.drop_table('jobs')
    op.drop_table('users')

    # Drop enum types
    op.execute('DROP TYPE subscription_status')
    op.execute('DROP TYPE plan_tier')
    op.execute('DROP TYPE job_status')
