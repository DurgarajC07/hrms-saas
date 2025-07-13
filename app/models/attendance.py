from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Index, Date, Time, Decimal
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    ON_LEAVE = "on_leave"
    HOLIDAY = "holiday"
    WEEKEND = "weekend"


class PunchType(str, enum.Enum):
    PUNCH_IN = "punch_in"
    PUNCH_OUT = "punch_out"
    BREAK_START = "break_start"
    BREAK_END = "break_end"


class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    
    # Time tracking
    punch_in_time = Column(DateTime(timezone=True))
    punch_out_time = Column(DateTime(timezone=True))
    break_duration = Column(Integer, default=0)  # minutes
    total_hours = Column(Decimal(5, 2))
    overtime_hours = Column(Decimal(5, 2), default=0)
    
    # Location tracking
    punch_in_latitude = Column(Decimal(10, 8))
    punch_in_longitude = Column(Decimal(11, 8))
    punch_out_latitude = Column(Decimal(10, 8))
    punch_out_longitude = Column(Decimal(11, 8))
    punch_in_address = Column(String(500))
    punch_out_address = Column(String(500))
    
    # Status and validation
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    is_late = Column(Boolean, default=False)
    late_minutes = Column(Integer, default=0)
    early_departure = Column(Boolean, default=False)
    early_departure_minutes = Column(Integer, default=0)
    
    # Manual adjustments
    manual_punch_in = Column(DateTime(timezone=True))
    manual_punch_out = Column(DateTime(timezone=True))
    adjusted_by = Column(Integer, ForeignKey("users.id"))
    adjustment_reason = Column(String(500))
    adjustment_date = Column(DateTime(timezone=True))
    
    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    approval_comments = Column(String(500))
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="attendances")
    adjuster = relationship("User", foreign_keys=[adjusted_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_att_emp_date', 'employee_id', 'date', unique=True),
        Index('idx_att_company_date', 'company_id', 'date'),
        Index('idx_att_status_date', 'status', 'date'),
        Index('idx_att_approval', 'requires_approval', 'approved_by'),
    )


class AttendancePunch(Base):
    """Detailed punch records for audit trail"""
    __tablename__ = "attendance_punches"
    
    id = Column(Integer, primary_key=True, index=True)
    attendance_id = Column(Integer, ForeignKey("attendances.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    punch_type = Column(Enum(PunchType), nullable=False)
    punch_time = Column(DateTime(timezone=True), nullable=False)
    
    # Location data
    latitude = Column(Decimal(10, 8))
    longitude = Column(Decimal(11, 8))
    address = Column(String(500))
    device_info = Column(String(255))  # Device/browser info
    ip_address = Column(String(45))
    
    # Validation
    is_valid_location = Column(Boolean, default=True)
    distance_from_office = Column(Integer)  # meters
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    attendance = relationship("Attendance")
    employee = relationship("Employee")
    
    # Indexes
    __table_args__ = (
        Index('idx_punch_emp_time', 'employee_id', 'punch_time'),
        Index('idx_punch_type_date', 'punch_type', 'punch_time'),
    )


class Shift(Base):
    __tablename__ = "shifts"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)
    
    # Shift timings
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    break_duration = Column(Integer, default=60)  # minutes
    
    # Grace periods
    late_grace_period = Column(Integer, default=10)  # minutes
    early_departure_grace = Column(Integer, default=10)  # minutes
    
    # Overtime settings
    overtime_threshold = Column(Integer, default=480)  # minutes (8 hours)
    overtime_multiplier = Column(Decimal(3, 2), default=1.5)
    
    # Weekly settings
    working_days = Column(String(20), default="1,2,3,4,5")  # Comma-separated day numbers
    weekly_hours = Column(Decimal(5, 2), default=40)
    
    # Validations
    is_night_shift = Column(Boolean, default=False)
    is_flexible = Column(Boolean, default=False)
    min_hours_per_day = Column(Decimal(4, 2), default=8)
    max_hours_per_day = Column(Decimal(4, 2), default=12)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="shifts")
    employees = relationship("Employee")
    
    # Indexes
    __table_args__ = (
        Index('idx_shift_company_code', 'company_id', 'code', unique=True),
        Index('idx_shift_company_active', 'company_id', 'is_active'),
    )


class Holiday(Base):
    __tablename__ = "holidays"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String(500))
    is_mandatory = Column(Boolean, default=True)
    is_recurring = Column(Boolean, default=False)  # Annual recurring
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company")
    
    # Indexes
    __table_args__ = (
        Index('idx_holiday_company_date', 'company_id', 'date'),
        Index('idx_holiday_date', 'date'),
    )
