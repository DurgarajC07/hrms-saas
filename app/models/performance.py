from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Index, Date, Text
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PerformanceReviewType(str, enum.Enum):
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    PROBATION = "probation"
    PROJECT_BASED = "project_based"


class ReviewStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    SELF_ASSESSMENT_PENDING = "self_assessment_pending"
    MANAGER_REVIEW_PENDING = "manager_review_pending"
    HR_REVIEW_PENDING = "hr_review_pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GoalStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    PARTIALLY_ACHIEVED = "partially_achieved"
    NOT_ACHIEVED = "not_achieved"
    CANCELLED = "cancelled"


class Performance(Base):
    __tablename__ = "performances"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Review details
    review_type = Column(Enum(PerformanceReviewType), nullable=False)
    review_period_start = Column(Date, nullable=False)
    review_period_end = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    
    # Status and progress
    status = Column(Enum(ReviewStatus), default=ReviewStatus.DRAFT)
    completion_percentage = Column(Integer, default=0)
    
    # Ratings (1-5 scale)
    overall_rating = Column(Numeric(3, 2))
    technical_skills_rating = Column(Numeric(3, 2))
    communication_rating = Column(Numeric(3, 2))
    teamwork_rating = Column(Numeric(3, 2))
    leadership_rating = Column(Numeric(3, 2))
    initiative_rating = Column(Numeric(3, 2))
    
    # Comments and feedback
    employee_comments = Column(Text)
    manager_comments = Column(Text)
    hr_comments = Column(Text)
    strengths = Column(Text)
    areas_for_improvement = Column(Text)
    development_plan = Column(Text)
    
    # Self assessment
    self_assessment_completed = Column(Boolean, default=False)
    self_assessment_date = Column(DateTime(timezone=True))
    self_rating = Column(Numeric(3, 2))
    achievements = Column(Text)
    challenges_faced = Column(Text)
    
    # Manager review
    manager_review_completed = Column(Boolean, default=False)
    manager_review_date = Column(DateTime(timezone=True))
    recommended_rating = Column(Numeric(3, 2))
    promotion_recommendation = Column(Boolean, default=False)
    salary_increase_recommendation = Column(Numeric(5, 2))  # percentage
    
    # Final review
    final_review_completed = Column(Boolean, default=False)
    final_review_date = Column(DateTime(timezone=True))
    final_reviewer_id = Column(Integer, ForeignKey("users.id"))
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="performances")
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])
    final_reviewer = relationship("User", foreign_keys=[final_reviewer_id])
    creator = relationship("User", foreign_keys=[created_by])
    goals = relationship("PerformanceGoal", back_populates="performance")
    
    # Indexes
    __table_args__ = (
        Index('idx_perf_emp_period', 'employee_id', 'review_period_start', 'review_period_end'),
        Index('idx_perf_status_due', 'status', 'due_date'),
        Index('idx_perf_company', 'company_id', 'status'),
    )


class PerformanceGoal(Base):
    __tablename__ = "performance_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    performance_id = Column(Integer, ForeignKey("performances.id"), nullable=False)
    
    # Goal details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100))  # technical, behavioral, business
    weight = Column(Integer, default=20)  # percentage weight in overall review
    
    # Target and measurement
    target_value = Column(String(200))
    measurement_criteria = Column(Text)
    target_date = Column(Date)
    
    # Progress tracking
    status = Column(Enum(GoalStatus), default=GoalStatus.NOT_STARTED)
    progress_percentage = Column(Integer, default=0)
    achievement_rating = Column(Numeric(3, 2))
    actual_achievement = Column(Text)
    
    # Comments
    employee_comments = Column(Text)
    manager_comments = Column(Text)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    performance = relationship("Performance", back_populates="goals")
    
    # Indexes
    __table_args__ = (
        Index('idx_goal_performance', 'performance_id', 'status'),
        Index('idx_goal_target_date', 'target_date'),
    )


class PerformanceTemplate(Base):
    __tablename__ = "performance_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Template details
    template_name = Column(String(200), nullable=False)
    review_type = Column(Enum(PerformanceReviewType), nullable=False)
    description = Column(Text)
    
    # Template configuration
    template_structure = Column(Text, nullable=False)  # JSON structure
    rating_scale = Column(String(50), default="1-5")
    competencies = Column(Text)  # JSON array of competencies
    
    # Applicable to
    applicable_to_all = Column(Boolean, default=True)
    applicable_departments = Column(Text)  # JSON array
    applicable_job_levels = Column(Text)  # JSON array
    
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
    
    # Indexes
    __table_args__ = (
        Index('idx_perf_template_company', 'company_id', 'is_active'),
        Index('idx_perf_template_type', 'review_type', 'is_active'),
    )


class Performance360Feedback(Base):
    __tablename__ = "performance_360_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    performance_id = Column(Integer, ForeignKey("performances.id"), nullable=False)
    feedback_provider_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Feedback details
    feedback_type = Column(String(50), nullable=False)  # peer, subordinate, customer, manager
    overall_rating = Column(Numeric(3, 2))
    technical_rating = Column(Numeric(3, 2))
    communication_rating = Column(Numeric(3, 2))
    teamwork_rating = Column(Numeric(3, 2))
    leadership_rating = Column(Numeric(3, 2))
    
    # Comments
    strengths = Column(Text)
    areas_for_improvement = Column(Text)
    additional_comments = Column(Text)
    
    # Anonymous feedback option
    is_anonymous = Column(Boolean, default=False)
    
    # System fields
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    performance = relationship("Performance")
    feedback_provider = relationship("Employee")
    
    # Indexes
    __table_args__ = (
        Index('idx_360_feedback_performance', 'performance_id', 'feedback_type'),
        Index('idx_360_feedback_provider', 'feedback_provider_id'),
    )


