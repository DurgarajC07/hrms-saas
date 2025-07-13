"""
Benefits administration schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class BenefitType(str, Enum):
    HEALTH_INSURANCE = "health_insurance"
    DENTAL_INSURANCE = "dental_insurance"
    VISION_INSURANCE = "vision_insurance"
    LIFE_INSURANCE = "life_insurance"
    DISABILITY_INSURANCE = "disability_insurance"
    RETIREMENT_401K = "retirement_401k"
    FLEXIBLE_SPENDING_ACCOUNT = "flexible_spending_account"
    HEALTH_SAVINGS_ACCOUNT = "health_savings_account"
    PAID_TIME_OFF = "paid_time_off"
    EMPLOYEE_ASSISTANCE_PROGRAM = "employee_assistance_program"
    WELLNESS_PROGRAM = "wellness_program"
    TRANSPORTATION = "transportation"
    TUITION_REIMBURSEMENT = "tuition_reimbursement"
    CHILDCARE_ASSISTANCE = "childcare_assistance"
    OTHER = "other"


class BenefitStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    EXPIRED = "expired"


class EnrollmentStatus(str, Enum):
    ENROLLED = "enrolled"
    DECLINED = "declined"
    PENDING = "pending"
    TERMINATED = "terminated"


# Benefit Plan Schemas
class BenefitPlanBase(BaseModel):
    plan_name: str = Field(..., min_length=1, max_length=200)
    benefit_type: BenefitType
    provider_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    employee_cost_monthly: float = Field(0, ge=0)
    employer_cost_monthly: float = Field(0, ge=0)
    deductible: Optional[float] = Field(None, ge=0)
    out_of_pocket_max: Optional[float] = Field(None, ge=0)
    coverage_details: Optional[str] = None


class BenefitPlanCreate(BenefitPlanBase):
    company_id: int
    is_active: bool = True
    requires_enrollment: bool = True
    auto_enroll_eligible: bool = False


class BenefitPlanUpdate(BaseModel):
    plan_name: Optional[str] = Field(None, min_length=1, max_length=200)
    provider_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    employee_cost_monthly: Optional[float] = Field(None, ge=0)
    employer_cost_monthly: Optional[float] = Field(None, ge=0)
    deductible: Optional[float] = Field(None, ge=0)
    out_of_pocket_max: Optional[float] = Field(None, ge=0)
    coverage_details: Optional[str] = None
    is_active: Optional[bool] = None
    requires_enrollment: Optional[bool] = None
    auto_enroll_eligible: Optional[bool] = None


class BenefitPlanResponse(BenefitPlanBase):
    id: int
    company_id: int
    is_active: bool
    requires_enrollment: bool
    auto_enroll_eligible: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Benefit Enrollment Schemas
class BenefitEnrollmentBase(BaseModel):
    plan_id: int
    enrollment_date: date
    effective_date: date
    termination_date: Optional[date] = None
    coverage_tier: str = Field(..., max_length=50)  # individual, family, etc.


class BenefitEnrollmentCreate(BenefitEnrollmentBase):
    employee_id: int
    status: EnrollmentStatus = EnrollmentStatus.PENDING


class BenefitEnrollmentUpdate(BaseModel):
    termination_date: Optional[date] = None
    coverage_tier: Optional[str] = Field(None, max_length=50)
    status: Optional[EnrollmentStatus] = None


class BenefitEnrollmentResponse(BenefitEnrollmentBase):
    id: int
    employee_id: int
    status: EnrollmentStatus
    monthly_employee_cost: float
    monthly_employer_cost: float
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Benefit Dependent Schemas
class BenefitDependentBase(BaseModel):
    enrollment_id: int
    dependent_name: str = Field(..., min_length=1, max_length=200)
    relationship: str = Field(..., max_length=50)  # spouse, child, etc.
    date_of_birth: date
    ssn_last_four: Optional[str] = Field(None, max_length=4)


class BenefitDependentCreate(BenefitDependentBase):
    pass


class BenefitDependentUpdate(BaseModel):
    dependent_name: Optional[str] = Field(None, min_length=1, max_length=200)
    relationship: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[date] = None
    ssn_last_four: Optional[str] = Field(None, max_length=4)


class BenefitDependentResponse(BenefitDependentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Open Enrollment Schemas
class OpenEnrollmentBase(BaseModel):
    enrollment_year: int = Field(..., ge=2020, le=2050)
    start_date: date
    end_date: date
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class OpenEnrollmentCreate(OpenEnrollmentBase):
    company_id: int
    is_active: bool = True


class OpenEnrollmentUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class OpenEnrollmentResponse(OpenEnrollmentBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    enrollment_count: int = 0
    eligible_employees: int = 0

    class Config:
        from_attributes = True


# Enrollment Summary Schemas
class EnrollmentSummary(BaseModel):
    total_employees: int
    enrolled_employees: int
    pending_enrollments: int
    declined_enrollments: int
    enrollment_rate: float
    total_monthly_cost: float
    employee_monthly_cost: float
    employer_monthly_cost: float


class BenefitPlanSummary(BaseModel):
    plan: BenefitPlanResponse
    enrollment_count: int
    total_monthly_cost: float
    utilization_rate: float
