from fastapi import FastAPI
from app.routers import auth, departments, employees, leaves, employee_leaves, reports

app=FastAPI(title="Employee & Leave Management System",version="1.0.0",docs_url="/api/docs",openapi_url="/api/openapi.json")
app.include_router(auth.router,prefix="/api")
app.include_router(departments.router,prefix="/api")
app.include_router(employees.router,prefix="/api")
app.include_router(leaves.router,prefix="/api")
app.include_router(employee_leaves.router,prefix="/api")
app.include_router(reports.router,prefix="/api")

@app.get("/api/healthz",tags=["Health"])
def healthz():
    return {"status":"ok"}
