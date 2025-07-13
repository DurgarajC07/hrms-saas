from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Index, Date, Text
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class BenefitType(str, enum.Enum):
    HEALTH_INSURANCE = "health_insurance"
    DENTAL_INSURANCE = "dental_insurance"
    VISION_INSURANCE = "vision_insurance"
    LIFE_INSURANCE = "life_insurance"
    DISABILITY_INSURANCE = "disability_insurance"
    RETIREMENT_401K = "retirement_401k"
    PENSION = "pension"
    PAID_TIME_OFF = "paid_time_off"
    SICK_LEAVE = "sick_leave"
    MATERNITY_LEAVE = "maternity_leave"
    PATERNITY_LEAVE = "paternity_leave"
    FLEXIBLE_SPENDING = "flexible_spending"
    HEALTH_SAVINGS = "health_savings"
    COMMUTER_BENEFITS = "commuter_benefits"
    GYM_MEMBERSHIP = "gym_membership"
    EDUCATION_ASSISTANCE = "education_assistance"
    EMPLOYEE_ASSISTANCE = "employee_assistance"
    STOCK_OPTIONS = "stock_options"
    BONUS = "bonus"
    MEAL_ALLOWANCE = "meal_allowance"


class BenefitStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class EnrollmentStatus(str, enum.Enum):
    NOT_ENROLLED = "not_enrolled"
    ENROLLED = "enrolled"
    PENDING_ENROLLMENT = "pending_enrollment"
    DECLINED = "declined"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class EmployeeBenefitPlan(Base):
    __tablename__ = "employee_benefit_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Plan details
    plan_name = Column(String(200), nullable=False)
    plan_code = Column(String(50), unique=True, nullable=False)
    benefit_type = Column(Enum(BenefitType), nullable=False)
    description = Column(Text)
    
    # Provider information
    provider_name = Column(String(200))
    provider_contact = Column(String(500))
    policy_number = Column(String(100))
    group_number = Column(String(100))
    
    # Coverage details
    coverage_start_date = Column(Date, nullable=False)
    coverage_end_date = Column(Date)
    plan_year = Column(Integer, nullable=False)
    
    # Cost structure
    employer_contribution = Column(Numeric(10, 2), default=0)
    employee_contribution = Column(Numeric(10, 2), default=0)
    employer_contribution_percent = Column(Numeric(5, 2))
    employee_contribution_percent = Column(Numeric(5, 2))
    annual_premium = Column(Numeric(10, 2))
    
    # Eligibility
    eligibility_requirements = Column(Text)
    waiting_period_days = Column(Integer, default=0)
    minimum_hours_per_week = Column(Integer)
    eligible_employee_types = Column(Text)  # JSON array
    
    # Plan limits
    annual_maximum = Column(Numeric(10, 2))
    lifetime_maximum = Column(Numeric(10, 2))
    deductible_amount = Column(Numeric(10, 2))
    out_of_pocket_maximum = Column(Numeric(10, 2))
    
    # Status and configuration
    status = Column(Enum(BenefitStatus), default=BenefitStatus.ACTIVE)
    is_mandatory = Column(Boolean, default=False)
    allows_dependents = Column(Boolean, default=True)
    max_dependents = Column(Integer)
    requires_medical_exam = Column(Boolean, default=False)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company")
    creator = relationship("User")
    enrollments = relationship("BenefitEnrollment", back_populates="benefit_plan")
    
    # Indexes
    __table_args__ = (
        Index('idx_benefit_plan_company', 'company_id', 'status'),
        Index('idx_benefit_plan_type', 'benefit_type', 'status'),
        Index('idx_benefit_plan_year', 'plan_year', 'status'),
    )


class BenefitEnrollment(Base):
    __tablename__ = "benefit_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    benefit_plan_id = Column(Integer, ForeignKey("employee_benefit_plans.id"), nullable=False)
    
    # Enrollment details
    enrollment_date = Column(Date, nullable=False)
    effective_date = Column(Date, nullable=False)
    termination_date = Column(Date)
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.PENDING_ENROLLMENT)
    
    # Coverage selection
    coverage_level = Column(String(50))  # employee_only, employee_spouse, family, etc.
    elected_amount = Column(Numeric(10, 2))
    beneficiary_information = Column(Text)  # JSON for multiple beneficiaries
    
    # Cost breakdown
    employee_premium = Column(Numeric(10, 2), default=0)
    employer_premium = Column(Numeric(10, 2), default=0)
    total_premium = Column(Numeric(10, 2), default=0)
    payroll_deduction_amount = Column(Numeric(10, 2), default=0)
    payroll_deduction_frequency = Column(String(20), default="monthly")
    
    # Dependent information
    has_dependents = Column(Boolean, default=False)
    number_of_dependents = Column(Integer, default=0)
    dependent_information = Column(Text)  # JSON array of dependents
    
    # Evidence and documentation
    requires_evidence_of_insurability = Column(Boolean, default=False)
    evidence_submitted = Column(Boolean, default=False)
    evidence_approved = Column(Boolean, default=False)
    medical_exam_required = Column(Boolean, default=False)
    medical_exam_completed = Column(Boolean, default=False)
    
    # Approval workflow
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_date = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    enrolled_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    employee = relationship("Employee", back_populates="benefit_enrollments")
    benefit_plan = relationship("EmployeeBenefitPlan", back_populates="enrollments")
    approver = relationship("User", foreign_keys=[approved_by])
    enrolling_user = relationship("User", foreign_keys=[enrolled_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_enrollment_employee', 'employee_id', 'status'),
        Index('idx_enrollment_plan', 'benefit_plan_id', 'status'),
        Index('idx_enrollment_effective', 'effective_date', 'status'),
    )


class BenefitDependent(Base):
    __tablename__ = "benefit_dependents"
    
    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("benefit_enrollments.id"), nullable=False)
    
    # Dependent details
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    relationship_type = Column(String(50), nullable=False)  # spouse, child, domestic_partner
    gender = Column(String(10))
    ssn_last_four = Column(String(4))
    
    # Status
    is_active = Column(Boolean, default=True)
    effective_date = Column(Date, nullable=False)
    termination_date = Column(Date)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    enrollment = relationship("BenefitEnrollment")
    
    # Indexes
    __table_args__ = (
        Index('idx_dependent_enrollment', 'enrollment_id', 'is_active'),
        Index('idx_dependent_relationship', 'relationship_type', 'is_active'),
    )


class BenefitOpenEnrollment(Base):
    __tablename__ = "benefit_open_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Enrollment period details
    period_name = Column(String(200), nullable=False)
    plan_year = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Configuration
    description = Column(Text)
    enrollment_instructions = Column(Text)
    available_plans = Column(Text)  # JSON array of plan IDs
    mandatory_plans = Column(Text)  # JSON array of plan IDs
    
    # Notifications
    reminder_notifications = Column(Boolean, default=True)
    reminder_days_before = Column(Integer, default=7)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_current = Column(Boolean, default=False)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company")
    creator = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_open_enrollment_company', 'company_id', 'is_active'),
        Index('idx_open_enrollment_period', 'start_date', 'end_date'),
        Index('idx_open_enrollment_year', 'plan_year', 'is_current'),
    )
