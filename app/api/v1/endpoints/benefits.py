from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.benefits import BenefitType, BenefitStatus, EnrollmentStatus
from app.schemas.benefits import (
    BenefitPlanCreate, BenefitPlanUpdate, BenefitPlanResponse,
    BenefitEnrollmentCreate, BenefitEnrollmentUpdate, BenefitEnrollmentResponse,
    OpenEnrollmentCreate, OpenEnrollmentResponse
)
from app.crud.benefits import (
    create_benefit_plan, get_benefit_plans, update_benefit_plan,
    create_enrollment, get_enrollments, update_enrollment,
    create_open_enrollment, get_open_enrollments
)

router = APIRouter()


@router.post("/benefit-plans", response_model=BenefitPlanResponse)
async def create_new_benefit_plan(
    plan: BenefitPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new benefit plan"""
    return await create_benefit_plan(db, plan, current_user.company_id)


@router.get("/benefit-plans", response_model=List[BenefitPlanResponse])
async def list_benefit_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    benefit_type: Optional[BenefitType] = Query(None),
    status: Optional[BenefitStatus] = Query(None),
    plan_year: Optional[int] = Query(None),
    is_active: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of benefit plans"""
    return await get_benefit_plans(
        db, current_user.company_id, skip, limit, 
        benefit_type, status, plan_year, is_active
    )


@router.put("/benefit-plans/{plan_id}", response_model=BenefitPlanResponse)
async def update_benefit_plan_record(
    plan_id: int,
    plan_update: BenefitPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update benefit plan"""
    plan = await update_benefit_plan(db, plan_id, plan_update, current_user.company_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Benefit plan not found")
    return plan


@router.post("/enrollments", response_model=BenefitEnrollmentResponse)
async def create_new_enrollment(
    enrollment: BenefitEnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Enroll employee in benefit plan"""
    return await create_enrollment(db, enrollment, current_user.id)


@router.get("/enrollments", response_model=List[BenefitEnrollmentResponse])
async def list_enrollments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[int] = Query(None),
    plan_id: Optional[int] = Query(None),
    status: Optional[EnrollmentStatus] = Query(None),
    effective_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of benefit enrollments"""
    return await get_enrollments(
        db, current_user.company_id, skip, limit,
        employee_id, plan_id, status, effective_date
    )


@router.put("/enrollments/{enrollment_id}", response_model=BenefitEnrollmentResponse)
async def update_enrollment_record(
    enrollment_id: int,
    enrollment_update: BenefitEnrollmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update benefit enrollment"""
    enrollment = await update_enrollment(db, enrollment_id, enrollment_update, current_user.company_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


@router.post("/enrollments/{enrollment_id}/approve")
async def approve_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Approve benefit enrollment"""
    # Implementation for approving enrollment
    pass


@router.post("/enrollments/{enrollment_id}/reject")
async def reject_enrollment(
    enrollment_id: int,
    rejection_reason: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Reject benefit enrollment"""
    # Implementation for rejecting enrollment
    pass


@router.post("/open-enrollments", response_model=OpenEnrollmentResponse)
async def create_new_open_enrollment(
    open_enrollment: OpenEnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new open enrollment period"""
    return await create_open_enrollment(db, open_enrollment, current_user.company_id)


@router.get("/open-enrollments", response_model=List[OpenEnrollmentResponse])
async def list_open_enrollments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: bool = Query(True),
    plan_year: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of open enrollment periods"""
    return await get_open_enrollments(db, current_user.company_id, skip, limit, is_active, plan_year)


@router.get("/open-enrollments/current")
async def get_current_open_enrollment(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current active open enrollment period"""
    # Implementation to get current open enrollment
    pass


@router.get("/benefit-types")
async def get_benefit_types():
    """Get list of available benefit types"""
    return [{"value": bt.value, "label": bt.value.replace("_", " ").title()} 
            for bt in BenefitType]


@router.get("/enrollments/employee/{employee_id}")
async def get_employee_enrollments(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all benefit enrollments for an employee"""
    # Implementation for getting employee's enrollments
    pass


@router.get("/enrollments/analytics/summary")
async def get_enrollment_analytics(
    plan_year: Optional[int] = Query(None),
    benefit_type: Optional[BenefitType] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get benefit enrollment analytics"""
    # Implementation for enrollment analytics
    # Returns enrollment rates, costs, trends, etc.
    pass


@router.post("/enrollments/bulk-import")
async def bulk_import_enrollments(
    # Implementation for bulk importing enrollments from CSV/Excel
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Bulk import benefit enrollments"""
    pass


@router.get("/enrollments/{enrollment_id}/cost-breakdown")
async def get_enrollment_cost_breakdown(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detailed cost breakdown for enrollment"""
    # Implementation for cost analysis
    pass
