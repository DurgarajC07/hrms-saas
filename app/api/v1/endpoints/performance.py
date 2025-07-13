from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.performance import PerformanceReviewType, ReviewStatus, GoalStatus
from app.schemas.performance import (
    PerformanceCreate, PerformanceUpdate, PerformanceResponse,
    PerformanceGoalCreate, PerformanceGoalUpdate, PerformanceGoalResponse,
    PerformanceTemplateCreate, PerformanceTemplateResponse
)
from app.crud.performance import (
    create_performance_review, get_performance_reviews, update_performance_review,
    create_performance_goal, get_performance_goals, update_performance_goal,
    create_performance_template, get_performance_templates
)

router = APIRouter()


@router.post("/reviews", response_model=PerformanceResponse)
async def create_new_performance_review(
    review: PerformanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new performance review"""
    return await create_performance_review(db, review, current_user.company_id)


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
    return await get_performance_reviews(
        db, current_user.company_id, skip, limit,
        employee_id, reviewer_id, review_type, status,
        review_period_start, review_period_end
    )


@router.get("/reviews/{review_id}", response_model=PerformanceResponse)
async def get_performance_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get performance review details"""
    # Implementation for getting specific review
    pass


@router.put("/reviews/{review_id}", response_model=PerformanceResponse)
async def update_performance_review_record(
    review_id: int,
    review_update: PerformanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update performance review"""
    review = await update_performance_review(db, review_id, review_update, current_user.company_id)
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
    # Implementation for self-assessment submission
    pass


@router.post("/reviews/{review_id}/submit-manager-review")
async def submit_manager_review(
    review_id: int,
    manager_review_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit manager review"""
    # Implementation for manager review submission
    pass


@router.post("/reviews/{review_id}/finalize")
async def finalize_performance_review(
    review_id: int,
    final_review_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Finalize performance review"""
    # Implementation for finalizing review
    pass


# Performance Goals
@router.post("/goals", response_model=PerformanceGoalResponse)
async def create_new_performance_goal(
    goal: PerformanceGoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new performance goal"""
    return await create_performance_goal(db, goal)


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
    return await get_performance_goals(db, skip, limit, performance_id, status, category)


@router.put("/goals/{goal_id}", response_model=PerformanceGoalResponse)
async def update_performance_goal_record(
    goal_id: int,
    goal_update: PerformanceGoalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update performance goal"""
    goal = await update_performance_goal(db, goal_id, goal_update)
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
    # Implementation for updating goal progress
    pass


# Performance Templates
@router.post("/templates", response_model=PerformanceTemplateResponse)
async def create_new_performance_template(
    template: PerformanceTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new performance review template"""
    return await create_performance_template(db, template, current_user.company_id)


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
    return await get_performance_templates(db, current_user.company_id, skip, limit, review_type, is_active)


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
    # Implementation for employee performance history
    pass


@router.get("/reviews/analytics/summary")
async def get_performance_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    department_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get performance analytics and summary"""
    # Implementation for performance analytics
    # Returns average ratings, completion rates, trends, etc.
    pass


@router.post("/reviews/bulk-create")
async def bulk_create_reviews(
    review_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Bulk create performance reviews for multiple employees"""
    # Implementation for bulk review creation
    pass


@router.get("/reviews/{review_id}/export")
async def export_performance_review(
    review_id: int,
    format: str = Query("pdf", regex="^(pdf|excel)$"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export performance review to PDF or Excel"""
    # Implementation for exporting review
    pass
