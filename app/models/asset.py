from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Index, Date, Decimal, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AssetType(str, enum.Enum):
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    MONITOR = "monitor"
    PRINTER = "printer"
    PHONE = "phone"
    VEHICLE = "vehicle"
    FURNITURE = "furniture"
    SOFTWARE_LICENSE = "software_license"
    OTHER = "other"


class AssetStatus(str, enum.Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    IN_REPAIR = "in_repair"
    RETIRED = "retired"
    LOST = "lost"
    STOLEN = "stolen"


class AssetCondition(str, enum.Enum):
    NEW = "new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    DAMAGED = "damaged"


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Asset identification
    asset_tag = Column(String(100), nullable=False, unique=True)
    serial_number = Column(String(100))
    asset_type = Column(Enum(AssetType), nullable=False)
    brand = Column(String(100))
    model = Column(String(100))
    
    # Asset details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    specifications = Column(Text)  # JSON for detailed specs
    
    # Financial information
    purchase_date = Column(Date)
    purchase_cost = Column(Decimal(15, 2))
    current_value = Column(Decimal(15, 2))
    depreciation_rate = Column(Decimal(5, 2))  # Percentage per year
    warranty_expiry = Column(Date)
    
    # Location and status
    location = Column(String(200))
    status = Column(Enum(AssetStatus), default=AssetStatus.AVAILABLE)
    condition = Column(Enum(AssetCondition), default=AssetCondition.NEW)
    
    # Vendor information
    vendor_name = Column(String(200))
    vendor_contact = Column(String(100))
    invoice_number = Column(String(100))
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company")
    creator = relationship("User")
    assignments = relationship("AssetAssignment", back_populates="asset")
    maintenance_records = relationship("AssetMaintenance", back_populates="asset")
    
    # Indexes
    __table_args__ = (
        Index('idx_asset_company_tag', 'company_id', 'asset_tag', unique=True),
        Index('idx_asset_type_status', 'asset_type', 'status'),
        Index('idx_asset_warranty', 'warranty_expiry'),
    )


class AssetAssignment(Base):
    __tablename__ = "asset_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Assignment details
    assigned_date = Column(Date, nullable=False)
    return_date = Column(Date)
    expected_return_date = Column(Date)
    assignment_reason = Column(String(500))
    return_reason = Column(String(500))
    
    # Condition tracking
    condition_at_assignment = Column(Enum(AssetCondition))
    condition_at_return = Column(Enum(AssetCondition))
    notes = Column(Text)
    
    # Approval
    assigned_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    asset = relationship("Asset", back_populates="assignments")
    employee = relationship("Employee", back_populates="assets")
    assigner = relationship("User", foreign_keys=[assigned_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_asset_assignment_active', 'asset_id', 'is_active'),
        Index('idx_asset_assignment_emp', 'employee_id', 'is_active'),
        Index('idx_asset_assignment_dates', 'assigned_date', 'return_date'),
    )


class AssetMaintenance(Base):
    __tablename__ = "asset_maintenance"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    # Maintenance details
    maintenance_type = Column(String(100), nullable=False)  # repair, upgrade, inspection
    description = Column(Text, nullable=False)
    cost = Column(Decimal(10, 2))
    maintenance_date = Column(Date, nullable=False)
    
    # Service provider
    service_provider = Column(String(200))
    technician_name = Column(String(100))
    service_ticket = Column(String(100))
    
    # Status
    is_warranty_covered = Column(Boolean, default=False)
    next_maintenance_date = Column(Date)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    asset = relationship("Asset", back_populates="maintenance_records")
    creator = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_asset_maintenance_asset', 'asset_id', 'maintenance_date'),
        Index('idx_asset_maintenance_next', 'next_maintenance_date'),
    )
