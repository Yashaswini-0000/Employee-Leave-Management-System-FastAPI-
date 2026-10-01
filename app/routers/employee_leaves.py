from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Employee, LeaveRequest
from app.dependencies import get_current_user
from app.routers.leaves import ALLOW

router=APIRouter(prefix="/employees",tags=["Employee Leave"])

@router.get("/{employee_id}/leaves")
def employee_leaves(employee_id:int,skip:int=0,limit:int=10,db:Session=Depends(get_db),user=Depends(get_current_user)):
    if user.role=="Employee" and user.employee_id!=employee_id: raise HTTPException(403,"Own records only")
    if not db.get(Employee,employee_id): raise HTTPException(404,"Employee not found")
    return db.query(LeaveRequest).filter(LeaveRequest.employee_id==employee_id).offset(skip).limit(limit).all()

@router.get("/{employee_id}/leave-balance")
def balance(employee_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    if user.role=="Employee" and user.employee_id!=employee_id: raise HTTPException(403,"Own records only")
    if not db.get(Employee,employee_id): raise HTTPException(404,"Employee not found")
    result={}
    for typ,allowed in ALLOW.items():
        used=sum(x.total_days for x in db.query(LeaveRequest).filter(LeaveRequest.employee_id==employee_id,LeaveRequest.leave_type==typ,LeaveRequest.status=="Approved").all())
        result[typ]={"allocated":allowed,"used":used,"remaining":max(allowed-used,0)}
    return result
