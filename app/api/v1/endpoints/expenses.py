from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.expense import Expense, ExpenseCategory, ExpensePolicy, Project
from app.schemas.expense import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseListResponse,
    ExpensePolicyCreate, ExpensePolicyUpdate, ExpensePolicyResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse
)
from app.crud.expense import (
    create_expense, get_expenses, get_expense, update_expense, delete_expense,
    create_expense_policy, get_expense_policies, update_expense_policy,
    create_project, get_projects, update_project
)

router = APIRouter()


@router.post("/expenses", response_model=ExpenseResponse)
async def create_new_expense(
    expense: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new expense record"""
    return await create_expense(db, expense, current_user.id)


@router.get("/expenses", response_model=ExpenseListResponse)
async def list_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[int] = Query(None),
    category: Optional[ExpenseCategory] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    project_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of expenses with filters"""
    expenses = await get_expenses(
        db, current_user.company_id, skip, limit,
        employee_id, category, status, start_date, end_date, project_id
    )
    return expenses


@router.get("/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense_detail(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get expense details by ID"""
    expense = await get_expense(db, expense_id, current_user.company_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense_record(
    expense_id: int,
    expense_update: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update expense record"""
    expense = await update_expense(db, expense_id, expense_update, current_user.company_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.delete("/expenses/{expense_id}")
async def delete_expense_record(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete expense record"""
    success = await delete_expense(db, expense_id, current_user.company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}


@router.post("/expenses/{expense_id}/submit")
async def submit_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit expense for approval"""
    # Implementation for submitting expense for approval
    # This would change status from draft to submitted
    pass


@router.post("/expenses/{expense_id}/approve")
async def approve_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Approve expense (manager/admin only)"""
    # Implementation for approving expense
    pass


@router.post("/expenses/{expense_id}/reject")
async def reject_expense(
    expense_id: int,
    rejection_reason: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Reject expense (manager/admin only)"""
    # Implementation for rejecting expense
    pass


@router.post("/expenses/{expense_id}/upload-receipt")
async def upload_receipt(
    expense_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload receipt for expense"""
    # Implementation for uploading receipt file
    pass


# Expense Policies
@router.post("/expense-policies", response_model=ExpensePolicyResponse)
async def create_new_expense_policy(
    policy: ExpensePolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new expense policy"""
    return await create_expense_policy(db, policy, current_user.company_id)


@router.get("/expense-policies", response_model=List[ExpensePolicyResponse])
async def list_expense_policies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[ExpenseCategory] = Query(None),
    is_active: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of expense policies"""
    return await get_expense_policies(db, current_user.company_id, skip, limit, category, is_active)


@router.put("/expense-policies/{policy_id}", response_model=ExpensePolicyResponse)
async def update_expense_policy_record(
    policy_id: int,
    policy_update: ExpensePolicyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update expense policy"""
    return await update_expense_policy(db, policy_id, policy_update, current_user.company_id)


# Projects
@router.post("/projects", response_model=ProjectResponse)
async def create_new_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new project"""
    return await create_project(db, project, current_user.company_id)


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of projects"""
    return await get_projects(db, current_user.company_id, skip, limit, is_active)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project_record(
    project_id: int,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update project"""
    return await update_project(db, project_id, project_update, current_user.company_id)


@router.get("/expense-categories")
async def get_expense_categories():
    """Get list of available expense categories"""
    return [{"value": cat.value, "label": cat.value.replace("_", " ").title()} 
            for cat in ExpenseCategory]


@router.get("/expenses/analytics/summary")
async def get_expense_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    department_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get expense analytics and summary"""
    # Implementation for expense analytics
    # Returns total expenses, category breakdown, trends, etc.
    pass
