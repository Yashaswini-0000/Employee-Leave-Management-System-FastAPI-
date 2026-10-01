from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Department, Employee
from app.schemas.schemas import DepartmentCreate, DepartmentOut, EmployeeOut
from app.dependencies import require_roles

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("", response_model=DepartmentOut, status_code=201)
def create(data: DepartmentCreate, db: Session=Depends(get_db), user=Depends(require_roles("Admin"))):
    if db.query(Department).filter(Department.department_name==data.department_name).first():
        raise HTTPException(409,"Department name already exists")
    obj=Department(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj

@router.get("", response_model=list[DepartmentOut])
def list_all(skip:int=0, limit:int=10, db:Session=Depends(get_db), user=Depends(require_roles("Admin","HR","Employee"))):
    return db.query(Department).offset(skip).limit(limit).all()

@router.get("/{department_id}", response_model=DepartmentOut)
def get_one(department_id:int, db:Session=Depends(get_db), user=Depends(require_roles("Admin","HR","Employee"))):
    obj=db.get(Department,department_id)
    if not obj: raise HTTPException(404,"Department not found")
    return obj

@router.put("/{department_id}", response_model=DepartmentOut)
def update(department_id:int, data:DepartmentCreate, db:Session=Depends(get_db), user=Depends(require_roles("Admin"))):
    obj=db.get(Department,department_id)
    if not obj: raise HTTPException(404,"Department not found")
    if db.query(Department).filter(Department.department_name==data.department_name, Department.id!=department_id).first():
        raise HTTPException(409,"Department name already exists")
    for k,v in data.model_dump().items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj

@router.delete("/{department_id}")
def delete(department_id:int, db:Session=Depends(get_db), user=Depends(require_roles("Admin"))):
    obj=db.get(Department,department_id)
    if not obj: raise HTTPException(404,"Department not found")
    if db.query(Employee).filter(Employee.department_id==department_id, Employee.is_active==True).first():
        raise HTTPException(409,"Department has active employees")
    obj.is_active=False; db.commit()
    return {"message":"Department deactivated"}

@router.get("/{department_id}/employees", response_model=list[EmployeeOut])
def employees(department_id:int, skip:int=0, limit:int=10, db:Session=Depends(get_db), user=Depends(require_roles("Admin","HR","Employee"))):
    if not db.get(Department,department_id): raise HTTPException(404,"Department not found")
    return db.query(Employee).filter(Employee.department_id==department_id).offset(skip).limit(limit).all()
