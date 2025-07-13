from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Index, Date, Decimal, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DocumentType(str, enum.Enum):
    CONTRACT = "contract"
    POLICY = "policy"
    HANDBOOK = "handbook"
    FORM = "form"
    CERTIFICATE = "certificate"
    ID_DOCUMENT = "id_document"
    RESUME = "resume"
    OFFER_LETTER = "offer_letter"
    PERFORMANCE_REVIEW = "performance_review"
    DISCIPLINARY_ACTION = "disciplinary_action"
    TRAINING_CERTIFICATE = "training_certificate"
    MEDICAL_RECORD = "medical_record"
    TAX_DOCUMENT = "tax_document"
    BANK_DETAIL = "bank_detail"
    EMERGENCY_CONTACT = "emergency_contact"
    REFERENCE = "reference"
    BACKGROUND_CHECK = "background_check"
    CONFIDENTIALITY_AGREEMENT = "confidentiality_agreement"
    NON_COMPETE = "non_compete"
    TERMINATION_LETTER = "termination_letter"


class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    EXPIRED = "expired"
    ARCHIVED = "archived"
    REQUIRES_SIGNATURE = "requires_signature"
    SIGNED = "signed"


class DocumentCategory(str, enum.Enum):
    PERSONAL = "personal"
    EMPLOYMENT = "employment"
    COMPLIANCE = "compliance"
    TRAINING = "training"
    BENEFITS = "benefits"
    PAYROLL = "payroll"
    PERFORMANCE = "performance"
    LEGAL = "legal"
    COMPANY_POLICY = "company_policy"
    ONBOARDING = "onboarding"
    OFFBOARDING = "offboarding"


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"))  # Nullable for company-wide documents
    
    # Document details
    document_name = Column(String(300), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    category = Column(Enum(DocumentCategory), nullable=False)
    description = Column(Text)
    
    # File information
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)  # in bytes
    file_type = Column(String(100))  # MIME type
    file_hash = Column(String(64))  # SHA-256 hash for integrity
    
    # Document metadata
    document_number = Column(String(100))
    version = Column(String(20), default="1.0")
    issue_date = Column(Date)
    expiry_date = Column(Date)
    issuing_authority = Column(String(200))
    
    # Status and workflow
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    is_confidential = Column(Boolean, default=False)
    is_mandatory = Column(Boolean, default=False)
    requires_acknowledgment = Column(Boolean, default=False)
    requires_signature = Column(Boolean, default=False)
    
    # Access control
    is_public = Column(Boolean, default=False)  # Visible to all employees
    accessible_departments = Column(Text)  # JSON array of department IDs
    accessible_roles = Column(Text)  # JSON array of role names
    
    # Compliance
    retention_period_years = Column(Integer)
    legal_hold = Column(Boolean, default=False)
    compliance_tags = Column(Text)  # JSON array of compliance tags
    
    # Review and approval
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_date = Column(DateTime(timezone=True))
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_date = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    company = relationship("Company")
    employee = relationship("Employee", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    approver = relationship("User", foreign_keys=[approved_by])
    acknowledgments = relationship("DocumentAcknowledgment", back_populates="document")
    signatures = relationship("DocumentSignature", back_populates="document")
    
    # Indexes
    __table_args__ = (
        Index('idx_doc_company_employee', 'company_id', 'employee_id'),
        Index('idx_doc_type_status', 'document_type', 'status'),
        Index('idx_doc_category', 'category', 'status'),
        Index('idx_doc_expiry', 'expiry_date', 'status'),
        Index('idx_doc_mandatory', 'is_mandatory', 'status'),
    )


class DocumentAcknowledgment(Base):
    __tablename__ = "document_acknowledgments"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Acknowledgment details
    acknowledged_date = Column(DateTime(timezone=True), nullable=False)
    acknowledgment_method = Column(String(50))  # email, portal, physical
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Comments
    employee_comments = Column(Text)
    questions_asked = Column(Text)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="acknowledgments")
    employee = relationship("Employee")
    
    # Indexes
    __table_args__ = (
        Index('idx_ack_doc_emp', 'document_id', 'employee_id'),
        Index('idx_ack_employee', 'employee_id', 'acknowledged_date'),
    )


class DocumentSignature(Base):
    __tablename__ = "document_signatures"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    signer_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Signature details
    signature_type = Column(String(50))  # electronic, wet_signature, digital
    signed_date = Column(DateTime(timezone=True), nullable=False)
    signature_image_path = Column(String(500))
    
    # Digital signature verification
    digital_signature_hash = Column(String(256))
    certificate_serial = Column(String(100))
    signing_algorithm = Column(String(50))
    
    # Verification
    ip_address = Column(String(45))
    user_agent = Column(Text)
    verification_status = Column(String(50), default="pending")
    verified_date = Column(DateTime(timezone=True))
    
    # Witness information (if required)
    witness_name = Column(String(200))
    witness_email = Column(String(255))
    witness_signature_path = Column(String(500))
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="signatures")
    signer = relationship("Employee")
    
    # Indexes
    __table_args__ = (
        Index('idx_sig_doc_signer', 'document_id', 'signer_employee_id'),
        Index('idx_sig_verification', 'verification_status', 'signed_date'),
    )


class DocumentTemplate(Base):
    __tablename__ = "document_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Template details
    template_name = Column(String(200), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    category = Column(Enum(DocumentCategory), nullable=False)
    description = Column(Text)
    
    # Template content
    template_content = Column(Text, nullable=False)  # HTML or rich text
    merge_fields = Column(Text)  # JSON array of merge field definitions
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)
    auto_generate = Column(Boolean, default=False)  # Auto-generate for new employees
    
    # Workflow
    approval_workflow = Column(Text)  # JSON definition of approval steps
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company")
    creator = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_template_company', 'company_id', 'is_active'),
        Index('idx_template_type', 'document_type', 'is_active'),
    )


class DocumentFolder(Base):
    __tablename__ = "document_folders"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    parent_folder_id = Column(Integer, ForeignKey("document_folders.id"))
    
    # Folder details
    folder_name = Column(String(200), nullable=False)
    description = Column(Text)
    folder_path = Column(String(1000), nullable=False)
    
    # Access control
    is_public = Column(Boolean, default=False)
    accessible_departments = Column(Text)  # JSON array
    accessible_roles = Column(Text)  # JSON array
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company")
    parent_folder = relationship("DocumentFolder", remote_side=[id])
    creator = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_folder_company', 'company_id'),
        Index('idx_folder_parent', 'parent_folder_id'),
    )
