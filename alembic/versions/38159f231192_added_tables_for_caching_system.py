"""added tables for caching system

Revision ID: 38159f231192
Revises: 2fc8c5836a0b
Create Date: 2014-03-28 10:15:03.949971

"""

# revision identifiers, used by Alembic.
revision = '38159f231192'
down_revision = '2fc8c5836a0b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('cachereference',
    sa.Column('cache_id', sa.String(length=128), nullable=False),
    sa.Column('type', sa.String(length=16), nullable=False),
    sa.Column('uri', sa.UnicodeText(length=8332), nullable=False),
    sa.PrimaryKeyConstraint('cache_id')
    )
    op.create_index('ix_cachereference_cache_id', 'cachereference', ['cache_id'], unique=True)
    op.create_index('ix_cachereference_type', 'cachereference', ['type'], unique=False)
    op.create_table('cachevalues',
    sa.Column('cache_id', sa.String(length=128), nullable=False),
    sa.Column('value_id', sa.Integer(), nullable=True),
    sa.Column('value_name', sa.Unicode(length=128), nullable=True),
    sa.ForeignKeyConstraint(['cache_id'], ['cachereference.cache_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('cache_id')
    )
    op.create_index('ix_cachevalues_cache_id', 'cachevalues', ['cache_id'], unique=False)
    op.create_index('ix_cachevalues_value_id', 'cachevalues', ['value_id'], unique=False)
    op.create_index('ix_cachevalues_value_name', 'cachevalues', ['value_name'], unique=False)
    op.create_table('cachecontainers',
    sa.Column('cache_id', sa.String(length=128), nullable=False),
    sa.Column('container_id', sa.Integer(), nullable=True),
    sa.Column('container_name', sa.Unicode(length=128), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cache_id'], ['cachereference.cache_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('cache_id')
    )
    op.create_index('ix_cachecontainers_cache_id', 'cachecontainers', ['cache_id'], unique=False)
    op.create_index('ix_cachecontainers_container_id', 'cachecontainers', ['container_id'], unique=False)
    op.create_index('ix_cachecontainers_container_name', 'cachecontainers', ['container_name'], unique=False)
    op.create_table('cachekeys',
    sa.Column('cache_id', sa.String(length=128), nullable=False),
    sa.Column('key_id', sa.Integer(), nullable=True),
    sa.Column('key_name', sa.Unicode(length=128), nullable=True),
    sa.ForeignKeyConstraint(['cache_id'], ['cachereference.cache_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('cache_id')
    )
    op.create_index('ix_cachekeys_cache_id', 'cachekeys', ['cache_id'], unique=False)
    op.create_index('ix_cachekeys_key_id', 'cachekeys', ['key_id'], unique=False)
    op.create_index('ix_cachekeys_key_name', 'cachekeys', ['key_name'], unique=False)
    op.create_table('cachetags',
    sa.Column('cache_id', sa.String(length=128), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.Column('tag_name', sa.Unicode(length=128), nullable=True),
    sa.ForeignKeyConstraint(['cache_id'], ['cachereference.cache_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('cache_id')
    )
    op.create_index('ix_cachetags_cache_id', 'cachetags', ['cache_id'], unique=False)
    op.create_index('ix_cachetags_tag_id', 'cachetags', ['tag_id'], unique=False)
    op.create_index('ix_cachetags_tag_name', 'cachetags', ['tag_name'], unique=False)


def downgrade():
    op.drop_index('ix_cachetags_tag_name', table_name='cachetags')
    op.drop_index('ix_cachetags_tag_id', table_name='cachetags')
    op.drop_index('ix_cachetags_cache_id', table_name='cachetags')
    op.drop_table('cachetags')
    op.drop_index('ix_cachekeys_key_name', table_name='cachekeys')
    op.drop_index('ix_cachekeys_key_id', table_name='cachekeys')
    op.drop_index('ix_cachekeys_cache_id', table_name='cachekeys')
    op.drop_table('cachekeys')
    op.drop_index('ix_cachecontainers_container_name', table_name='cachecontainers')
    op.drop_index('ix_cachecontainers_container_id', table_name='cachecontainers')
    op.drop_index('ix_cachecontainers_cache_id', table_name='cachecontainers')
    op.drop_table('cachecontainers')
    op.drop_index('ix_cachevalues_value_name', table_name='cachevalues')
    op.drop_index('ix_cachevalues_value_id', table_name='cachevalues')
    op.drop_index('ix_cachevalues_cache_id', table_name='cachevalues')
    op.drop_table('cachevalues')
    op.drop_index('ix_cachereference_type', table_name='cachereference')
    op.drop_index('ix_cachereference_cache_id', table_name='cachereference')
    op.drop_table('cachereference')