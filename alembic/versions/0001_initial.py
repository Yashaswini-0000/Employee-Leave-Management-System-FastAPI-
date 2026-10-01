from alembic import op
import sqlalchemy as sa

revision="0001_initial"
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("departments",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("department_name",sa.String(100),nullable=False,unique=True),
        sa.Column("location",sa.String(150),nullable=False),
        sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column("created_at",sa.DateTime(),nullable=False),
        sa.Column("updated_at",sa.DateTime(),nullable=False))
    op.create_table("employees",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("employee_code",sa.String(30),nullable=False,unique=True),
        sa.Column("name",sa.String(150),nullable=False),
        sa.Column("email",sa.String(255),nullable=False,unique=True),
        sa.Column("phone",sa.String(10),nullable=False),
        sa.Column("department_id",sa.Integer(),sa.ForeignKey("departments.id"),nullable=False),
        sa.Column("designation",sa.String(100),nullable=False),
        sa.Column("salary",sa.Numeric(12,2),nullable=False),
        sa.Column("date_of_joining",sa.Date(),nullable=False),
        sa.Column("employment_type",sa.String(20),nullable=False),
        sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column("created_at",sa.DateTime(),nullable=False),
        sa.Column("updated_at",sa.DateTime(),nullable=False))
    op.create_table("users",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("username",sa.String(100),nullable=False,unique=True),
        sa.Column("password_hash",sa.String(255),nullable=False),
        sa.Column("role",sa.String(20),nullable=False),
        sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.Column("employee_id",sa.Integer(),sa.ForeignKey("employees.id"),unique=True),
        sa.Column("created_at",sa.DateTime(),nullable=False),
        sa.Column("updated_at",sa.DateTime(),nullable=False))
    op.create_table("leave_requests",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("employee_id",sa.Integer(),sa.ForeignKey("employees.id"),nullable=False),
        sa.Column("leave_type",sa.String(20),nullable=False),
        sa.Column("start_date",sa.Date(),nullable=False),
        sa.Column("end_date",sa.Date(),nullable=False),
        sa.Column("total_days",sa.Integer(),nullable=False),
        sa.Column("reason",sa.Text(),nullable=False),
        sa.Column("status",sa.String(20),nullable=False,server_default="Pending"),
        sa.Column("approved_by",sa.Integer(),sa.ForeignKey("users.id")),
        sa.Column("rejection_reason",sa.Text()),
        sa.Column("created_at",sa.DateTime(),nullable=False),
        sa.Column("updated_at",sa.DateTime(),nullable=False))

def downgrade():
    op.drop_table("leave_requests"); op.drop_table("users"); op.drop_table("employees"); op.drop_table("departments")
