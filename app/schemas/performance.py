"""
Performance management schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date, datetime
from enum import Enum


class PerformanceReviewType(str, Enum):
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    PROBATION = "probation"
    PROJECT_BASED = "project_based"


class ReviewStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    SELF_ASSESSMENT_PENDING = "self_assessment_pending"
    MANAGER_REVIEW_PENDING = "manager_review_pending"
    HR_REVIEW_PENDING = "hr_review_pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GoalStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    PARTIALLY_ACHIEVED = "partially_achieved"
    NOT_ACHIEVED = "not_achieved"
    CANCELLED = "cancelled"


# Performance Goal Schemas
class PerformanceGoalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    category: Optional[str] = Field(None, max_length=100)
    weight: int = Field(20, ge=0, le=100)
    target_value: Optional[str] = Field(None, max_length=200)
    measurement_criteria: Optional[str] = None
    target_date: Optional[date] = None


class PerformanceGoalCreate(PerformanceGoalBase):
    performance_id: int


class PerformanceGoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=100)
    weight: Optional[int] = Field(None, ge=0, le=100)
    target_value: Optional[str] = Field(None, max_length=200)
    measurement_criteria: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[GoalStatus] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    achievement_rating: Optional[float] = Field(None, ge=0, le=5)
    actual_achievement: Optional[str] = None
    employee_comments: Optional[str] = None
    manager_comments: Optional[str] = None


class PerformanceGoal(PerformanceGoalBase):
    id: int
    performance_id: int
    status: GoalStatus
    progress_percentage: int
    achievement_rating: Optional[float]
    actual_achievement: Optional[str]
    employee_comments: Optional[str]
    manager_comments: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Performance Review Schemas
class PerformanceBase(BaseModel):
    employee_id: int
    reviewer_id: int
    review_type: PerformanceReviewType
    review_period_start: date
    review_period_end: date
    due_date: date


class PerformanceCreate(PerformanceBase):
    company_id: int


class PerformanceUpdate(BaseModel):
    reviewer_id: Optional[int] = None
    review_type: Optional[PerformanceReviewType] = None
    review_period_start: Optional[date] = None
    review_period_end: Optional[date] = None
    due_date: Optional[date] = None
    status: Optional[ReviewStatus] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    
    # Ratings
    overall_rating: Optional[float] = Field(None, ge=0, le=5)
    technical_skills_rating: Optional[float] = Field(None, ge=0, le=5)
    communication_rating: Optional[float] = Field(None, ge=0, le=5)
    teamwork_rating: Optional[float] = Field(None, ge=0, le=5)
    leadership_rating: Optional[float] = Field(None, ge=0, le=5)
    initiative_rating: Optional[float] = Field(None, ge=0, le=5)
    
    # Comments
    employee_comments: Optional[str] = None
    manager_comments: Optional[str] = None
    hr_comments: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    development_plan: Optional[str] = None
    
    # Self assessment
    self_assessment_completed: Optional[bool] = None
    self_rating: Optional[float] = Field(None, ge=0, le=5)
    achievements: Optional[str] = None
    challenges_faced: Optional[str] = None
    
    # Manager review
    manager_review_completed: Optional[bool] = None
    recommended_rating: Optional[float] = Field(None, ge=0, le=5)
    promotion_recommendation: Optional[bool] = None
    salary_increase_recommendation: Optional[float] = Field(None, ge=0, le=100)
    
    # Final review
    final_review_completed: Optional[bool] = None
    final_reviewed_by: Optional[int] = None


class Performance(PerformanceBase):
    id: int
    company_id: int
    status: ReviewStatus
    completion_percentage: int
    
    # Ratings
    overall_rating: Optional[float]
    technical_skills_rating: Optional[float]
    communication_rating: Optional[float]
    teamwork_rating: Optional[float]
    leadership_rating: Optional[float]
    initiative_rating: Optional[float]
    
    # Comments
    employee_comments: Optional[str]
    manager_comments: Optional[str]
    hr_comments: Optional[str]
    strengths: Optional[str]
    areas_for_improvement: Optional[str]
    development_plan: Optional[str]
    
    # Self assessment
    self_assessment_completed: bool
    self_assessment_date: Optional[datetime]
    self_rating: Optional[float]
    achievements: Optional[str]
    challenges_faced: Optional[str]
    
    # Manager review
    manager_review_completed: bool
    manager_review_date: Optional[datetime]
    recommended_rating: Optional[float]
    promotion_recommendation: bool
    salary_increase_recommendation: Optional[float]
    
    # Final review
    final_review_completed: bool
    final_review_date: Optional[datetime]
    final_reviewed_by: Optional[int]
    
    # System fields
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]
    
    # Related data
    goals: List[PerformanceGoal] = []

    class Config:
        from_attributes = True


# Performance Template Schemas
class PerformanceTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    review_type: PerformanceReviewType
    is_active: bool = True


class PerformanceTemplateCreate(PerformanceTemplateBase):
    company_id: int


class PerformanceTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    review_type: Optional[PerformanceReviewType] = None
    is_active: Optional[bool] = None


class PerformanceTemplate(PerformanceTemplateBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]

    class Config:
        from_attributes = True


# Response Schemas
class PerformanceResponse(Performance):
    """Performance response with all fields"""
    pass


class PerformanceGoalResponse(PerformanceGoal):
    """Performance goal response with all fields"""
    pass


class PerformanceTemplateResponse(PerformanceTemplate):
    """Performance template response with all fields"""
    pass


# Performance List Response
class PerformanceListResponse(BaseModel):
    items: List[Performance]
    total: int
    page: int
    per_page: int
    pages: int


class PerformanceGoalListResponse(BaseModel):
    items: List[PerformanceGoal]
    total: int
    page: int
    per_page: int
    pages: int


# Advanced Performance Management Schemas

class Performance360FeedbackBase(BaseModel):
    performance_id: int
    feedback_type: str = Field(..., pattern="^(peer|subordinate|customer|manager)$")
    is_anonymous: bool = False
    
    # Ratings
    overall_rating: Optional[float] = Field(None, ge=0, le=5)
    technical_rating: Optional[float] = Field(None, ge=0, le=5)
    communication_rating: Optional[float] = Field(None, ge=0, le=5)
    teamwork_rating: Optional[float] = Field(None, ge=0, le=5)
    leadership_rating: Optional[float] = Field(None, ge=0, le=5)
    
    # Comments
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    additional_comments: Optional[str] = None


class Performance360FeedbackCreate(Performance360FeedbackBase):
    feedback_provider_id: Optional[int] = None  # Optional for anonymous feedback


class Performance360Feedback(Performance360FeedbackBase):
    id: int
    feedback_provider_id: Optional[int]
    submitted_at: datetime

    class Config:
        from_attributes = True


class PerformanceCompetencyBase(BaseModel):
    competency_name: str = Field(..., min_length=1, max_length=200)
    competency_category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    weight: int = Field(20, ge=0, le=100)


class PerformanceCompetencyCreate(PerformanceCompetencyBase):
    performance_id: int


class PerformanceCompetencyUpdate(BaseModel):
    self_rating: Optional[float] = Field(None, ge=0, le=5)
    manager_rating: Optional[float] = Field(None, ge=0, le=5)
    peer_rating: Optional[float] = Field(None, ge=0, le=5)
    final_rating: Optional[float] = Field(None, ge=0, le=5)
    self_comments: Optional[str] = None
    manager_comments: Optional[str] = None
    development_notes: Optional[str] = None


class PerformanceCompetency(PerformanceCompetencyBase):
    id: int
    performance_id: int
    self_rating: Optional[float]
    manager_rating: Optional[float]
    peer_rating: Optional[float]
    final_rating: Optional[float]
    self_comments: Optional[str]
    manager_comments: Optional[str]
    development_notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DevelopmentPlanBase(BaseModel):
    plan_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: date
    end_date: date
    current_level: Optional[str] = Field(None, max_length=100)
    target_level: Optional[str] = Field(None, max_length=100)
    career_path: Optional[str] = None


class DevelopmentPlanCreate(DevelopmentPlanBase):
    performance_id: int
    employee_id: int
    training_programs: Optional[List[str]] = []
    mentoring_assignments: Optional[List[str]] = []
    stretch_assignments: Optional[List[str]] = []
    skill_requirements: Optional[List[str]] = []


class DevelopmentPlanUpdate(BaseModel):
    plan_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    end_date: Optional[date] = None
    target_level: Optional[str] = Field(None, max_length=100)
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[str] = Field(None, pattern="^(active|completed|cancelled)$")


class DevelopmentPlan(DevelopmentPlanBase):
    id: int
    performance_id: int
    employee_id: int
    training_programs: List[str]
    mentoring_assignments: List[str]
    stretch_assignments: List[str]
    skill_requirements: List[str]
    completion_percentage: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]

    class Config:
        from_attributes = True


class CalibrationSessionBase(BaseModel):
    session_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    session_date: datetime
    department_id: Optional[int] = None


class CalibrationSessionCreate(CalibrationSessionBase):
    facilitator_id: int
    participants: List[int] = []
    review_ids: List[int] = []


class CalibrationSessionUpdate(BaseModel):
    session_date: Optional[datetime] = None
    participants: Optional[List[int]] = None
    review_ids: Optional[List[int]] = None
    calibration_notes: Optional[str] = None
    consensus_reached: Optional[bool] = None
    status: Optional[str] = Field(None, pattern="^(scheduled|in_progress|completed|cancelled)$")


class CalibrationSession(CalibrationSessionBase):
    id: int
    company_id: int
    facilitator_id: int
    participants: List[int]
    review_ids: List[int]
    calibration_notes: Optional[str]
    rating_adjustments: Optional[List[dict]]
    consensus_reached: bool
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SuccessionPlanBase(BaseModel):
    position_title: str = Field(..., min_length=1, max_length=200)
    department_id: Optional[int] = None
    current_incumbent_id: Optional[int] = None
    criticality_level: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    risk_of_departure: Optional[str] = Field(None, pattern="^(high|medium|low)$")


class SuccessionPlanCreate(SuccessionPlanBase):
    ready_now_successor_id: Optional[int] = None
    ready_1year_successor_id: Optional[int] = None
    ready_2year_successor_id: Optional[int] = None
    key_competencies: Optional[List[str]] = []
    development_actions: Optional[List[str]] = []


class SuccessionPlanUpdate(BaseModel):
    current_incumbent_id: Optional[int] = None
    ready_now_successor_id: Optional[int] = None
    ready_1year_successor_id: Optional[int] = None
    ready_2year_successor_id: Optional[int] = None
    criticality_level: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    risk_of_departure: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    key_competencies: Optional[List[str]] = None
    development_actions: Optional[List[str]] = None
    next_review_date: Optional[date] = None


class SuccessionPlan(SuccessionPlanBase):
    id: int
    company_id: int
    ready_now_successor_id: Optional[int]
    ready_1year_successor_id: Optional[int]
    ready_2year_successor_id: Optional[int]
    key_competencies: List[str]
    development_actions: List[str]
    last_review_date: Optional[date]
    next_review_date: Optional[date]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]

    class Config:
        from_attributes = True


class PerformanceReminderBase(BaseModel):
    reminder_type: str = Field(..., pattern="^(due_soon|overdue|self_assessment|manager_review)$")
    scheduled_date: datetime
    subject: Optional[str] = Field(None, max_length=500)
    message: Optional[str] = None


class PerformanceReminderCreate(PerformanceReminderBase):
    performance_id: int
    recipient_id: int


class PerformanceReminder(PerformanceReminderBase):
    id: int
    performance_id: int
    recipient_id: int
    sent_date: Optional[datetime]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Extended Performance Response with Advanced Features
class PerformanceResponseAdvanced(PerformanceResponse):
    """Extended performance response with advanced features"""
    feedback_360: List[Performance360Feedback] = []
    competencies: List[PerformanceCompetency] = []
    development_plan: Optional[DevelopmentPlan] = None


# Analytics and Reporting Schemas
class PerformanceAnalytics(BaseModel):
    total_reviews: int
    completed_reviews: int
    completion_rate: float
    average_rating: float
    status_distribution: Dict[str, int]
    rating_distribution: Dict[str, int]
    trends: Optional[Dict[str, List[float]]] = None


class TalentMatrixData(BaseModel):
    employee_id: int
    employee_name: str
    performance_score: float
    potential_score: float
    box_category: str  # star, core_player, high_potential, etc.
    current_role: str
    recommended_actions: List[str]


class CalibrationAnalytics(BaseModel):
    rating_distribution: Dict[str, int]
    department_averages: Dict[str, float]
    outliers: List[dict]
    recommendations: List[str]
    forced_ranking_compliance: float


class SuccessionReadiness(BaseModel):
    position: str
    current_incumbent: str
    successor_pipeline: List[dict]
    risk_level: str
    development_gap_months: int
    action_items: List[str]
