"""
Expense management schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class ExpenseCategory(str, Enum):
    TRAVEL = "travel"
    MEALS = "meals"
    ACCOMMODATION = "accommodation"
    TRANSPORTATION = "transportation"
    OFFICE_SUPPLIES = "office_supplies"
    SOFTWARE = "software"
    TRAINING = "training"
    COMMUNICATION = "communication"
    MARKETING = "marketing"
    UTILITIES = "utilities"
    MAINTENANCE = "maintenance"
    INSURANCE = "insurance"
    LEGAL = "legal"
    CONSULTING = "consulting"
    OTHER = "other"


class ExpenseStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


# Expense Schemas
class ExpenseBase(BaseModel):
    category: ExpenseCategory
    description: str = Field(..., min_length=1, max_length=500)
    amount: float = Field(..., gt=0)
    expense_date: date
    merchant: Optional[str] = Field(None, max_length=200)
    receipt_number: Optional[str] = Field(None, max_length=100)
    project_id: Optional[int] = None
    client_billable: bool = False


class ExpenseCreate(ExpenseBase):
    employee_id: int


class ExpenseUpdate(BaseModel):
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    amount: Optional[float] = Field(None, gt=0)
    expense_date: Optional[date] = None
    merchant: Optional[str] = Field(None, max_length=200)
    receipt_number: Optional[str] = Field(None, max_length=100)
    project_id: Optional[int] = None
    client_billable: Optional[bool] = None


class ExpenseResponse(ExpenseBase):
    id: int
    employee_id: int
    status: ExpenseStatus
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    approved_by: Optional[int]
    rejection_reason: Optional[str]
    reimbursed_at: Optional[datetime]
    reimbursed_amount: Optional[float]
    reimbursement_reference: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ExpenseListResponse(BaseModel):
    items: List[ExpenseResponse]
    total: int
    page: int
    per_page: int
    pages: int


# Expense Policy Schemas
class ExpensePolicyBase(BaseModel):
    policy_name: str = Field(..., min_length=1, max_length=200)
    category: ExpenseCategory
    max_amount_per_expense: Optional[float] = Field(None, gt=0)
    max_amount_per_month: Optional[float] = Field(None, gt=0)
    requires_receipt: bool = True
    receipt_required_above: float = Field(25.00, ge=0)
    requires_approval: bool = True
    auto_approve_below: Optional[float] = Field(None, ge=0)


class ExpensePolicyCreate(ExpensePolicyBase):
    company_id: int
    applicable_to_all: bool = True
    applicable_departments: Optional[List[str]] = []
    applicable_employee_types: Optional[List[str]] = []


class ExpensePolicyUpdate(BaseModel):
    policy_name: Optional[str] = Field(None, min_length=1, max_length=200)
    max_amount_per_expense: Optional[float] = Field(None, gt=0)
    max_amount_per_month: Optional[float] = Field(None, gt=0)
    requires_receipt: Optional[bool] = None
    receipt_required_above: Optional[float] = Field(None, ge=0)
    requires_approval: Optional[bool] = None
    auto_approve_below: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ExpensePolicyResponse(ExpensePolicyBase):
    id: int
    company_id: int
    applicable_to_all: bool
    applicable_departments: List[str]
    applicable_employee_types: List[str]
    approval_levels: List[dict]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = Field(None, gt=0)
    client_name: Optional[str] = Field(None, max_length=200)


class ProjectCreate(ProjectBase):
    company_id: int
    manager_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = Field(None, gt=0)
    client_name: Optional[str] = Field(None, max_length=200)
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: int
    company_id: int
    manager_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
