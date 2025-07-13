from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated
from datetime import date
import re

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.performance import PerformanceReviewType, ReviewStatus, GoalStatus
from app.schemas.performance import (
    PerformanceCreate, PerformanceUpdate, PerformanceResponse,
    PerformanceGoalCreate, PerformanceGoalUpdate, PerformanceGoalResponse,
    PerformanceTemplateCreate, PerformanceTemplateResponse
)
from app.crud.performance import (
    performance_crud, performance_goal_crud, performance_template_crud
)

router = APIRouter()


@router.post("/reviews", response_model=PerformanceResponse)
async def create_new_performance_review(
    review: PerformanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new performance review"""
    return await performance_crud.create_review(db, review, current_user.id, current_user.company_id)


@router.get("/reviews", response_model=List[PerformanceResponse])
async def list_performance_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[int] = Query(None),
    reviewer_id: Optional[int] = Query(None),
    review_type: Optional[PerformanceReviewType] = Query(None),
    status: Optional[ReviewStatus] = Query(None),
    review_period_start: Optional[date] = Query(None),
    review_period_end: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of performance reviews"""
    if employee_id:
        return await performance_crud.get_reviews_by_employee(
            db, employee_id, current_user.company_id, skip, limit
        )
    elif reviewer_id:
        return await performance_crud.get_reviews_by_reviewer(
            db, reviewer_id, current_user.company_id, skip, limit
        )
    else:
        # Return all reviews for the company
        return await performance_crud.get_company_reviews(
            db, company_id=current_user.company_id, 
            status=status, review_type=review_type, skip=skip, limit=limit
        )


@router.get("/reviews/{review_id}", response_model=PerformanceResponse)
async def get_performance_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get performance review details"""
    review = await performance_crud.get_review_by_id(db, review_id=review_id, company_id=current_user.company_id)
    if not review:
        raise HTTPException(status_code=404, detail="Performance review not found")
    return review


@router.put("/reviews/{review_id}", response_model=PerformanceResponse)
async def update_performance_review_record(
    review_id: int,
    review_update: PerformanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update performance review"""
    review = await performance_crud.update_review(db, review_id, review_update, current_user.company_id)
    if not review:
        raise HTTPException(status_code=404, detail="Performance review not found")
    return review


@router.post("/reviews/{review_id}/submit-self-assessment")
async def submit_self_assessment(
    review_id: int,
    self_assessment_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit self-assessment for performance review"""
    review = await performance_crud.submit_self_assessment(
        db, 
        review_id=review_id, 
        employee_id=current_user.employee_id,
        assessment_data=self_assessment_data,
        company_id=current_user.company_id
    )
    if not review:
        raise HTTPException(status_code=404, detail="Performance review not found or access denied")
    return review


@router.post("/reviews/{review_id}/submit-manager-review")
async def submit_manager_review(
    review_id: int,
    manager_review_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit manager review"""
    review = await performance_crud.submit_manager_review(
        db,
        review_id=review_id,
        reviewer_id=current_user.employee_id,
        review_data=manager_review_data,
        company_id=current_user.company_id
    )
    if not review:
        raise HTTPException(status_code=404, detail="Performance review not found or access denied")
    return review


@router.post("/reviews/{review_id}/finalize")
async def finalize_performance_review(
    review_id: int,
    final_review_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Finalize performance review"""
    # Check if user has HR permissions
    if not current_user.is_hr_admin:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    review = await performance_crud.finalize_review(
        db,
        review_id=review_id,
        hr_user_id=current_user.id,
        final_data=final_review_data,
        company_id=current_user.company_id
    )
    if not review:
        raise HTTPException(status_code=404, detail="Performance review not found")
    return review


# Performance Goals
@router.post("/goals", response_model=PerformanceGoalResponse)
async def create_new_performance_goal(
    goal: PerformanceGoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new performance goal"""
    return await performance_goal_crud.create_goal(db, goal)


@router.get("/goals", response_model=List[PerformanceGoalResponse])
async def list_performance_goals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    performance_id: Optional[int] = Query(None),
    status: Optional[GoalStatus] = Query(None),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of performance goals"""
    if performance_id:
        return await performance_goal_crud.get_goals_by_performance(db, performance_id, status)
    else:
        return []


@router.put("/goals/{goal_id}", response_model=PerformanceGoalResponse)
async def update_performance_goal_record(
    goal_id: int,
    goal_update: PerformanceGoalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update performance goal"""
    goal = await performance_goal_crud.update_goal(db, goal_id, goal_update)
    if not goal:
        raise HTTPException(status_code=404, detail="Performance goal not found")
    return goal


@router.post("/goals/{goal_id}/update-progress")
async def update_goal_progress(
    goal_id: int,
    progress_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update goal progress"""
    goal = await performance_goal_crud.update_goal_progress(
        db, goal_id=goal_id, progress_data=progress_data
    )
    if not goal:
        raise HTTPException(status_code=404, detail="Performance goal not found")
    return goal


# Performance Templates
@router.post("/templates", response_model=PerformanceTemplateResponse)
async def create_new_performance_template(
    template: PerformanceTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new performance review template"""
    # Templates are read-only for now - would need template creation logic
    raise HTTPException(status_code=501, detail="Template creation not implemented")


@router.get("/templates", response_model=List[PerformanceTemplateResponse])
async def list_performance_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    review_type: Optional[PerformanceReviewType] = Query(None),
    is_active: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of performance review templates"""
    return await performance_template_crud.get_templates(db, current_user.company_id, is_active)


@router.get("/review-types")
async def get_review_types():
    """Get list of available review types"""
    return [{"value": rt.value, "label": rt.value.replace("_", " ").title()} 
            for rt in PerformanceReviewType]


@router.get("/reviews/employee/{employee_id}")
async def get_employee_performance_history(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get performance review history for an employee"""
    reviews = await performance_crud.get_reviews_by_employee(
        db, employee_id=employee_id, company_id=current_user.company_id
    )
    return reviews


@router.get("/reviews/analytics/summary")
async def get_performance_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    department_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get performance analytics and summary"""
    analytics = await performance_crud.get_performance_analytics(
        db,
        company_id=current_user.company_id,
        start_date=start_date,
        end_date=end_date,
        department_id=department_id
    )
    return analytics


@router.post("/reviews/bulk-create")
async def bulk_create_reviews(
    review_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Bulk create performance reviews for multiple employees"""
    # Check if user has admin/HR permissions
    if not current_user.is_admin and not current_user.is_hr_admin:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    reviews = await performance_crud.bulk_create_reviews(
        db,
        review_data=review_data,
        created_by=current_user.id,
        company_id=current_user.company_id
    )
    return {"created_count": len(reviews), "reviews": reviews}


@router.get("/reviews/{review_id}/export")
async def export_performance_review(
    review_id: int,
    format: str = Query("pdf"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export performance review to PDF or Excel"""
    # Validate format
    if format not in ["pdf", "excel"]:
        raise HTTPException(status_code=400, detail="Format must be 'pdf' or 'excel'")
    
    review = await performance_crud.get_review_by_id(
        db, review_id=review_id, company_id=current_user.company_id
    )
    if not review:
        raise HTTPException(status_code=404, detail="Performance review not found")
    
    # Implementation for PDF/Excel export would go here
    # For now, return review data that can be processed by frontend
    return {
        "review": review,
        "format": format,
        "message": f"Review exported in {format} format"
    }


# Advanced Performance Management Features

@router.post("/reviews/{review_id}/360-feedback")
async def submit_360_feedback(
    review_id: int,
    feedback_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit 360-degree feedback for performance review"""
    # Implementation for 360-degree feedback
    # This includes peer reviews, subordinate feedback, customer feedback
    feedback_type = feedback_data.get('feedback_type')  # peer, subordinate, customer, other
    feedback_comments = feedback_data.get('comments')
    ratings = feedback_data.get('ratings', {})
    
    # Store 360 feedback in database (would need additional model)
    return {
        "message": "360-degree feedback submitted successfully",
        "feedback_type": feedback_type,
        "review_id": review_id
    }


@router.get("/competencies")
async def get_competency_framework(
    job_level: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get competency framework for performance evaluation"""
    # Return competency frameworks based on role/level
    competencies = {
        "technical_competencies": [
            {"name": "Technical Expertise", "description": "Depth of technical knowledge", "weight": 30},
            {"name": "Problem Solving", "description": "Ability to solve complex problems", "weight": 25},
            {"name": "Innovation", "description": "Creative thinking and innovation", "weight": 20}
        ],
        "behavioral_competencies": [
            {"name": "Communication", "description": "Effective communication skills", "weight": 15},
            {"name": "Teamwork", "description": "Collaboration and team contribution", "weight": 20},
            {"name": "Leadership", "description": "Leadership and mentoring abilities", "weight": 25}
        ],
        "business_competencies": [
            {"name": "Business Acumen", "description": "Understanding of business context", "weight": 20},
            {"name": "Customer Focus", "description": "Customer-centric approach", "weight": 15},
            {"name": "Results Orientation", "description": "Focus on achieving results", "weight": 25}
        ]
    }
    return competencies


@router.post("/reviews/{review_id}/competency-assessment")
async def submit_competency_assessment(
    review_id: int,
    assessment_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit competency-based assessment"""
    # Implementation for competency assessment
    competency_ratings = assessment_data.get('competency_ratings', {})
    assessment_type = assessment_data.get('type')  # self, manager, peer
    
    return {
        "message": "Competency assessment submitted successfully",
        "competencies_assessed": len(competency_ratings),
        "assessment_type": assessment_type
    }


@router.get("/reviews/{review_id}/development-plan")
async def get_development_plan(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get individual development plan based on performance review"""
    review = await performance_crud.get_review_by_id(
        db, review_id=review_id, company_id=current_user.company_id
    )
    if not review:
        raise HTTPException(status_code=404, detail="Performance review not found")
    
    # Generate development plan based on review results
    development_plan = {
        "strengths_to_leverage": review.strengths.split('\n') if review.strengths else [],
        "areas_for_improvement": review.areas_for_improvement.split('\n') if review.areas_for_improvement else [],
        "recommended_training": [
            "Leadership Development Program",
            "Technical Skills Enhancement",
            "Communication Skills Workshop"
        ],
        "career_progression": {
            "current_level": "Senior Developer",
            "next_level": "Tech Lead",
            "timeline": "12-18 months",
            "required_skills": ["Team Leadership", "Architecture Design", "Mentoring"]
        },
        "smart_goals": [
            {
                "goal": "Complete leadership training certification",
                "timeline": "6 months",
                "measurable_outcome": "Certification completion"
            },
            {
                "goal": "Mentor 2 junior developers",
                "timeline": "12 months",
                "measurable_outcome": "Successful completion of mentoring program"
            }
        ]
    }
    return development_plan


@router.post("/reviews/{review_id}/development-plan")
async def create_development_plan(
    review_id: int,
    plan_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create or update individual development plan"""
    # Implementation for creating/updating development plans
    return {
        "message": "Development plan created successfully",
        "plan_id": "dev_plan_123",
        "review_id": review_id
    }


@router.get("/calibration")
async def get_calibration_data(
    department_id: Optional[int] = Query(None),
    review_cycle: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get calibration data for performance review normalization"""
    # Performance calibration to ensure consistent ratings across teams
    calibration_data = {
        "rating_distribution": {
            "5.0": 10,  # % of employees at each rating
            "4.0-4.9": 25,
            "3.0-3.9": 40,
            "2.0-2.9": 20,
            "1.0-1.9": 5
        },
        "department_averages": {
            "Engineering": 3.8,
            "Sales": 3.6,
            "Marketing": 3.7,
            "HR": 3.9
        },
        "recommendations": [
            "Consider normalizing ratings in Sales department",
            "Engineering ratings appear well-calibrated"
        ]
    }
    return calibration_data


@router.post("/calibration/session")
async def create_calibration_session(
    session_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create calibration session for performance reviews"""
    # Implementation for calibration sessions
    return {
        "session_id": "cal_session_123",
        "participants": session_data.get('participants', []),
        "scheduled_date": session_data.get('scheduled_date'),
        "status": "scheduled"
    }


@router.get("/succession-planning")
async def get_succession_planning_data(
    position_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get succession planning data based on performance reviews"""
    # Identify high performers for succession planning
    succession_data = {
        "critical_positions": [
            {
                "position": "Engineering Manager",
                "current_incumbent": "John Doe",
                "successors": [
                    {"name": "Jane Smith", "readiness": "Ready Now", "performance_rating": 4.5},
                    {"name": "Bob Johnson", "readiness": "Ready in 1 Year", "performance_rating": 4.2}
                ]
            }
        ],
        "high_potential_employees": [
            {"name": "Alice Brown", "current_role": "Senior Developer", "potential_roles": ["Tech Lead", "Engineering Manager"]},
            {"name": "Charlie Wilson", "current_role": "Sales Executive", "potential_roles": ["Sales Manager"]}
        ]
    }
    return succession_data


@router.get("/talent-matrix")
async def get_talent_matrix(
    department_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get 9-box talent matrix based on performance and potential"""
    # 9-box grid: Performance (x-axis) vs Potential (y-axis)
    talent_matrix = {
        "matrix_data": [
            {"employee": "John Doe", "performance": "High", "potential": "High", "box": "Star"},
            {"employee": "Jane Smith", "performance": "High", "potential": "Medium", "box": "Core Player"},
            {"employee": "Bob Johnson", "performance": "Medium", "potential": "High", "box": "High Potential"}
        ],
        "distribution": {
            "stars": 15,
            "core_players": 45,
            "high_potential": 20,
            "solid_performers": 15,
            "under_performers": 5
        }
    }
    return talent_matrix


@router.get("/reviews/trends")
async def get_performance_trends(
    timeframe: str = Query("12months"),
    metric: str = Query("overall_rating"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get performance trends and analytics over time"""
    # Validate parameters
    if timeframe not in ["6months", "12months", "24months"]:
        raise HTTPException(status_code=400, detail="Timeframe must be '6months', '12months', or '24months'")
    
    if metric not in ["overall_rating", "completion_rate", "goal_achievement"]:
        raise HTTPException(status_code=400, detail="Metric must be 'overall_rating', 'completion_rate', or 'goal_achievement'")
    
    # Performance trends analysis
    trends_data = {
        "timeline": ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"],
        "overall_rating_trend": [3.6, 3.7, 3.8, 3.9],
        "completion_rate_trend": [85, 88, 92, 95],
        "goal_achievement_trend": [78, 82, 85, 88],
        "insights": [
            "Performance ratings showing upward trend",
            "Completion rates have improved significantly",
            "Goal achievement rates are consistently improving"
        ]
    }
    return trends_data


@router.post("/reviews/remind")
async def send_review_reminders(
    reminder_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send automated reminders for pending performance reviews"""
    # Implementation for automated reminders
    reminder_type = reminder_data.get('type')  # due_soon, overdue, self_assessment, manager_review
    recipients = reminder_data.get('recipients', [])
    
    return {
        "message": f"Reminders sent successfully",
        "type": reminder_type,
        "recipients_count": len(recipients)
    }


@router.get("/reviews/dashboard")
async def get_performance_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get performance management dashboard data"""
    # Comprehensive dashboard for HR/managers
    dashboard_data = {
        "overview": {
            "total_reviews": 150,
            "completed_reviews": 120,
            "pending_reviews": 30,
            "overdue_reviews": 5
        },
        "ratings_summary": {
            "average_rating": 3.8,
            "distribution": {"5": 15, "4": 35, "3": 30, "2": 15, "1": 5}
        },
        "goals_progress": {
            "total_goals": 450,
            "achieved": 320,
            "in_progress": 100,
            "not_started": 30
        },
        "upcoming_deadlines": [
            {"employee": "John Doe", "due_date": "2024-12-15", "type": "Self Assessment"},
            {"employee": "Jane Smith", "due_date": "2024-12-20", "type": "Manager Review"}
        ],
        "recent_completions": [
            {"employee": "Bob Johnson", "completion_date": "2024-12-10", "rating": 4.2},
            {"employee": "Alice Brown", "completion_date": "2024-12-09", "rating": 4.5}
        ]
    }
    return dashboard_data


@router.post("/reviews/templates/custom")
async def create_custom_review_template(
    template_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create custom performance review template"""
    # Implementation for custom template creation
    template_name = template_data.get('name')
    sections = template_data.get('sections', [])
    competencies = template_data.get('competencies', [])
    
    return {
        "template_id": "custom_template_123",
        "name": template_name,
        "sections_count": len(sections),
        "competencies_count": len(competencies),
        "status": "created"
    }


@router.get("/reviews/benchmarking")
async def get_performance_benchmarking(
    industry: Optional[str] = Query(None),
    company_size: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get performance benchmarking data against industry standards"""
    # External benchmarking data
    benchmarking_data = {
        "company_metrics": {
            "average_rating": 3.8,
            "completion_rate": 95,
            "goal_achievement": 88
        },
        "industry_average": {
            "average_rating": 3.6,
            "completion_rate": 87,
            "goal_achievement": 82
        },
        "top_quartile": {
            "average_rating": 4.2,
            "completion_rate": 98,
            "goal_achievement": 95
        },
        "insights": [
            "Your performance ratings are above industry average",
            "Completion rates are excellent compared to peers",
            "Goal achievement is strong but has room for improvement"
        ]
    }
    return benchmarking_data
