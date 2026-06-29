"""add_interview_messages_table

Revision ID: b3a4c5d6e7f8
Revises: b2a3c4d5e6f7
Create Date: 2026-06-24 14:50:02.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3a4c5d6e7f8'
down_revision: Union[str, None] = 'b2a3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'interview_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('interview_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('question_index', sa.Integer(), nullable=True),
        sa.Column('score', sa.DECIMAL(precision=3, scale=1), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_interview_messages_id'), 'interview_messages', ['id'], unique=False)
    op.create_index(op.f('ix_interview_messages_interview_id'), 'interview_messages', ['interview_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_interview_messages_interview_id'), table_name='interview_messages')
    op.drop_index(op.f('ix_interview_messages_id'), table_name='interview_messages')
    op.drop_table('interview_messages')