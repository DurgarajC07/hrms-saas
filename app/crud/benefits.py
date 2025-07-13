"""
Benefits administration CRUD operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, date

from app.crud.base import CRUDBase
from app.models.benefits import (
    EmployeeBenefitPlan, BenefitEnrollment, BenefitDependent, BenefitOpenEnrollment,
    BenefitType, BenefitStatus, EnrollmentStatus
)
from app.schemas.benefits import (
    BenefitPlanCreate, BenefitPlanUpdate,
    BenefitEnrollmentCreate, BenefitEnrollmentUpdate,
    OpenEnrollmentCreate
)


# Benefit Plan CRUD
async def create_benefit_plan(
    db: AsyncSession,
    plan: BenefitPlanCreate
) -> EmployeeBenefitPlan:
    """Create benefit plan"""
    db_obj = EmployeeBenefitPlan(**plan.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_benefit_plans(
    db: AsyncSession,
    company_id: int,
    benefit_type: Optional[BenefitType] = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 100
) -> List[EmployeeBenefitPlan]:
    """Get benefit plans"""
    query = select(EmployeeBenefitPlan).where(
        and_(
            EmployeeBenefitPlan.company_id == company_id,
            EmployeeBenefitPlan.is_active == is_active
        )
    )
    
    if benefit_type:
        query = query.where(EmployeeBenefitPlan.benefit_type == benefit_type)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_benefit_plan(
    db: AsyncSession,
    plan_id: int,
    plan_update: BenefitPlanUpdate
) -> Optional[EmployeeBenefitPlan]:
    """Update benefit plan"""
    result = await db.execute(select(EmployeeBenefitPlan).where(EmployeeBenefitPlan.id == plan_id))
    db_obj = result.scalars().first()
    
    if not db_obj:
        return None
    
    update_data = plan_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# Benefit Enrollment CRUD
async def create_enrollment(
    db: AsyncSession,
    enrollment: BenefitEnrollmentCreate
) -> BenefitEnrollment:
    """Create benefit enrollment"""
    db_obj = BenefitEnrollment(**enrollment.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_enrollments(
    db: AsyncSession,
    employee_id: Optional[int] = None,
    plan_id: Optional[int] = None,
    status: Optional[EnrollmentStatus] = None,
    skip: int = 0,
    limit: int = 100
) -> List[BenefitEnrollment]:
    """Get benefit enrollments"""
    query = select(BenefitEnrollment)
    
    if employee_id:
        query = query.where(BenefitEnrollment.employee_id == employee_id)
    if plan_id:
        query = query.where(BenefitEnrollment.plan_id == plan_id)
    if status:
        query = query.where(BenefitEnrollment.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def update_enrollment(
    db: AsyncSession,
    enrollment_id: int,
    enrollment_update: BenefitEnrollmentUpdate
) -> Optional[BenefitEnrollment]:
    """Update benefit enrollment"""
    result = await db.execute(select(BenefitEnrollment).where(BenefitEnrollment.id == enrollment_id))
    db_obj = result.scalars().first()
    
    if not db_obj:
        return None
    
    update_data = enrollment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# Open Enrollment CRUD
async def create_open_enrollment(
    db: AsyncSession,
    open_enrollment: OpenEnrollmentCreate
) -> BenefitOpenEnrollment:
    """Create open enrollment period"""
    db_obj = BenefitOpenEnrollment(**open_enrollment.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_open_enrollments(
    db: AsyncSession,
    company_id: int,
    year: Optional[int] = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 100
) -> List[BenefitOpenEnrollment]:
    """Get open enrollment periods"""
    query = select(BenefitOpenEnrollment).where(
        and_(
            BenefitOpenEnrollment.company_id == company_id,
            BenefitOpenEnrollment.is_active == is_active
        )
    )
    
    if year:
        query = query.where(BenefitOpenEnrollment.enrollment_year == year)
    
    query = query.order_by(desc(BenefitOpenEnrollment.enrollment_year)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
