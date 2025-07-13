from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Index, Date, Text
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class OnboardingStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    OVERDUE = "overdue"


class TaskType(str, enum.Enum):
    DOCUMENT_SUBMISSION = "document_submission"
    DOCUMENT_REVIEW = "document_review"
    FORM_COMPLETION = "form_completion"
    TRAINING_MODULE = "training_module"
    SYSTEM_ACCESS = "system_access"
    EQUIPMENT_ASSIGNMENT = "equipment_assignment"
    ORIENTATION_SESSION = "orientation_session"
    MEETING_SCHEDULING = "meeting_scheduling"
    POLICY_ACKNOWLEDGMENT = "policy_acknowledgment"
    COMPLIANCE_CHECK = "compliance_check"
    BACKGROUND_VERIFICATION = "background_verification"
    MEDICAL_EXAMINATION = "medical_examination"
    OFFICE_TOUR = "office_tour"
    TEAM_INTRODUCTION = "team_introduction"
    GOAL_SETTING = "goal_setting"


class OnboardingChecklist(Base):
    __tablename__ = "onboarding_checklists"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("onboarding_templates.id"), nullable=False)
    
    # Checklist details
    checklist_name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    expected_completion_date = Column(Date, nullable=False)
    actual_completion_date = Column(Date)
    
    # Progress tracking
    status = Column(Enum(OnboardingStatus), default=OnboardingStatus.NOT_STARTED)
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    progress_percentage = Column(Integer, default=0)
    
    # Assignment
    assigned_to_hr = Column(Integer, ForeignKey("employees.id"))
    assigned_to_manager = Column(Integer, ForeignKey("employees.id"))
    assigned_to_buddy = Column(Integer, ForeignKey("employees.id"))
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="onboarding_checklists")
    template = relationship("OnboardingTemplate")
    hr_assignee = relationship("Employee", foreign_keys=[assigned_to_hr])
    manager_assignee = relationship("Employee", foreign_keys=[assigned_to_manager])
    buddy_assignee = relationship("Employee", foreign_keys=[assigned_to_buddy])
    creator = relationship("User")
    tasks = relationship("OnboardingTask", back_populates="checklist")
    
    # Indexes
    __table_args__ = (
        Index('idx_onboard_employee', 'employee_id', 'status'),
        Index('idx_onboard_completion', 'expected_completion_date', 'status'),
        Index('idx_onboard_progress', 'progress_percentage', 'status'),
    )


