from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Index, Date, Decimal, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class LeaveType(str, enum.Enum):
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    BEREAVEMENT = "bereavement"
    UNPAID = "unpaid"
    EMERGENCY = "emergency"


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    WITHDRAWN = "withdrawn"


class Leave(Base):
    __tablename__ = "leaves"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Leave details
    leave_type = Column(Enum(LeaveType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_requested = Column(Decimal(4, 2), nullable=False)
    days_approved = Column(Decimal(4, 2))
    
    # Request details
    reason = Column(Text, nullable=False)
    comments = Column(Text)
    attachment_url = Column(String(500))
    
    # Status and workflow
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING)
    applied_date = Column(DateTime(timezone=True), server_default=func.now())
    approved_date = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
    rejection_reason = Column(Text)
    
    # Coverage
    coverage_by = Column(Integer, ForeignKey("employees.id"))
    coverage_notes = Column(Text)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="leaves")
    employee = relationship("Employee", back_populates="leaves")
    approver = relationship("User")
    coverage_employee = relationship("Employee", foreign_keys=[coverage_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_leave_emp_dates', 'employee_id', 'start_date', 'end_date'),
        Index('idx_leave_status_date', 'status', 'applied_date'),
        Index('idx_leave_company_status', 'company_id', 'status'),
    )


class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(Enum(LeaveType), nullable=False)
    year = Column(Integer, nullable=False)
    
    # Balance tracking
    allocated_days = Column(Decimal(5, 2), default=0)
    used_days = Column(Decimal(5, 2), default=0)
    pending_days = Column(Decimal(5, 2), default=0)
    available_days = Column(Decimal(5, 2), default=0)
    
    # Carry forward
    carried_forward = Column(Decimal(5, 2), default=0)
    max_carry_forward = Column(Decimal(5, 2), default=0)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee")
    
    # Indexes
    __table_args__ = (
        Index('idx_leave_balance_emp_type_year', 'employee_id', 'leave_type', 'year', unique=True),
    )


class LeavePolicy(Base):
    __tablename__ = "leave_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    policy_name = Column(String(200), nullable=False)
    leave_type = Column(Enum(LeaveType), nullable=False)
    
    # Policy rules
    days_per_year = Column(Decimal(5, 2), nullable=False)
    min_service_period = Column(Integer, default=0)  # months
    max_consecutive_days = Column(Integer)
    min_advance_notice = Column(Integer, default=1)  # days
    
    # Accrual settings
    accrual_frequency = Column(String(20), default="yearly")  # monthly, quarterly, yearly
    prorate_on_joining = Column(Boolean, default=True)
    
    # Carry forward rules
    allow_carry_forward = Column(Boolean, default=False)
    max_carry_forward_days = Column(Decimal(5, 2), default=0)
    carry_forward_expiry_months = Column(Integer, default=12)
    
    # Approval settings
    requires_approval = Column(Boolean, default=True)
    auto_approve_threshold = Column(Decimal(4, 2))  # days
    
    # Applicable to
    applicable_to_all = Column(Boolean, default=True)
    applicable_employee_types = Column(String(200))  # JSON array
    applicable_departments = Column(String(200))  # JSON array
    
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
        Index('idx_leave_policy_company_type', 'company_id', 'leave_type'),
        Index('idx_leave_policy_active', 'is_active', 'effective_from', 'effective_to'),
    )
