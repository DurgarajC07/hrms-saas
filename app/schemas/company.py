from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from enum import Enum

class Industry(str, Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    CONSULTING = "consulting"
    REAL_ESTATE = "real_estate"
    OTHER = "other"

class CompanySize(str, Enum):
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"

class CompanyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

# Base Company Schema
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    industry: Optional[Industry] = None
    size: Optional[CompanySize] = None
    website: Optional[HttpUrl] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=50)
    logo_url: Optional[str] = None
    timezone: Optional[str] = Field(None, max_length=50)
    currency: Optional[str] = Field(None, max_length=3)
    fiscal_year_start: Optional[int] = Field(None, ge=1, le=12)
    status: Optional[CompanyStatus] = CompanyStatus.ACTIVE

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    name: Optional[str] = Field(None, min_length=1, max_length=200)

class CompanyInDBBase(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Company(CompanyInDBBase):
    pass

class CompanyResponse(CompanyInDBBase):
    employee_count: Optional[int] = 0
    department_count: Optional[int] = 0
    subscription_plan: Optional[str] = None

# Company Settings Schema
class CompanySettings(BaseModel):
    work_week_days: Optional[int] = Field(5, ge=1, le=7)
    work_hours_per_day: Optional[float] = Field(8.0, ge=1.0, le=24.0)
    overtime_threshold: Optional[float] = Field(40.0, ge=1.0)
    leave_accrual_enabled: Optional[bool] = True
    performance_review_frequency: Optional[str] = "annual"  # annual, semi_annual, quarterly
    probation_period_days: Optional[int] = Field(90, ge=0)
    notice_period_days: Optional[int] = Field(30, ge=0)
    expense_approval_required: Optional[bool] = True
    auto_clock_out_hours: Optional[int] = Field(12, ge=1, le=24)
    password_policy: Optional[dict] = {}
    notification_settings: Optional[dict] = {}

# Company Stats Schema
class CompanyStatsResponse(BaseModel):
    total_employees: int
    active_employees: int
    departments: int
    pending_leaves: int
    pending_expenses: int
    payroll_processed_this_month: int
    attendance_percentage: Optional[float] = None
    average_performance_rating: Optional[float] = None
    employee_satisfaction_score: Optional[float] = None