class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("onboarding_checklists.id"), nullable=False)
    
    # Task details
    task_name = Column(String(200), nullable=False)
    task_description = Column(Text)
    task_type = Column(Enum(TaskType), nullable=False)
    instructions = Column(Text)
    
    # Scheduling
    sequence_order = Column(Integer, nullable=False)
    due_date = Column(Date)
    estimated_duration_hours = Column(Integer)
    is_mandatory = Column(Boolean, default=True)
    
    # Dependencies
    depends_on_task_ids = Column(Text)  # JSON array of task IDs
    blocks_task_ids = Column(Text)  # JSON array of task IDs
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"))
    assigned_to_employee = Column(Boolean, default=True)  # True if employee completes, False if HR/Manager
    
    # Status and completion
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    started_date = Column(DateTime(timezone=True))
    completed_date = Column(DateTime(timezone=True))
    completed_by = Column(Integer, ForeignKey("users.id"))
    
    # Task-specific data
    form_template_id = Column(Integer)  # Reference to form template
    document_template_id = Column(Integer)  # Reference to document template
    training_module_id = Column(Integer)  # Reference to training module
    required_documents = Column(Text)  # JSON array of required documents
    submission_data = Column(Text)  # JSON data submitted by employee
    
    # Verification
    requires_verification = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey("users.id"))
    verified_date = Column(DateTime(timezone=True))
    verification_notes = Column(Text)
    
    # Comments and notes
    employee_notes = Column(Text)
    admin_notes = Column(Text)
    completion_notes = Column(Text)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    checklist = relationship("OnboardingChecklist", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to])
    completer = relationship("User", foreign_keys=[completed_by])
    verifier = relationship("User", foreign_keys=[verified_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_task_checklist', 'checklist_id', 'sequence_order'),
        Index('idx_task_status', 'status', 'due_date'),
        Index('idx_task_assignee', 'assigned_to', 'status'),
    )


class OnboardingTemplate(Base):
    __tablename__ = "onboarding_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Template details
    template_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Applicability
    applicable_departments = Column(Text)  # JSON array of department IDs
    applicable_job_levels = Column(Text)  # JSON array of job levels
    applicable_employee_types = Column(Text)  # JSON array of employee types
    
    # Timeline
    default_duration_days = Column(Integer, default=30)
    pre_start_days = Column(Integer, default=7)  # Tasks before first day
    first_day_tasks = Column(Boolean, default=True)
    first_week_tasks = Column(Boolean, default=True)
    first_month_tasks = Column(Boolean, default=True)
    
    # Configuration
    auto_assign_buddy = Column(Boolean, default=True)
    send_welcome_email = Column(Boolean, default=True)
    notify_manager = Column(Boolean, default=True)
    notify_hr = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company")
    creator = relationship("User")
    template_tasks = relationship("OnboardingTemplateTask", back_populates="template")
    
    # Indexes
    __table_args__ = (
        Index('idx_onboarding_template_company', 'company_id', 'is_active'),
        Index('idx_template_default', 'is_default', 'is_active'),
    )


class OnboardingTemplateTask(Base):
    __tablename__ = "onboarding_template_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("onboarding_templates.id"), nullable=False)
    
    # Task template details
    task_name = Column(String(200), nullable=False)
    task_description = Column(Text)
    task_type = Column(Enum(TaskType), nullable=False)
    instructions = Column(Text)
    
    # Scheduling template
    sequence_order = Column(Integer, nullable=False)
    due_date_offset_days = Column(Integer, default=0)  # Days from start date
    estimated_duration_hours = Column(Integer)
    is_mandatory = Column(Boolean, default=True)
    
    # Assignment template
    default_assignee_role = Column(String(50))  # hr, manager, employee, buddy
    requires_verification = Column(Boolean, default=False)
    verifier_role = Column(String(50))  # hr, manager
    
    # Dependencies
    depends_on_task_orders = Column(Text)  # JSON array of sequence orders
    
    # Task-specific configuration
    form_template_id = Column(Integer)
    document_template_id = Column(Integer)
    training_module_id = Column(Integer)
    required_documents = Column(Text)  # JSON array
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    template = relationship("OnboardingTemplate", back_populates="template_tasks")
    
    # Indexes
    __table_args__ = (
        Index('idx_template_task_order', 'template_id', 'sequence_order'),
        Index('idx_template_task_type', 'task_type'),
    )


class OnboardingProgress(Base):
    __tablename__ = "onboarding_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Overall progress
    onboarding_start_date = Column(Date, nullable=False)
    expected_completion_date = Column(Date, nullable=False)
    actual_completion_date = Column(Date)
    current_phase = Column(String(50))  # pre_start, first_day, first_week, first_month, completed
    
    # Satisfaction and feedback
    employee_satisfaction_rating = Column(Integer)  # 1-5 scale
    employee_feedback = Column(Text)
    manager_feedback = Column(Text)
    hr_feedback = Column(Text)
    buddy_feedback = Column(Text)
    
    # Completion metrics
    tasks_completed_on_time = Column(Integer, default=0)
    tasks_completed_late = Column(Integer, default=0)
    tasks_skipped = Column(Integer, default=0)
    total_time_spent_hours = Column(Numeric(8, 2))
    
    # Exit survey (if applicable)
    exit_survey_completed = Column(Boolean, default=False)
    exit_survey_date = Column(Date)
    exit_reason = Column(Text)
    would_recommend_company = Column(Boolean)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee")
    
    # Indexes
    __table_args__ = (
        Index('idx_progress_employee', 'employee_id'),
        Index('idx_progress_phase', 'current_phase', 'expected_completion_date'),
    )
