from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Index, Date, Decimal, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PayrollStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    PROCESSED = "processed"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class PayrollType(str, enum.Enum):
    REGULAR = "regular"
    BONUS = "bonus"
    FINAL_SETTLEMENT = "final_settlement"
    ADVANCE = "advance"


class PayComponent(str, enum.Enum):
    # Earnings
    BASIC_SALARY = "basic_salary"
    HRA = "hra"
    TRANSPORT_ALLOWANCE = "transport_allowance"
    MEDICAL_ALLOWANCE = "medical_allowance"
    PERFORMANCE_BONUS = "performance_bonus"
    OVERTIME = "overtime"
    COMMISSION = "commission"
    
    # Deductions
    PF = "pf"
    ESI = "esi"
    INCOME_TAX = "income_tax"
    PROFESSIONAL_TAX = "professional_tax"
    LOAN_EMI = "loan_emi"
    ADVANCE_DEDUCTION = "advance_deduction"


class Payroll(Base):
    __tablename__ = "payrolls"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    payroll_id = Column(String(100), nullable=False, unique=True)
    
    # Period
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    
    # Type and status
    payroll_type = Column(Enum(PayrollType), default=PayrollType.REGULAR)
    status = Column(Enum(PayrollStatus), default=PayrollStatus.DRAFT)
    
    # Summary
    total_employees = Column(Integer, default=0)
    total_gross_pay = Column(Decimal(15, 2), default=0)
    total_deductions = Column(Decimal(15, 2), default=0)
    total_net_pay = Column(Decimal(15, 2), default=0)
    
    # Processing details
    processed_at = Column(DateTime(timezone=True))
    processed_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="payrolls")
    employees = relationship("PayrollEmployee", back_populates="payroll")
    processor = relationship("User", foreign_keys=[processed_by])
    approver = relationship("User", foreign_keys=[approved_by])
    creator = relationship("User", foreign_keys=[created_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_payroll_company_period', 'company_id', 'pay_period_start', 'pay_period_end'),
        Index('idx_payroll_status', 'status'),
        Index('idx_payroll_pay_date', 'pay_date'),
    )


class PayrollEmployee(Base):
    __tablename__ = "payroll_employees"
    
    id = Column(Integer, primary_key=True, index=True)
    payroll_id = Column(Integer, ForeignKey("payrolls.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Basic info
    employee_name = Column(String(200), nullable=False)
    employee_code = Column(String(50), nullable=False)
    department = Column(String(100))
    designation = Column(String(200))
    
    # Salary structure
    base_salary = Column(Decimal(15, 2), nullable=False)
    
    # Attendance data
    days_worked = Column(Decimal(5, 2), default=0)
    days_absent = Column(Decimal(5, 2), default=0)
    overtime_hours = Column(Decimal(5, 2), default=0)
    
    # Calculated amounts
    gross_pay = Column(Decimal(15, 2), default=0)
    total_deductions = Column(Decimal(15, 2), default=0)
    net_pay = Column(Decimal(15, 2), default=0)
    
    # Tax calculations
    taxable_income = Column(Decimal(15, 2), default=0)
    tax_deducted = Column(Decimal(15, 2), default=0)
    
    # Status
    is_processed = Column(Boolean, default=False)
    is_paid = Column(Boolean, default=False)
    payment_date = Column(DateTime(timezone=True))
    payment_reference = Column(String(100))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    payroll = relationship("Payroll", back_populates="employees")
    employee = relationship("Employee", back_populates="payrolls")
    components = relationship("PayrollComponent", back_populates="payroll_employee")
    
    # Indexes
    __table_args__ = (
        Index('idx_payroll_emp_unique', 'payroll_id', 'employee_id', unique=True),
        Index('idx_payroll_emp_status', 'is_processed', 'is_paid'),
    )


class PayrollComponent(Base):
    __tablename__ = "payroll_components"
    
    id = Column(Integer, primary_key=True, index=True)
    payroll_employee_id = Column(Integer, ForeignKey("payroll_employees.id"), nullable=False)
    component_type = Column(Enum(PayComponent), nullable=False)
    component_name = Column(String(100), nullable=False)
    
    # Amount calculation
    amount = Column(Decimal(15, 2), nullable=False)
    is_percentage = Column(Boolean, default=False)
    percentage_value = Column(Decimal(5, 2))
    calculation_base = Column(String(50))  # basic_salary, gross_pay, etc.
    
    # Tax treatment
    is_taxable = Column(Boolean, default=True)
    is_pf_applicable = Column(Boolean, default=True)
    is_esi_applicable = Column(Boolean, default=True)
    
    # Relationships
    payroll_employee = relationship("PayrollEmployee", back_populates="components")
    
    # Indexes
    __table_args__ = (
        Index('idx_payroll_comp_type', 'payroll_employee_id', 'component_type'),
    )


class SalaryStructure(Base):
    __tablename__ = "salary_structures"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Structure details
    structure_name = Column(String(100), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    
    # Basic components
    basic_salary = Column(Decimal(15, 2), nullable=False)
    hra = Column(Decimal(15, 2), default=0)
    transport_allowance = Column(Decimal(15, 2), default=0)
    medical_allowance = Column(Decimal(15, 2), default=0)
    special_allowance = Column(Decimal(15, 2), default=0)
    
    # Variable components
    performance_bonus = Column(Decimal(15, 2), default=0)
    annual_bonus = Column(Decimal(15, 2), default=0)
    
    # Deduction components
    pf_employee = Column(Decimal(15, 2), default=0)
    pf_employer = Column(Decimal(15, 2), default=0)
    esi_employee = Column(Decimal(15, 2), default=0)
    esi_employer = Column(Decimal(15, 2), default=0)
    professional_tax = Column(Decimal(15, 2), default=0)
    
    # Calculated fields
    gross_salary = Column(Decimal(15, 2))
    total_deductions = Column(Decimal(15, 2))
    net_salary = Column(Decimal(15, 2))
    ctc = Column(Decimal(15, 2))  # Cost to Company
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company")
    employee = relationship("Employee")
    creator = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_salary_struct_emp_date', 'employee_id', 'effective_from'),
        Index('idx_salary_struct_company', 'company_id', 'is_active'),
    )


class PayslipTemplate(Base):
    __tablename__ = "payslip_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    template_name = Column(String(100), nullable=False)
    template_html = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company")
    creator = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_payslip_template_company', 'company_id', 'is_active'),
    )
