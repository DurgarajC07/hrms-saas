from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.crud.base import CRUDBase
from app.models.performance import (
    Performance, PerformanceGoal, PerformanceTemplate,
    PerformanceReviewType, ReviewStatus, GoalStatus
)
from app.models.employee import Employee
from app.schemas.performance import (
    PerformanceCreate, PerformanceUpdate,
    PerformanceGoalCreate, PerformanceGoalUpdate,
    PerformanceTemplateCreate
)
import logging

logger = logging.getLogger(__name__)


class CRUDPerformance(CRUDBase[Performance, PerformanceCreate, PerformanceUpdate]):
    
    async def create_review(
        self,
        db: AsyncSession,
        *,
        review_data: PerformanceCreate,
        created_by: int,
        company_id: int
    ) -> Performance:
        """Create a new performance review"""
        db_obj = Performance(
            **review_data.dict(),
            company_id=company_id,
            created_by=created_by,
            status=ReviewStatus.DRAFT
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_review_by_id(
        self,
        db: AsyncSession,
        *,
        review_id: int,
        company_id: int
    ) -> Optional[Performance]:
        """Get performance review by ID"""
        result = await db.execute(
            select(Performance)
            .options(selectinload(Performance.goals))
            .where(
                and_(
                    Performance.id == review_id,
                    Performance.company_id == company_id
                )
            )
        )
        return result.scalars().first()
    
    async def get_reviews_by_employee(
        self,
        db: AsyncSession,
        *,
        employee_id: int,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Performance]:
        """Get performance reviews for an employee"""
        result = await db.execute(
            select(Performance)
            .options(selectinload(Performance.goals))
            .where(
                and_(
                    Performance.employee_id == employee_id,
                    Performance.company_id == company_id
                )
            )
            .order_by(desc(Performance.review_period_start))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_reviews_by_reviewer(
        self,
        db: AsyncSession,
        *,
        reviewer_id: int,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Performance]:
        """Get performance reviews assigned to a reviewer"""
        result = await db.execute(
            select(Performance)
            .options(selectinload(Performance.goals))
            .where(
                and_(
                    Performance.reviewer_id == reviewer_id,
                    Performance.company_id == company_id
                )
            )
            .order_by(desc(Performance.due_date))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_company_reviews(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        status: Optional[ReviewStatus] = None,
        review_type: Optional[PerformanceReviewType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Performance]:
        """Get all performance reviews for a company with filters"""
        query = select(Performance).options(selectinload(Performance.goals)).where(
            Performance.company_id == company_id
        )
        
        if status:
            query = query.where(Performance.status == status)
        if review_type:
            query = query.where(Performance.review_type == review_type)
            
        query = query.order_by(desc(Performance.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_review(
        self,
        db: AsyncSession,
        *,
        review_id: int,
        review_update: PerformanceUpdate,
        company_id: int
    ) -> Optional[Performance]:
        """Update performance review"""
        db_obj = await self.get_review_by_id(db, review_id=review_id, company_id=company_id)
        if not db_obj:
            return None
            
        update_data = review_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def submit_self_assessment(
        self,
        db: AsyncSession,
        *,
        review_id: int,
        employee_id: int,
        assessment_data: Dict[str, Any],
        company_id: int
    ) -> Optional[Performance]:
        """Submit employee self-assessment"""
        db_obj = await self.get_review_by_id(db, review_id=review_id, company_id=company_id)
        if not db_obj or db_obj.employee_id != employee_id:
            return None
        
        # Update self-assessment fields
        db_obj.self_assessment_completed = True
        db_obj.self_assessment_date = datetime.utcnow()
        db_obj.self_rating = assessment_data.get('self_rating')
        db_obj.achievements = assessment_data.get('achievements')
        db_obj.challenges_faced = assessment_data.get('challenges_faced')
        db_obj.employee_comments = assessment_data.get('employee_comments')
        
        # Update status if needed
        if db_obj.status == ReviewStatus.DRAFT:
            db_obj.status = ReviewStatus.MANAGER_REVIEW_PENDING
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def submit_manager_review(
        self,
        db: AsyncSession,
        *,
        review_id: int,
        reviewer_id: int,
        review_data: Dict[str, Any],
        company_id: int
    ) -> Optional[Performance]:
        """Submit manager review"""
        db_obj = await self.get_review_by_id(db, review_id=review_id, company_id=company_id)
        if not db_obj or db_obj.reviewer_id != reviewer_id:
            return None
        
        # Update manager review fields
        db_obj.manager_review_completed = True
        db_obj.manager_review_date = datetime.utcnow()
        db_obj.recommended_rating = review_data.get('recommended_rating')
        db_obj.promotion_recommendation = review_data.get('promotion_recommendation', False)
        db_obj.salary_increase_recommendation = review_data.get('salary_increase_recommendation')
        db_obj.manager_comments = review_data.get('manager_comments')
        db_obj.strengths = review_data.get('strengths')
        db_obj.areas_for_improvement = review_data.get('areas_for_improvement')
        db_obj.development_plan = review_data.get('development_plan')
        
        # Update ratings
        db_obj.overall_rating = review_data.get('overall_rating')
        db_obj.technical_skills_rating = review_data.get('technical_skills_rating')
        db_obj.communication_rating = review_data.get('communication_rating')
        db_obj.teamwork_rating = review_data.get('teamwork_rating')
        db_obj.leadership_rating = review_data.get('leadership_rating')
        db_obj.initiative_rating = review_data.get('initiative_rating')
        
        # Update status
        db_obj.status = ReviewStatus.HR_REVIEW_PENDING
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def finalize_review(
        self,
        db: AsyncSession,
        *,
        review_id: int,
        hr_user_id: int,
        final_data: Dict[str, Any],
        company_id: int
    ) -> Optional[Performance]:
        """Finalize performance review"""
        db_obj = await self.get_review_by_id(db, review_id=review_id, company_id=company_id)
        if not db_obj:
            return None
        
        # Update final review fields
        db_obj.final_review_completed = True
        db_obj.final_review_date = datetime.utcnow()
        db_obj.final_reviewed_by = hr_user_id
        db_obj.hr_comments = final_data.get('hr_comments')
        db_obj.status = ReviewStatus.COMPLETED
        db_obj.completion_percentage = 100
        
        # Override ratings if provided
        if 'final_overall_rating' in final_data:
            db_obj.overall_rating = final_data['final_overall_rating']
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_performance_analytics(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        department_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get performance analytics and summary"""
        query = select(Performance).where(Performance.company_id == company_id)
        
        if start_date:
            query = query.where(Performance.review_period_start >= start_date)
        if end_date:
            query = query.where(Performance.review_period_end <= end_date)
        
        result = await db.execute(query)
        reviews = result.scalars().all()
        
        # Calculate analytics
        total_reviews = len(reviews)
        completed_reviews = len([r for r in reviews if r.status == ReviewStatus.COMPLETED])
        avg_rating = sum([r.overall_rating for r in reviews if r.overall_rating]) / len([r for r in reviews if r.overall_rating]) if reviews else 0
        
        # Status distribution
        status_counts = {}
        for status in ReviewStatus:
            status_counts[status.value] = len([r for r in reviews if r.status == status])
        
        # Rating distribution
        rating_ranges = {
            "excellent": len([r for r in reviews if r.overall_rating and r.overall_rating >= 4.5]),
            "good": len([r for r in reviews if r.overall_rating and 3.5 <= r.overall_rating < 4.5]),
            "average": len([r for r in reviews if r.overall_rating and 2.5 <= r.overall_rating < 3.5]),
            "below_average": len([r for r in reviews if r.overall_rating and r.overall_rating < 2.5])
        }
        
        return {
            "total_reviews": total_reviews,
            "completed_reviews": completed_reviews,
            "completion_rate": (completed_reviews / total_reviews * 100) if total_reviews > 0 else 0,
            "average_rating": round(avg_rating, 2),
            "status_distribution": status_counts,
            "rating_distribution": rating_ranges
        }
    
    async def bulk_create_reviews(
        self,
        db: AsyncSession,
        *,
        review_data: Dict[str, Any],
        created_by: int,
        company_id: int
    ) -> List[Performance]:
        """Bulk create performance reviews"""
        employee_ids = review_data.get('employee_ids', [])
        review_template = review_data.get('review_template', {})
        
        created_reviews = []
        for employee_id in employee_ids:
            review = Performance(
                company_id=company_id,
                employee_id=employee_id,
                reviewer_id=review_template.get('reviewer_id'),
                review_type=PerformanceReviewType(review_template.get('review_type')),
                review_period_start=review_template.get('review_period_start'),
                review_period_end=review_template.get('review_period_end'),
                due_date=review_template.get('due_date'),
                created_by=created_by,
                status=ReviewStatus.DRAFT
            )
            db.add(review)
            created_reviews.append(review)
        
        await db.commit()
        return created_reviews


class CRUDPerformanceGoal(CRUDBase[PerformanceGoal, PerformanceGoalCreate, PerformanceGoalUpdate]):
    
    async def create_goal(
        self,
        db: AsyncSession,
        *,
        goal_data: PerformanceGoalCreate
    ) -> PerformanceGoal:
        """Create a new performance goal"""
        db_obj = PerformanceGoal(**goal_data.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_goals_by_performance(
        self,
        db: AsyncSession,
        *,
        performance_id: int,
        status: Optional[GoalStatus] = None
    ) -> List[PerformanceGoal]:
        """Get goals for a performance review"""
        query = select(PerformanceGoal).where(PerformanceGoal.performance_id == performance_id)
        
        if status:
            query = query.where(PerformanceGoal.status == status)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_goal(
        self,
        db: AsyncSession,
        *,
        goal_id: int,
        goal_update: PerformanceGoalUpdate
    ) -> Optional[PerformanceGoal]:
        """Update performance goal"""
        result = await db.execute(select(PerformanceGoal).where(PerformanceGoal.id == goal_id))
        db_obj = result.scalars().first()
        
        if not db_obj:
            return None
        
        update_data = goal_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update_goal_progress(
        self,
        db: AsyncSession,
        *,
        goal_id: int,
        progress_data: Dict[str, Any]
    ) -> Optional[PerformanceGoal]:
        """Update goal progress"""
        result = await db.execute(select(PerformanceGoal).where(PerformanceGoal.id == goal_id))
        db_obj = result.scalars().first()
        
        if not db_obj:
            return None
        
        db_obj.progress_percentage = progress_data.get('progress_percentage', db_obj.progress_percentage)
        db_obj.status = GoalStatus(progress_data.get('status', db_obj.status))
        db_obj.actual_achievement = progress_data.get('actual_achievement', db_obj.actual_achievement)
        db_obj.employee_comments = progress_data.get('employee_comments', db_obj.employee_comments)
        db_obj.manager_comments = progress_data.get('manager_comments', db_obj.manager_comments)
        
        # Auto-update status based on progress
        if db_obj.progress_percentage == 100:
            db_obj.status = GoalStatus.ACHIEVED
        elif db_obj.progress_percentage > 0:
            db_obj.status = GoalStatus.IN_PROGRESS
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


class CRUDPerformanceTemplate(CRUDBase[PerformanceTemplate, PerformanceTemplateCreate, PerformanceTemplateCreate]):
    
    async def get_templates(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        is_active: bool = True,
        review_type: Optional[PerformanceReviewType] = None
    ) -> List[PerformanceTemplate]:
        """Get performance templates for a company"""
        query = select(PerformanceTemplate).where(
            and_(
                PerformanceTemplate.company_id == company_id,
                PerformanceTemplate.is_active == is_active
            )
        )
        
        if review_type:
            query = query.where(PerformanceTemplate.review_type == review_type)
        
        result = await db.execute(query)
        return result.scalars().all()


# Create instances
performance_crud = CRUDPerformance(Performance)
performance_goal_crud = CRUDPerformanceGoal(PerformanceGoal)
performance_template_crud = CRUDPerformanceTemplate(PerformanceTemplate)