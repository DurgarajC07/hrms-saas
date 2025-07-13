from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Index, Date
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"
    PROBATION = "probation"
    NOTICE_PERIOD = "notice_period"


class EmployeeType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERN = "intern"
    CONSULTANT = "consultant"


class MaritalStatus(str, enum.Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    manager_id = Column(Integer, ForeignKey("employees.id"))
    
    # Employee Identification
    employee_id = Column(String(50), nullable=False, index=True)  # Company-specific ID
    badge_number = Column(String(50))
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    date_of_birth = Column(Date)
    gender = Column(Enum(Gender))
    marital_status = Column(Enum(MaritalStatus))
    nationality = Column(String(100))
    blood_group = Column(String(10))
    
    # Contact Information
    personal_email = Column(String(255))
    work_email = Column(String(255))
    phone = Column(String(20))
    mobile = Column(String(20))
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relationship = Column(String(50))
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Employment Details
    employee_type = Column(Enum(EmployeeType), default=EmployeeType.FULL_TIME)
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.PROBATION)
    hire_date = Column(Date, nullable=False)
    probation_end_date = Column(Date)
    confirmation_date = Column(Date)
    termination_date = Column(Date)
    last_working_day = Column(Date)
    
    # Job Information
    job_title = Column(String(200), nullable=False)
    job_level = Column(String(50))
    job_code = Column(String(50))
    reporting_to = Column(String(200))
    work_location = Column(String(255))
    shift_id = Column(Integer, ForeignKey("shifts.id"))
    
    # Compensation
    base_salary = Column(Numeric(15, 2))
    currency = Column(String(3), default="USD")
    pay_frequency = Column(String(20), default="monthly")  # weekly, bi-weekly, monthly
    overtime_eligible = Column(Boolean, default=True)
    
    # Benefits and Policies
    health_insurance_eligible = Column(Boolean, default=True)
    life_insurance_eligible = Column(Boolean, default=True)
    retirement_plan_eligible = Column(Boolean, default=True)
    vacation_days_per_year = Column(Integer, default=20)
    sick_days_per_year = Column(Integer, default=10)
    
    # Tax and Legal
    social_security_number = Column(String(50))  # Encrypted
    tax_id = Column(String(50))
    bank_account_number = Column(String(100))  # Encrypted
    bank_routing_number = Column(String(50))
    bank_name = Column(String(200))
    
    # Documents
    profile_picture = Column(String(500))
    resume_file = Column(String(500))
    contract_file = Column(String(500))
    
    # System fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="employees")
    user = relationship("User", foreign_keys=[user_id])
    department = relationship("Department", foreign_keys=[department_id], back_populates="employees")
    manager = relationship("Employee", remote_side=[id])
    shift = relationship("Shift", back_populates="employees")
    creator = relationship("User", foreign_keys=[created_by])
    attendances = relationship("Attendance", back_populates="employee")
    leaves = relationship("Leave", foreign_keys="Leave.employee_id", back_populates="employee")
    payrolls = relationship("PayrollEmployee", back_populates="employee")
    performances = relationship("Performance", foreign_keys="Performance.employee_id", back_populates="employee")
    assets = relationship("AssetAssignment", back_populates="employee")
    expenses = relationship("Expense", back_populates="employee")
    benefit_enrollments = relationship("BenefitEnrollment", back_populates="employee")
    documents = relationship("Document", back_populates="employee")
    onboarding_checklists = relationship("OnboardingChecklist", foreign_keys="OnboardingChecklist.employee_id", back_populates="employee")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_emp_company_id', 'company_id', 'employee_id', unique=True),
        Index('idx_emp_status_type', 'status', 'employee_type'),
        Index('idx_emp_department', 'department_id', 'status'),
        Index('idx_emp_manager', 'manager_id'),
        Index('idx_emp_hire_date', 'hire_date'),
    )


class EmployeeDocument(Base):
    __tablename__ = "employee_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    document_type = Column(String(100), nullable=False)  # resume, contract, id_proof, etc.
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    is_confidential = Column(Boolean, default=False)
    expiry_date = Column(Date)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    employee = relationship("Employee")
    uploader = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_emp_doc_type', 'employee_id', 'document_type'),
        Index('idx_emp_doc_expiry', 'expiry_date'),
    )
