from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Index, Date, Decimal, Text
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
    overall_rating = Column(Decimal(3, 2))
    technical_skills_rating = Column(Decimal(3, 2))
    communication_rating = Column(Decimal(3, 2))
    teamwork_rating = Column(Decimal(3, 2))
    leadership_rating = Column(Decimal(3, 2))
    initiative_rating = Column(Decimal(3, 2))
    
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
    self_rating = Column(Decimal(3, 2))
    achievements = Column(Text)
    challenges_faced = Column(Text)
    
    # Manager review
    manager_review_completed = Column(Boolean, default=False)
    manager_review_date = Column(DateTime(timezone=True))
    recommended_rating = Column(Decimal(3, 2))
    promotion_recommendation = Column(Boolean, default=False)
    salary_increase_recommendation = Column(Decimal(5, 2))  # percentage
    
    # Final review
    final_review_completed = Column(Boolean, default=False)
    final_review_date = Column(DateTime(timezone=True))
    final_reviewed_by = Column(Integer, ForeignKey("users.id"))
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="performances")
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])
    final_reviewer = relationship("User")
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
    achievement_rating = Column(Decimal(3, 2))
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
