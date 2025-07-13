"""
CRUD operations for Employee model
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.crud.base import CRUDBase
from app.models.employee import Employee
from typing import Optional, List
from datetime import datetime


class CRUDEmployee(CRUDBase[Employee, dict, dict]):
    """Employee CRUD operations"""
    
    async def get_by_employee_id(self, db: AsyncSession, *, employee_id: str) -> Optional[Employee]:
        """Get employee by employee ID"""
        result = await db.execute(select(Employee).where(Employee.employee_id == employee_id))
        return result.scalars().first()
    
    async def get_by_user_id(self, db: AsyncSession, *, user_id: int) -> Optional[Employee]:
        """Get employee by user ID"""
        result = await db.execute(select(Employee).where(Employee.user_id == user_id))
        return result.scalars().first()
    
    async def get_by_company(
        self, 
        db: AsyncSession, 
        *, 
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """Get employees by company"""
        result = await db.execute(
            select(Employee)
            .where(Employee.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_department(
        self, 
        db: AsyncSession, 
        *, 
        department_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """Get employees by department"""
        result = await db.execute(
            select(Employee)
            .where(Employee.department_id == department_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_manager(
        self, 
        db: AsyncSession, 
        *, 
        manager_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """Get employees by manager"""
        result = await db.execute(
            select(Employee)
            .where(Employee.manager_id == manager_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_employees(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """Search employees by name, email, or employee ID"""
        search_filter = or_(
            Employee.first_name.ilike(f"%{search_term}%"),
            Employee.last_name.ilike(f"%{search_term}%"),
            Employee.work_email.ilike(f"%{search_term}%"),
            Employee.employee_id.ilike(f"%{search_term}%")
        )
        
        result = await db.execute(
            select(Employee)
            .where(and_(Employee.company_id == company_id, search_filter))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_active_employees(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """Get active employees"""
        result = await db.execute(
            select(Employee)
            .where(
                and_(
                    Employee.company_id == company_id,
                    Employee.is_active == True,
                    Employee.status == "ACTIVE"
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_last_activity(
        self,
        db: AsyncSession,
        *,
        employee_id: int
    ) -> Optional[Employee]:
        """Update employee last activity timestamp"""
        employee = await self.get(db, id=employee_id)
        if employee:
            employee.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(employee)
        return employee


# Create global instance
employee_crud = CRUDEmployee(Employee)
