from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Index, Date, Decimal, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ComplianceType(str, enum.Enum):
    LABOR_LAW = "labor_law"
    TAX_COMPLIANCE = "tax_compliance"
    SAFETY_REGULATION = "safety_regulation"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    DATA_PROTECTION = "data_protection"
    INDUSTRY_SPECIFIC = "industry_specific"
    ENVIRONMENTAL = "environmental"
    FINANCIAL_REGULATION = "financial_regulation"
    HEALTHCARE_REGULATION = "healthcare_regulation"
    INTERNATIONAL_LAW = "international_law"


class ComplianceStatus(str, enum.Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    PENDING_ACTION = "pending_action"
    EXEMPTED = "exempted"


class RequirementStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    SUPERSEDED = "superseded"


class ComplianceRequirement(Base):
    __tablename__ = "compliance_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Requirement details
    requirement_name = Column(String(300), nullable=False)
    requirement_code = Column(String(100), unique=True, nullable=False)
    compliance_type = Column(Enum(ComplianceType), nullable=False)
    description = Column(Text, nullable=False)
    
    # Legal/regulatory information
    regulating_authority = Column(String(200))
    regulation_reference = Column(String(200))
    law_citation = Column(String(500))
    jurisdiction = Column(String(100))  # federal, state, local, international
    
    # Applicability
    applicable_to_all_employees = Column(Boolean, default=True)
    applicable_departments = Column(Text)  # JSON array of department IDs
    applicable_job_levels = Column(Text)  # JSON array of job levels
    applicable_locations = Column(Text)  # JSON array of location IDs
    
    # Timeline and frequency
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    review_frequency_months = Column(Integer)  # How often to review compliance
    next_review_date = Column(Date)
    
    # Compliance criteria
    compliance_criteria = Column(Text, nullable=False)  # JSON array of criteria
    measurement_method = Column(Text)
    acceptable_threshold = Column(String(100))
    
    # Documentation requirements
    required_documents = Column(Text)  # JSON array of document types
    evidence_required = Column(Text)  # JSON array of evidence types
    
    # Risk assessment
    risk_level = Column(String(20), default="medium")  # low, medium, high, critical
    penalty_for_non_compliance = Column(Text)
    
    # Status
    status = Column(Enum(RequirementStatus), default=RequirementStatus.ACTIVE)
    is_mandatory = Column(Boolean, default=True)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company")
    creator = relationship("User")
    assessments = relationship("ComplianceAssessment", back_populates="requirement")
    
    # Indexes
    __table_args__ = (
        Index('idx_req_company_type', 'company_id', 'compliance_type'),
        Index('idx_req_status', 'status', 'effective_date'),
        Index('idx_req_review', 'next_review_date', 'status'),
    )


class ComplianceAssessment(Base):
    __tablename__ = "compliance_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("compliance_requirements.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Assessment details
    assessment_name = Column(String(200), nullable=False)
    assessment_date = Column(Date, nullable=False)
    assessment_period_start = Column(Date, nullable=False)
    assessment_period_end = Column(Date, nullable=False)
    
    # Assessment scope
    scope_description = Column(Text)
    assessed_departments = Column(Text)  # JSON array
    assessed_employees = Column(Text)  # JSON array of employee IDs
    assessed_locations = Column(Text)  # JSON array
    
    # Results
    overall_status = Column(Enum(ComplianceStatus), nullable=False)
    compliance_score = Column(Decimal(5, 2))  # percentage 0-100
    findings = Column(Text)  # JSON array of findings
    non_compliance_issues = Column(Text)  # JSON array of issues
    
    # Evidence and documentation
    evidence_collected = Column(Text)  # JSON array of evidence
    supporting_documents = Column(Text)  # JSON array of document references
    
    # Assessment team
    conducted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    external_auditor = Column(String(200))
    
    # Corrective actions
    corrective_actions_required = Column(Boolean, default=False)
    action_plan = Column(Text)
    target_completion_date = Column(Date)
    actual_completion_date = Column(Date)
    follow_up_required = Column(Boolean, default=False)
    next_assessment_date = Column(Date)
    
    # Risk assessment
    identified_risks = Column(Text)  # JSON array of risks
    risk_mitigation_plan = Column(Text)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    requirement = relationship("ComplianceRequirement", back_populates="assessments")
    company = relationship("Company")
    conductor = relationship("User", foreign_keys=[conducted_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    approver = relationship("User", foreign_keys=[approved_by])
    action_items = relationship("ComplianceActionItem", back_populates="assessment")
    
    # Indexes
    __table_args__ = (
        Index('idx_assess_req_date', 'requirement_id', 'assessment_date'),
        Index('idx_assess_status', 'overall_status', 'assessment_date'),
        Index('idx_assess_follow_up', 'follow_up_required', 'next_assessment_date'),
    )


class ComplianceActionItem(Base):
    __tablename__ = "compliance_action_items"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("compliance_assessments.id"), nullable=False)
    
    # Action item details
    action_title = Column(String(200), nullable=False)
    action_description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_department = Column(String(100))
    responsible_manager = Column(Integer, ForeignKey("users.id"))
    
    # Timeline
    due_date = Column(Date, nullable=False)
    estimated_effort_hours = Column(Integer)
    actual_effort_hours = Column(Integer)
    
    # Status tracking
    status = Column(String(50), default="open")  # open, in_progress, completed, cancelled, overdue
    completion_percentage = Column(Integer, default=0)
    started_date = Column(Date)
    completed_date = Column(Date)
    
    # Progress updates
    progress_notes = Column(Text)
    obstacles_encountered = Column(Text)
    resources_needed = Column(Text)
    
    # Verification
    requires_verification = Column(Boolean, default=True)
    verified_by = Column(Integer, ForeignKey("users.id"))
    verification_date = Column(Date)
    verification_notes = Column(Text)
    
    # Evidence of completion
    completion_evidence = Column(Text)  # JSON array of evidence
    supporting_documents = Column(Text)  # JSON array of document references
    
    # Cost tracking
    estimated_cost = Column(Decimal(10, 2))
    actual_cost = Column(Decimal(10, 2))
    budget_approved = Column(Boolean, default=False)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    assessment = relationship("ComplianceAssessment", back_populates="action_items")
    assignee = relationship("User", foreign_keys=[assigned_to])
    manager = relationship("User", foreign_keys=[responsible_manager])
    verifier = relationship("User", foreign_keys=[verified_by])
    creator = relationship("User", foreign_keys=[created_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_action_assessment', 'assessment_id', 'status'),
        Index('idx_action_assignee', 'assigned_to', 'due_date'),
        Index('idx_action_due_date', 'due_date', 'status'),
    )


class ComplianceTraining(Base):
    __tablename__ = "compliance_training"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    requirement_id = Column(Integer, ForeignKey("compliance_requirements.id"))
    
    # Training details
    training_name = Column(String(200), nullable=False)
    training_description = Column(Text)
    compliance_topics = Column(Text)  # JSON array of topics covered
    
    # Training configuration
    is_mandatory = Column(Boolean, default=True)
    frequency_months = Column(Integer)  # How often retraining is required
    duration_hours = Column(Decimal(4, 2))
    
    # Delivery method
    delivery_method = Column(String(50))  # online, classroom, hybrid, self_study
    training_provider = Column(String(200))
    training_materials = Column(Text)  # JSON array of materials
    
    # Applicability
    applicable_to_all = Column(Boolean, default=True)
    applicable_departments = Column(Text)  # JSON array
    applicable_roles = Column(Text)  # JSON array
    
    # Certification
    provides_certification = Column(Boolean, default=False)
    certificate_valid_months = Column(Integer)
    requires_exam = Column(Boolean, default=False)
    passing_score = Column(Integer)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company")
    requirement = relationship("ComplianceRequirement")
    creator = relationship("User")
    enrollments = relationship("ComplianceTrainingEnrollment", back_populates="training")
    
    # Indexes
    __table_args__ = (
        Index('idx_training_company', 'company_id', 'is_active'),
        Index('idx_training_mandatory', 'is_mandatory', 'is_active'),
    )


class ComplianceTrainingEnrollment(Base):
    __tablename__ = "compliance_training_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    training_id = Column(Integer, ForeignKey("compliance_training.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Enrollment details
    enrollment_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    completion_deadline = Column(Date)
    
    # Progress tracking
    status = Column(String(50), default="enrolled")  # enrolled, in_progress, completed, failed, overdue
    start_date = Column(Date)
    completion_date = Column(Date)
    progress_percentage = Column(Integer, default=0)
    
    # Assessment results
    exam_score = Column(Integer)
    passing_status = Column(Boolean)
    attempts_count = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    # Certification
    certificate_issued = Column(Boolean, default=False)
    certificate_number = Column(String(100))
    certificate_issue_date = Column(Date)
    certificate_expiry_date = Column(Date)
    
    # Tracking
    time_spent_hours = Column(Decimal(6, 2))
    modules_completed = Column(Text)  # JSON array of completed modules
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    training = relationship("ComplianceTraining", back_populates="enrollments")
    employee = relationship("Employee")
    
    # Indexes
    __table_args__ = (
        Index('idx_enrollment_training_emp', 'training_id', 'employee_id'),
        Index('idx_enrollment_due_date', 'due_date', 'status'),
        Index('idx_enrollment_cert_expiry', 'certificate_expiry_date', 'certificate_issued'),
    )
