# Employee & Leave Management System

A FastAPI backend for employee, department and leave management with JWT authentication, RBAC, MySQL, SQLAlchemy and Alembic.

## Features
- Admin, HR and Employee roles
- JWT tokens with configurable 30-minute default expiry
- Password hashing with bcrypt
- Department and employee management
- Employee soft delete
- Sick/Casual/Earned leave balances: 12/10/15
- Weekday-only leave calculation
- Overlap and balance validation
- Approval, rejection and cancellation workflow
- Pagination, filtering and sorting
- HR dashboard and monthly leave summary
- Alembic migrations

## Setup
1. Create a MySQL database named `employee_leave_db`.
2. Copy `.env.example` to `.env`.
3. Put your MySQL SQLAlchemy URL and a strong secret in `.env`.
4. Create a virtual environment and install `requirements.txt`.
5. Run `alembic upgrade head`.
6. Start with `uvicorn app.main:app --reload`.
7. Open `http://127.0.0.1:8000/api/docs`.

If your MySQL password contains `@`, URL-encode it as `%40` in the connection URL.

## Important
Do not commit `.env`. Commit only `.env.example`.

## Main API groups
- `/api/auth`
- `/api/departments`
- `/api/employees`
- `/api/leaves`
- `/api/reports`

## Suggested test order
Register an Admin -> login -> create Department -> create Employee -> register/login HR or Employee -> apply leave -> approve/reject -> inspect balance -> run reports.

## GitHub submission checklist
- Source code
- Alembic migration
- requirements.txt
- README.md
- .env.example
- .gitignore
- Swagger screenshots
- Tests

## Note
The included health endpoint confirms that the FastAPI process is running; it does not prove MySQL connectivity. For database verification, run the Alembic migration and test a database-backed endpoint.
