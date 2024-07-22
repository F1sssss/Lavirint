"""Nova logika praćenja rednih brojeva faktura i knjižnih odobrenja, efi_ordinal_number i internal_ordinal_number u tabeli faktura i knjizno_odobrenje, nova tabela ordinal_number_counter i ordinal_number_counter_type

Revision ID: 005
Revises: 004
Create Date: 2023-12-31 02:38:55.884051

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ordinal_number_counter_type',
    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ordinal_number_counter',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('last_value', sa.Integer(), nullable=True),
    sa.Column('payment_device_id', sa.Integer(), nullable=True),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['payment_device_id'], ['naplatni_uredjaj.id'], name='FK_085E34139A95'),
    sa.ForeignKeyConstraint(['type_id'], ['ordinal_number_counter_type.id'], name='FK_EE03E095368A'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('faktura', sa.Column('efi_ordinal_number', sa.Integer(), nullable=True))
    op.add_column('faktura', sa.Column('internal_ordinal_number', sa.Integer(), nullable=True))
    op.add_column('knjizno_odobrenje', sa.Column('efi_ordinal_number', sa.Integer(), nullable=True))
    op.add_column('knjizno_odobrenje', sa.Column('internal_ordinal_number', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('knjizno_odobrenje', 'internal_ordinal_number')
    op.drop_column('knjizno_odobrenje', 'efi_ordinal_number')
    op.drop_column('faktura', 'internal_ordinal_number')
    op.drop_column('faktura', 'efi_ordinal_number')
    op.drop_table('ordinal_number_counter')
    op.drop_table('ordinal_number_counter_type')
    # ### end Alembic commands ###
