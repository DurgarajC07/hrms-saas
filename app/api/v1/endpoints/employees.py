from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.employee import employee_crud
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=EmployeeResponse)
async def create_employee(
    employee_in: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new employee."""
    employee_in.company_id = current_user.company_id
    db_employee = await employee_crud.create(db, obj_in=employee_in)
    return db_employee

@router.get("/", response_model=List[EmployeeResponse])
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    employee_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all employees with filtering."""
    employees = await employee_crud.get_multi_with_filters(
        db,
        skip=skip,
        limit=limit,
        search=search,
        department_id=department_id,
        status=status,
        employee_type=employee_type,
        company_id=current_user.company_id
    )
    return employees

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific employee by ID."""
    db_employee = await employee_crud.get(db, id=employee_id)
    if not db_employee or db_employee.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_in: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an employee."""
    db_employee = await employee_crud.get(db, id=employee_id)
    if not db_employee or db_employee.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    updated_employee = await employee_crud.update(db, db_obj=db_employee, obj_in=employee_in)
    return updated_employee

@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an employee."""
    db_employee = await employee_crud.get(db, id=employee_id)
    if not db_employee or db_employee.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    await employee_crud.remove(db, id=employee_id)
    return {"message": "Employee deleted successfully"}

@router.get("/departments/list")
async def get_departments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all departments for the company."""
    departments = await employee_crud.get_departments(db, company_id=current_user.company_id)
    return departments

@router.get("/org-chart/data")
async def get_org_chart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organizational chart data."""
    org_chart = await employee_crud.get_org_chart(db, company_id=current_user.company_id)
    return org_chart

@router.get("/employee-types/list")
async def get_employee_types():
    """Get available employee types."""
    return [
        {"value": "full_time", "label": "Full-time"},
        {"value": "part_time", "label": "Part-time"},
        {"value": "contract", "label": "Contract"},
        {"value": "intern", "label": "Intern"},
        {"value": "temporary", "label": "Temporary"}
    ]

@router.get("/stats/summary")
async def get_employee_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get employee statistics summary."""
    stats = await employee_crud.get_employee_stats(db, company_id=current_user.company_id)
    return stats

@router.post("/{employee_id}/assign-manager")
async def assign_manager(
    employee_id: int,
    manager_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a manager to an employee."""
    db_employee = await employee_crud.get(db, id=employee_id)
    if not db_employee or db_employee.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    await employee_crud.assign_manager(db, employee_id=employee_id, manager_id=manager_id)
    return {"message": "Manager assigned successfully"}

@router.get("/{employee_id}/direct-reports")
async def get_direct_reports(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get direct reports for an employee."""
    db_employee = await employee_crud.get(db, id=employee_id)
    if not db_employee or db_employee.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    direct_reports = await employee_crud.get_direct_reports(db, employee_id=employee_id)
    return direct_reports

@router.post("/bulk-import")
async def bulk_import_employees(
    employees_data: List[EmployeeCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk import employees."""
    # Add company_id to all employees
    for emp_data in employees_data:
        emp_data.company_id = current_user.company_id
    
    result = await employee_crud.bulk_create(db, employees_data)
    return result
