from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6)
    role: str = "Employee"
    employee_id: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: str
    is_active: bool

class DepartmentCreate(BaseModel):
    department_name: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=150)
    is_active: bool = True

class DepartmentOut(DepartmentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class EmployeeCreate(BaseModel):
    employee_code: str
    name: str
    email: EmailStr
    phone: str
    department_id: int
    designation: str
    salary: Decimal = Field(gt=0)
    date_of_joining: date
    employment_type: str
    is_active: bool = True

    @field_validator("phone")
    @classmethod
    def phone_digits(cls, v):
        if not (v.isdigit() and len(v) == 10):
            raise ValueError("Phone must contain exactly 10 digits")
        return v

    @field_validator("employment_type")
    @classmethod
    def valid_type(cls, v):
        if v not in {"Full-Time","Part-Time","Intern","Contract"}:
            raise ValueError("Invalid employment type")
        return v

    @field_validator("date_of_joining")
    @classmethod
    def not_future(cls, v):
        if v > date.today():
            raise ValueError("Date of joining cannot be in the future")
        return v

class EmployeeUpdate(EmployeeCreate):
    pass

class EmployeeOut(EmployeeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class LeaveCreate(BaseModel):
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str = Field(min_length=1)

    @field_validator("leave_type")
    @classmethod
    def valid_leave_type(cls, v):
        if v not in {"Sick","Casual","Earned"}:
            raise ValueError("Invalid leave type")
        return v

class LeaveReject(BaseModel):
    rejection_reason: str = Field(min_length=1)

class LeaveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    total_days: int
    reason: str
    status: str
    approved_by: Optional[int]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
