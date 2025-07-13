"""
CRUD operations for Company model
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from app.crud.base import CRUDBase
from app.models.company import Company
from typing import Optional, List, Dict, Any
from datetime import datetime


class CRUDCompany(CRUDBase[Company, dict, dict]):
    """Company CRUD operations"""
    
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Company]:
        """Get company by name"""
        result = await db.execute(select(Company).where(Company.name == name))
        return result.scalars().first()
    
    async def get_by_registration_number(self, db: AsyncSession, *, registration_number: str) -> Optional[Company]:
        """Get company by registration number"""
        result = await db.execute(select(Company).where(Company.registration_number == registration_number))
        return result.scalars().first()
    
    async def get_multi_with_filters(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        industry: Optional[str] = None,
        size: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Company]:
        """Get companies with filters"""
        query = select(Company)
        
        # Apply filters
        filters = []
        
        if search:
            filters.append(
                or_(
                    Company.name.ilike(f"%{search}%"),
                    Company.legal_name.ilike(f"%{search}%"),
                    Company.email.ilike(f"%{search}%")
                )
            )
        
        if industry:
            filters.append(Company.industry == industry)
        
        if size:
            filters.append(Company.company_size == size)
        
        if status:
            filters.append(Company.status == status)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.offset(skip).limit(limit).order_by(Company.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_company_stats(self, db: AsyncSession, *, company_id: int) -> Dict[str, Any]:
        """Get company statistics"""
        from app.models.employee import Employee
        from app.models.leave import Leave
        from app.models.expense import Expense
        from app.models.payroll import Payroll
        from app.models.attendance import Attendance
        
        # Employee stats
        total_employees_result = await db.execute(
            select(func.count(Employee.id)).where(Employee.company_id == company_id)
        )
        total_employees = total_employees_result.scalar() or 0
        
        active_employees_result = await db.execute(
            select(func.count(Employee.id)).where(
                and_(Employee.company_id == company_id, Employee.status == "active")
            )
        )
        active_employees = active_employees_result.scalar() or 0
        
        # Department count
        departments_result = await db.execute(
            select(func.count(func.distinct(Employee.department_id))).where(
                and_(Employee.company_id == company_id, Employee.department_id.isnot(None))
            )
        )
        departments = departments_result.scalar() or 0
        
        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "departments": departments,
            "pending_leaves": 0,  # Placeholder
            "pending_expenses": 0,  # Placeholder
            "payroll_processed_this_month": 0,  # Placeholder
            "attendance_percentage": None,
            "average_performance_rating": None,
            "employee_satisfaction_score": None
        }
    
    async def update_settings(self, db: AsyncSession, *, company_id: int, settings: dict) -> bool:
        """Update company settings"""
        # This would typically update a separate settings table or JSON field
        # For now, return True as placeholder
        return True
    
    async def get_settings(self, db: AsyncSession, *, company_id: int) -> dict:
        """Get company settings"""
        # This would typically fetch from a separate settings table or JSON field
        # For now, return default settings
        return {
            "work_week_days": 5,
            "work_hours_per_day": 8.0,
            "overtime_threshold": 40.0,
            "leave_accrual_enabled": True,
            "performance_review_frequency": "annual",
            "probation_period_days": 90,
            "notice_period_days": 30,
            "expense_approval_required": True,
            "auto_clock_out_hours": 12,
            "password_policy": {},
            "notification_settings": {}
        }
    
    async def get_active_companies(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Company]:
        """Get active companies"""
        result = await db.execute(
            select(Company)
            .where(Company.status == "active")
            .offset(skip)
            .limit(limit)
            .order_by(Company.created_at.desc())
        )
        return result.scalars().all()


company = CRUDCompany(Company)
company_crud = CRUDCompany(Company)