class PerformanceCompetency(Base):
    __tablename__ = "performance_competencies"
    
    id = Column(Integer, primary_key=True, index=True)
    performance_id = Column(Integer, ForeignKey("performances.id"), nullable=False)
    
    # Competency details
    competency_name = Column(String(200), nullable=False)
    competency_category = Column(String(100))  # technical, behavioral, business
    description = Column(Text)
    weight = Column(Integer, default=20)  # percentage weight
    
    # Ratings from different sources
    self_rating = Column(Numeric(3, 2))
    manager_rating = Column(Numeric(3, 2))
    peer_rating = Column(Numeric(3, 2))
    final_rating = Column(Numeric(3, 2))
    
    # Comments
    self_comments = Column(Text)
    manager_comments = Column(Text)
    development_notes = Column(Text)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    performance = relationship("Performance")
    
    # Indexes
    __table_args__ = (
        Index('idx_competency_performance', 'performance_id'),
        Index('idx_competency_category', 'competency_category'),
    )


class DevelopmentPlan(Base):
    __tablename__ = "development_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    performance_id = Column(Integer, ForeignKey("performances.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Plan details
    plan_name = Column(String(200), nullable=False)
    description = Column(Text)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Career progression
    current_level = Column(String(100))
    target_level = Column(String(100))
    career_path = Column(Text)
    
    # Development activities
    training_programs = Column(Text)  # JSON array
    mentoring_assignments = Column(Text)  # JSON array
    stretch_assignments = Column(Text)  # JSON array
    skill_requirements = Column(Text)  # JSON array
    
    # Progress tracking
    completion_percentage = Column(Integer, default=0)
    status = Column(String(50), default="active")  # active, completed, cancelled
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    performance = relationship("Performance")
    employee = relationship("Employee")
    creator = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_dev_plan_employee', 'employee_id', 'status'),
        Index('idx_dev_plan_performance', 'performance_id'),
    )


class CalibrationSession(Base):
    __tablename__ = "calibration_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Session details
    session_name = Column(String(200), nullable=False)
    description = Column(Text)
    session_date = Column(DateTime(timezone=True), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    # Participants
    facilitator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    participants = Column(Text)  # JSON array of user IDs
    
    # Reviews being calibrated
    review_ids = Column(Text)  # JSON array of performance review IDs
    
    # Session outcomes
    calibration_notes = Column(Text)
    rating_adjustments = Column(Text)  # JSON array of adjustments made
    consensus_reached = Column(Boolean, default=False)
    
    # Status
    status = Column(String(50), default="scheduled")  # scheduled, in_progress, completed, cancelled
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company")
    facilitator = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_calibration_company', 'company_id', 'status'),
        Index('idx_calibration_date', 'session_date'),
    )


class SuccessionPlan(Base):
    __tablename__ = "succession_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Position details
    position_title = Column(String(200), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    current_incumbent_id = Column(Integer, ForeignKey("employees.id"))
    
    # Succession details
    criticality_level = Column(String(50))  # high, medium, low
    risk_of_departure = Column(String(50))  # high, medium, low
    
    # Successors
    ready_now_successor_id = Column(Integer, ForeignKey("employees.id"))
    ready_1year_successor_id = Column(Integer, ForeignKey("employees.id"))
    ready_2year_successor_id = Column(Integer, ForeignKey("employees.id"))
    
    # Development needs
    key_competencies = Column(Text)  # JSON array
    development_actions = Column(Text)  # JSON array
    
    # Review information
    last_review_date = Column(Date)
    next_review_date = Column(Date)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company")
    current_incumbent = relationship("Employee", foreign_keys=[current_incumbent_id])
    ready_now_successor = relationship("Employee", foreign_keys=[ready_now_successor_id])
    ready_1year_successor = relationship("Employee", foreign_keys=[ready_1year_successor_id])
    ready_2year_successor = relationship("Employee", foreign_keys=[ready_2year_successor_id])
    creator = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_succession_company', 'company_id'),
        Index('idx_succession_position', 'position_title'),
    )


class PerformanceReviewReminder(Base):
    __tablename__ = "performance_review_reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    performance_id = Column(Integer, ForeignKey("performances.id"), nullable=False)
    
    # Reminder details
    reminder_type = Column(String(100), nullable=False)  # due_soon, overdue, self_assessment, manager_review
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timing
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    sent_date = Column(DateTime(timezone=True))
    
    # Content
    subject = Column(String(500))
    message = Column(Text)
    
    # Status
    status = Column(String(50), default="scheduled")  # scheduled, sent, failed
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    performance = relationship("Performance")
    recipient = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_reminder_scheduled', 'scheduled_date', 'status'),
        Index('idx_reminder_performance', 'performance_id'),
    )
