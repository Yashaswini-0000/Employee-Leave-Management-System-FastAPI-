from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Employee, Department
from app.schemas.schemas import EmployeeCreate, EmployeeOut
from app.dependencies import require_roles, get_current_user

router=APIRouter(prefix="/employees",tags=["Employees"])

def ensure_unique(db,data,exclude=None):
    q=db.query(Employee).filter((Employee.email==data.email)|(Employee.employee_code==data.employee_code))
    if exclude: q=q.filter(Employee.id!=exclude)
    if q.first(): raise HTTPException(409,"Email or employee code already exists")

@router.post("",response_model=EmployeeOut,status_code=201)
def create(data:EmployeeCreate,db:Session=Depends(get_db),user=Depends(require_roles("Admin","HR"))):
    if not db.get(Department,data.department_id): raise HTTPException(404,"Department not found")
    ensure_unique(db,data)
    obj=Employee(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("",response_model=list[EmployeeOut])
def list_all(name:str|None=None,department_id:int|None=None,designation:str|None=None,employment_type:str|None=None,is_active:bool|None=None,sort_by:str="name",order:str="asc",skip:int=0,limit:int=10,db:Session=Depends(get_db),user=Depends(get_current_user)):
    q=db.query(Employee)
    if user.role=="Employee":
        if not user.employee_id: return []
        q=q.filter(Employee.id==user.employee_id)
    if name: q=q.filter(Employee.name.ilike(f"%{name}%"))
    if department_id: q=q.filter(Employee.department_id==department_id)
    if designation: q=q.filter(Employee.designation==designation)
    if employment_type: q=q.filter(Employee.employment_type==employment_type)
    if is_active is not None: q=q.filter(Employee.is_active==is_active)
    allowed={"name":Employee.name,"salary":Employee.salary,"date_of_joining":Employee.date_of_joining}
    col=allowed.get(sort_by,Employee.name)
    q=q.order_by(col.desc() if order=="desc" else col.asc())
    return q.offset(skip).limit(limit).all()

@router.get("/{employee_id}",response_model=EmployeeOut)
def get_one(employee_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    if user.role=="Employee" and user.employee_id!=employee_id: raise HTTPException(403,"Own profile only")
    obj=db.get(Employee,employee_id)
    if not obj: raise HTTPException(404,"Employee not found")
    return obj

@router.put("/{employee_id}",response_model=EmployeeOut)
def update(employee_id:int,data:EmployeeCreate,db:Session=Depends(get_db),user=Depends(require_roles("Admin","HR"))):
    obj=db.get(Employee,employee_id)
    if not obj: raise HTTPException(404,"Employee not found")
    ensure_unique(db,data,employee_id)
    if not db.get(Department,data.department_id): raise HTTPException(404,"Department not found")
    for k,v in data.model_dump().items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj

@router.delete("/{employee_id}")
def delete(employee_id:int,db:Session=Depends(get_db),user=Depends(require_roles("Admin","HR"))):
    obj=db.get(Employee,employee_id)
    if not obj: raise HTTPException(404,"Employee not found")
    obj.is_active=False; db.commit()
    return {"message":"Employee soft-deleted","employee_id":employee_id}
