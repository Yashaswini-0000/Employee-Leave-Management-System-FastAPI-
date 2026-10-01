from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import LeaveRequest, Employee
from app.schemas.schemas import LeaveCreate, LeaveOut, LeaveReject
from app.dependencies import get_current_user, require_roles

router=APIRouter(prefix="/leaves",tags=["Leave Requests"])
ALLOW={"Sick":12,"Casual":10,"Earned":15}

def weekdays(a,b):
    n=0; d=a
    while d<=b:
        if d.weekday()<5: n+=1
        d+=timedelta(days=1)
    return n

def used_days(db,employee_id,leave_type,year,exclude_id=None):
    q=db.query(LeaveRequest).filter(LeaveRequest.employee_id==employee_id,LeaveRequest.leave_type==leave_type,LeaveRequest.status=="Approved")
    if exclude_id: q=q.filter(LeaveRequest.id!=exclude_id)
    return sum(x.total_days for x in q.all() if x.start_date.year==year)

def overlapping(db,data):
    return db.query(LeaveRequest).filter(
        LeaveRequest.employee_id==data.employee_id,
        LeaveRequest.status.in_([ "Pending","Approved" ]),
        LeaveRequest.start_date<=data.end_date,
        LeaveRequest.end_date>=data.start_date
    ).first()

@router.post("",response_model=LeaveOut,status_code=201)
def create(data:LeaveCreate,db:Session=Depends(get_db),user=Depends(get_current_user)):
    if user.role=="Employee" and user.employee_id!=data.employee_id: raise HTTPException(403,"Employees can apply only for themselves")
    emp=db.get(Employee,data.employee_id)
    if not emp or not emp.is_active: raise HTTPException(400,"Inactive or unknown employee")
    if data.end_date<data.start_date: raise HTTPException(400,"End date cannot be before start date")
    if data.start_date<date.today(): raise HTTPException(400,"Past leave dates are not allowed")
    if overlapping(db,data): raise HTTPException(409,"Overlapping leave request exists")
    total=weekdays(data.start_date,data.end_date)
    if total<=0: raise HTTPException(400,"Leave must contain at least one weekday")
    if used_days(db,data.employee_id,data.leave_type,data.start_date.year)+total>ALLOW[data.leave_type]:
        raise HTTPException(409,"Insufficient leave balance")
    obj=LeaveRequest(**data.model_dump(),total_days=total,status="Pending")
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("",response_model=list[LeaveOut])
def list_all(status:str|None=None,leave_type:str|None=None,employee_id:int|None=None,from_date:date|None=None,to_date:date|None=None,skip:int=0,limit:int=10,db:Session=Depends(get_db),user=Depends(get_current_user)):
    q=db.query(LeaveRequest)
    if user.role=="Employee": q=q.filter(LeaveRequest.employee_id==user.employee_id)
    elif employee_id: q=q.filter(LeaveRequest.employee_id==employee_id)
    if status:q=q.filter(LeaveRequest.status==status)
    if leave_type:q=q.filter(LeaveRequest.leave_type==leave_type)
    if from_date:q=q.filter(LeaveRequest.start_date>=from_date)
    if to_date:q=q.filter(LeaveRequest.end_date<=to_date)
    return q.offset(skip).limit(limit).all()

@router.get("/{leave_id}",response_model=LeaveOut)
def get_one(leave_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    obj=db.get(LeaveRequest,leave_id)
    if not obj: raise HTTPException(404,"Leave not found")
    if user.role=="Employee" and obj.employee_id!=user.employee_id: raise HTTPException(403,"Own leave only")
    return obj

@router.put("/{leave_id}/approve",response_model=LeaveOut)
def approve(leave_id:int,db:Session=Depends(get_db),user=Depends(require_roles("Admin","HR"))):
    obj=db.get(LeaveRequest,leave_id)
    if not obj: raise HTTPException(404,"Leave not found")
    if obj.status!="Pending": raise HTTPException(400,"Only Pending leaves can be approved")
    if user.role=="HR" and user.employee_id==obj.employee_id: raise HTTPException(403,"HR cannot approve own leave")
    if used_days(db,obj.employee_id,obj.leave_type,obj.start_date.year)+obj.total_days>ALLOW[obj.leave_type]: raise HTTPException(409,"Insufficient balance")
    obj.status="Approved"; obj.approved_by=user.id; db.commit(); db.refresh(obj); return obj

@router.put("/{leave_id}/reject",response_model=LeaveOut)
def reject(leave_id:int,data:LeaveReject,db:Session=Depends(get_db),user=Depends(require_roles("Admin","HR"))):
    obj=db.get(LeaveRequest,leave_id)
    if not obj: raise HTTPException(404,"Leave not found")
    if obj.status!="Pending": raise HTTPException(400,"Only Pending leaves can be rejected")
    obj.status="Rejected"; obj.rejection_reason=data.rejection_reason; obj.approved_by=user.id; db.commit(); db.refresh(obj); return obj

@router.put("/{leave_id}/cancel",response_model=LeaveOut)
def cancel(leave_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    obj=db.get(LeaveRequest,leave_id)
    if not obj: raise HTTPException(404,"Leave not found")
    if obj.status!="Pending": raise HTTPException(400,"Only Pending leaves can be cancelled")
    if user.role=="Employee" and obj.employee_id!=user.employee_id: raise HTTPException(403,"Own leave only")
    obj.status="Cancelled"; db.commit(); db.refresh(obj); return obj
