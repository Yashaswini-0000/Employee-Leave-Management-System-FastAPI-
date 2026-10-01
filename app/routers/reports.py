from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.database import get_db
from app.models.models import Employee, Department, LeaveRequest
from app.dependencies import require_roles

router=APIRouter(prefix="/reports",tags=["Reports"])

@router.get("/dashboard")
def dashboard(db:Session=Depends(get_db),user=Depends(require_roles("Admin","HR"))):
    today=date.today()
    active=db.query(Employee).filter(Employee.is_active==True).count()
    total=db.query(Employee).count()
    pending=db.query(LeaveRequest).filter(LeaveRequest.status=="Pending").count()
    today_count=db.query(LeaveRequest).filter(LeaveRequest.status=="Approved",LeaveRequest.start_date<=today,LeaveRequest.end_date>=today).count()
    per_dept=[{"department":d.department_name,"employee_count":db.query(Employee).filter(Employee.department_id==d.id,Employee.is_active==True).count()} for d in db.query(Department).all()]
    return {"total_employees":total,"active_employees":active,"employees_per_department":per_dept,"pending_leave_requests":pending,"employees_on_leave_today":today_count}

@router.get("/leave-summary")
def leave_summary(month:int=Query(...,ge=1,le=12),year:int=Query(...,ge=2000),db:Session=Depends(get_db),user=Depends(require_roles("Admin","HR"))):
    rows=db.query(LeaveRequest.leave_type,LeaveRequest.status,func.count(LeaveRequest.id)).filter(extract("month",LeaveRequest.start_date)==month,extract("year",LeaveRequest.start_date)==year).group_by(LeaveRequest.leave_type,LeaveRequest.status).all()
    return [{"leave_type":a,"status":b,"count":c} for a,b,c in rows]
