from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Index, Date, Text
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ExpenseCategory(str, enum.Enum):
    TRAVEL = "travel"
    MEALS = "meals"
    ACCOMMODATION = "accommodation"
    TRANSPORT = "transport"
    OFFICE_SUPPLIES = "office_supplies"
    SOFTWARE = "software"
    TRAINING = "training"
    MEDICAL = "medical"
    OTHER = "other"


class ExpenseStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    REIMBURSED = "reimbursed"
    CANCELLED = "cancelled"


class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Expense details
    expense_number = Column(String(100), nullable=False, unique=True)
    category = Column(Enum(ExpenseCategory), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="USD")
    expense_date = Column(Date, nullable=False)
    
    # Receipt information
    receipt_url = Column(String(500))
    receipt_number = Column(String(100))
    vendor_name = Column(String(200))
    
    # Approval workflow
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.DRAFT)
    submitted_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
    rejection_reason = Column(Text)
    
    # Reimbursement
    reimbursed_at = Column(DateTime(timezone=True))
    reimbursed_amount = Column(Numeric(15, 2))
    reimbursement_reference = Column(String(100))
    
    # Project/client tracking
    project_id = Column(Integer, ForeignKey("projects.id"))
    client_billable = Column(Boolean, default=False)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee")
    approver = relationship("User")
    project = relationship("Project")
    
    # Indexes
    __table_args__ = (
        Index('idx_expense_emp_date', 'employee_id', 'expense_date'),
        Index('idx_expense_status', 'status', 'submitted_at'),
        Index('idx_expense_company', 'company_id', 'status'),
    )


class ExpensePolicy(Base):
    __tablename__ = "expense_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    policy_name = Column(String(200), nullable=False)
    category = Column(Enum(ExpenseCategory), nullable=False)
    
    # Policy limits
    max_amount_per_expense = Column(Numeric(15, 2))
    max_amount_per_month = Column(Numeric(15, 2))
    requires_receipt = Column(Boolean, default=True)
    receipt_required_above = Column(Numeric(10, 2), default=25.00)
    
    # Approval rules
    requires_approval = Column(Boolean, default=True)
    auto_approve_below = Column(Numeric(10, 2))
    approval_levels = Column(Text)  # JSON array of approval levels
    
    # Applicable employees
    applicable_to_all = Column(Boolean, default=True)
    applicable_departments = Column(Text)  # JSON array
    applicable_employee_types = Column(Text)  # JSON array
    
    # Status
    is_active = Column(Boolean, default=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company")
    creator = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_expense_policy_company', 'company_id', 'is_active'),
        Index('idx_expense_policy_category', 'category', 'is_active'),
    )


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    project_code = Column(String(50), nullable=False)
    project_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Project details
    client_name = Column(String(200))
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(Numeric(15, 2))
    currency = Column(String(3), default="USD")
    
    # Project manager
    manager_id = Column(Integer, ForeignKey("employees.id"))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_billable = Column(Boolean, default=True)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company")
    manager = relationship("Employee")
    
    # Indexes
    __table_args__ = (
        Index('idx_project_company_code', 'company_id', 'project_code', unique=True),
        Index('idx_project_active', 'is_active', 'start_date'),
    )
