"""
Expense management CRUD operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, date

from app.crud.base import CRUDBase
from app.models.expense import Expense, ExpensePolicy, Project, ExpenseStatus, ExpenseCategory
from app.schemas.expense import (
    ExpenseCreate, ExpenseUpdate,
    ExpensePolicyCreate, ExpensePolicyUpdate,
    ProjectCreate, ProjectUpdate
)


class CRUDExpense(CRUDBase[Expense, ExpenseCreate, ExpenseUpdate]):
    
    async def create_expense(
        self,
        db: AsyncSession,
        *,
        expense_data: ExpenseCreate,
        company_id: int
    ) -> Expense:
        """Create a new expense"""
        db_obj = Expense(
            **expense_data.dict(),
            company_id=company_id,
            status=ExpenseStatus.DRAFT
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_expenses_by_employee(
        self,
        db: AsyncSession,
        *,
        employee_id: int,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Expense]:
        """Get expenses for an employee"""
        result = await db.execute(
            select(Expense)
            .where(
                and_(
                    Expense.employee_id == employee_id,
                    Expense.company_id == company_id
                )
            )
            .order_by(desc(Expense.expense_date))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


async def create_expense(db: AsyncSession, expense: ExpenseCreate) -> Expense:
    """Create a new expense"""
    expense_crud = CRUDExpense(Expense)
    return await expense_crud.create_expense(db, expense_data=expense, company_id=1)


async def get_expenses(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[int] = None
) -> List[Expense]:
    """Get expenses with optional filtering"""
    if employee_id:
        expense_crud = CRUDExpense(Expense)
        return await expense_crud.get_expenses_by_employee(
            db, employee_id=employee_id, company_id=1, skip=skip, limit=limit
        )
    
    result = await db.execute(select(Expense).offset(skip).limit(limit))
    return result.scalars().all()


async def get_expense(db: AsyncSession, expense_id: int) -> Optional[Expense]:
    """Get expense by ID"""
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    return result.scalars().first()


async def update_expense(
    db: AsyncSession,
    expense_id: int,
    expense_update: ExpenseUpdate
) -> Optional[Expense]:
    """Update expense"""
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    db_obj = result.scalars().first()
    
    if not db_obj:
        return None
    
    update_data = expense_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_expense(db: AsyncSession, expense_id: int) -> bool:
    """Delete expense"""
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    db_obj = result.scalars().first()
    
    if not db_obj:
        return False
    
    await db.delete(db_obj)
    await db.commit()
    return True


# Expense Policy CRUD
async def create_expense_policy(
    db: AsyncSession,
    policy: ExpensePolicyCreate
) -> ExpensePolicy:
    """Create expense policy"""
    db_obj = ExpensePolicy(**policy.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_expense_policies(
    db: AsyncSession,
    company_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[ExpensePolicy]:
    """Get expense policies"""
    result = await db.execute(
        select(ExpensePolicy)
        .where(ExpensePolicy.company_id == company_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_expense_policy(
    db: AsyncSession,
    policy_id: int,
    policy_update: ExpensePolicyUpdate
) -> Optional[ExpensePolicy]:
    """Update expense policy"""
    result = await db.execute(select(ExpensePolicy).where(ExpensePolicy.id == policy_id))
    db_obj = result.scalars().first()
    
    if not db_obj:
        return None
    
    update_data = policy_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# Project CRUD
async def create_project(db: AsyncSession, project: ProjectCreate) -> Project:
    """Create project"""
    db_obj = Project(**project.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_projects(
    db: AsyncSession,
    company_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Project]:
    """Get projects"""
    result = await db.execute(
        select(Project)
        .where(Project.company_id == company_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_project(
    db: AsyncSession,
    project_id: int,
    project_update: ProjectUpdate
) -> Optional[Project]:
    """Update project"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    db_obj = result.scalars().first()
    
    if not db_obj:
        return None
    
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
