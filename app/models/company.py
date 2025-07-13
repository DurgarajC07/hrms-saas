from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Index
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class CompanySize(str, enum.Enum):
    STARTUP = "startup"  # 1-10 employees
    SMALL = "small"      # 11-50 employees
    MEDIUM = "medium"    # 51-200 employees
    LARGE = "large"      # 201-1000 employees
    ENTERPRISE = "enterprise"  # 1000+ employees


class CompanyStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"


class Industry(str, enum.Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    CONSULTING = "consulting"
    OTHER = "other"


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255))
    registration_number = Column(String(100), unique=True)
    tax_id = Column(String(100))
    industry = Column(Enum(Industry))
    company_size = Column(Enum(CompanySize))
    status = Column(Enum(CompanyStatus), default=CompanyStatus.TRIAL)
    
    # Contact Information
    email = Column(String(255))
    phone = Column(String(20))
    website = Column(String(255))
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Geolocation for attendance
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    punch_radius = Column(Integer, default=100)  # meters
    
    # Subscription
    subscription_plan = Column(String(50))
    subscription_start = Column(DateTime(timezone=True))
    subscription_end = Column(DateTime(timezone=True))
    max_employees = Column(Integer, default=10)
    
    # Settings
    timezone = Column(String(50), default="UTC")
    currency = Column(String(3), default="USD")
    date_format = Column(String(20), default="YYYY-MM-DD")
    language = Column(String(10), default="en")
    
    # Logo and branding
    logo_url = Column(String(500))
    primary_color = Column(String(7))  # Hex color
    secondary_color = Column(String(7))
    
    # Compliance and settings
    payroll_frequency = Column(String(20), default="monthly")  # weekly, bi-weekly, monthly
    week_start_day = Column(Integer, default=1)  # 1=Monday, 7=Sunday
    fiscal_year_start = Column(String(5), default="01-01")  # MM-DD format
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    users = relationship("CompanyUser", back_populates="company")
    employees = relationship("Employee", back_populates="company")
    departments = relationship("Department", back_populates="company")
    shifts = relationship("Shift", back_populates="company")
    leaves = relationship("Leave", back_populates="company")
    payrolls = relationship("Payroll", back_populates="company")
    
    # Indexes
    __table_args__ = (
        Index('idx_company_status_subscription', 'status', 'subscription_end'),
        Index('idx_company_created_at', 'created_at'),
    )


class CompanyUser(Base):
    """Association table for users and companies with roles"""
    __tablename__ = "company_users"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)  # Company-specific role
    is_primary = Column(Boolean, default=False)  # Primary admin
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True))
    
    # Relationships
    company = relationship("Company", back_populates="users")
    user = relationship("User", back_populates="companies")
    
    # Indexes
    __table_args__ = (
        Index('idx_company_user_unique', 'company_id', 'user_id', unique=True),
        Index('idx_company_user_role', 'company_id', 'role'),
    )


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)  # e.g., ENG, HR, FIN
    description = Column(Text)
    manager_id = Column(Integer, ForeignKey("employees.id"))
    budget = Column(Numeric(15, 2))
    cost_center = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="departments")
    employees = relationship("Employee", foreign_keys="Employee.department_id", back_populates="department")
    manager = relationship("Employee", foreign_keys=[manager_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_dept_company_code', 'company_id', 'code', unique=True),
        Index('idx_dept_company_active', 'company_id', 'is_active'),
    )
