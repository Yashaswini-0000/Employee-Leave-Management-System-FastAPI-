from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Employee
from app.schemas.schemas import UserRegister, Token, UserOut
from app.auth.security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if data.role not in {"Admin","HR","Employee"}:
        raise HTTPException(422, "Invalid role")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(409, "Username already exists")
    if data.role == "Employee" and data.employee_id:
        emp = db.get(Employee, data.employee_id)
        if not emp or not emp.is_active:
            raise HTTPException(400, "Active employee required")
    user = User(username=data.username, password_hash=hash_password(data.password), role=data.role, employee_id=data.employee_id)
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active or (user.employee and not user.employee.is_active) or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid credentials or inactive user")
    return Token(access_token=create_access_token(user.username, user.role), token_type="bearer", expires_in=settings.access_token_expire_minutes*60)

@router.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user)):
    return user
