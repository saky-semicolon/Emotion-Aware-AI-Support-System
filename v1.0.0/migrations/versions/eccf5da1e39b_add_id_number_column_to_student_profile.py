"""Add id_number column to student_profile table"""

# revision identifiers, used by Alembic.
revision = 'eccf5da1e39b'
down_revision = None
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    # Step 1: Add column without unique constraint first
    with op.batch_alter_table('student_profile', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id_number', sa.String(length=50), nullable=False, server_default='DEFAULT_ID'))

    # Step 2: Remove server default (optional but recommended)
    with op.batch_alter_table('student_profile', schema=None) as batch_op:
        batch_op.alter_column('id_number', server_default=None)

    # Step 3: Update duplicate values with unique IDs (using profile_id)
    op.execute("""
        DO $$
        DECLARE 
            rec RECORD;
        BEGIN
            FOR rec IN SELECT profile_id FROM student_profile WHERE id_number = 'DEFAULT_ID' LOOP
                UPDATE student_profile 
                SET id_number = 'ID_' || rec.profile_id 
                WHERE profile_id = rec.profile_id;
            END LOOP;
        END
        $$;
    """)

    # Step 4: Add the unique constraint now that values are unique
    with op.batch_alter_table('student_profile', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_student_profile_id_number', ['id_number'])


def downgrade():
    with op.batch_alter_table('student_profile', schema=None) as batch_op:
        batch_op.drop_constraint('uq_student_profile_id_number', type_='unique')
        batch_op.drop_column('id_number')
