from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class EmployeeType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"
    TEMPORARY = "temporary"

class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"

# Base Employee Schema
class EmployeeBase(BaseModel):
    employee_id: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    hire_date: Optional[date] = None
    termination_date: Optional[date] = None
    job_title: Optional[str] = Field(None, max_length=200)
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    employee_type: Optional[EmployeeType] = EmployeeType.FULL_TIME
    status: Optional[EmployeeStatus] = EmployeeStatus.ACTIVE
    salary: Optional[float] = Field(None, ge=0)
    hourly_rate: Optional[float] = Field(None, ge=0)
    user_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    company_id: Optional[int] = None  # Will be set by the endpoint

class EmployeeUpdate(EmployeeBase):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None

class EmployeeInDBBase(EmployeeBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Employee(EmployeeInDBBase):
    pass

class EmployeeResponse(EmployeeInDBBase):
    department_name: Optional[str] = None
    manager_name: Optional[str] = None
    user_email: Optional[str] = None

# Department Schema
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    head_employee_id: Optional[int] = None

class DepartmentCreate(DepartmentBase):
    company_id: Optional[int] = None

class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = Field(None, min_length=1, max_length=200)

class DepartmentResponse(DepartmentBase):
    id: int
    company_id: int
    employee_count: Optional[int] = 0
    head_employee_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Employee Stats Schema
class EmployeeStatsResponse(BaseModel):
    total_employees: int
    active_employees: int
    inactive_employees: int
    new_hires_this_month: int
    terminations_this_month: int
    by_department: List[dict]
    by_employee_type: List[dict]
    average_tenure: Optional[float] = None

# Org Chart Schema
class OrgChartEmployee(BaseModel):
    id: int
    name: str
    title: str
    department: Optional[str] = None
    manager_id: Optional[int] = None
    direct_reports: List['OrgChartEmployee'] = []

    class Config:
        from_attributes = True

OrgChartEmployee.model_rebuild()

# Bulk Import Schema
class BulkImportResult(BaseModel):
    success_count: int
    error_count: int
    errors: List[dict] = []
    created_employees: List[EmployeeResponse] = []
