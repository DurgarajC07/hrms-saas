from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.company import company_crud
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_in: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new company."""
    db_company = await company_crud.create(db, obj_in=company_in)
    return db_company

@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all companies with filtering."""
    companies = await company_crud.get_multi_with_filters(
        db,
        skip=skip,
        limit=limit,
        search=search,
        industry=industry,
        size=size
    )
    return companies

@router.get("/current", response_model=CompanyResponse)
async def get_current_company(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's company."""
    db_company = await company_crud.get(db, id=current_user.company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific company by ID."""
    db_company = await company_crud.get(db, id=company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_in: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a company."""
    # Only allow users to update their own company
    if company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this company")
    
    db_company = await company_crud.get(db, id=company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    updated_company = await company_crud.update(db, db_obj=db_company, obj_in=company_in)
    return updated_company

@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a company (admin only)."""
    # Additional authorization check would be needed here
    db_company = await company_crud.get(db, id=company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    await company_crud.remove(db, id=company_id)
    return {"message": "Company deleted successfully"}

@router.get("/industries/list")
async def get_industries():
    """Get list of available industries."""
    return [
        {"value": "technology", "label": "Technology"},
        {"value": "healthcare", "label": "Healthcare"},
        {"value": "finance", "label": "Finance"},
        {"value": "education", "label": "Education"},
        {"value": "manufacturing", "label": "Manufacturing"},
        {"value": "retail", "label": "Retail"},
        {"value": "consulting", "label": "Consulting"},
        {"value": "real_estate", "label": "Real Estate"},
        {"value": "other", "label": "Other"}
    ]

@router.get("/sizes/list")
async def get_company_sizes():
    """Get list of available company sizes."""
    return [
        {"value": "startup", "label": "Startup (1-10)"},
        {"value": "small", "label": "Small (11-50)"},
        {"value": "medium", "label": "Medium (51-200)"},
        {"value": "large", "label": "Large (201-1000)"},
        {"value": "enterprise", "label": "Enterprise (1000+)"}
    ]

@router.get("/{company_id}/stats")
async def get_company_stats(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get company statistics."""
    if company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this company's stats")
    
    stats = await company_crud.get_company_stats(db, company_id=company_id)
    return stats

@router.post("/{company_id}/settings")
async def update_company_settings(
    company_id: int,
    settings: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update company settings."""
    if company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this company's settings")
    
    await company_crud.update_settings(db, company_id=company_id, settings=settings)
    return {"message": "Settings updated successfully"}

@router.get("/{company_id}/settings")
async def get_company_settings(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get company settings."""
    if company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this company's settings")
    
    settings = await company_crud.get_settings(db, company_id=company_id)
    return settings
