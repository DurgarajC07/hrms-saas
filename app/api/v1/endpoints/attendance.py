from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, date
from geopy.distance import geodesic

from app.core.database import get_db
from app.core.config import settings
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.attendance import Attendance, AttendancePunch, PunchType
from app.schemas.attendance import (
    AttendanceCreate, AttendanceUpdate, AttendanceResponse,
    PunchRequest, PunchResponse, AttendanceList
)
from app.crud.attendance import attendance_crud
from app.crud.employee import employee_crud
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/punch", response_model=PunchResponse)
async def punch_in_out(
    punch_data: PunchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Punch in/out with location validation"""
    try:
        # Get employee record
        employee = await employee_crud.get_by_user_id(db, user_id=current_user.id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found"
            )
        
        # Validate location if coordinates provided
        if punch_data.latitude and punch_data.longitude:
            company_location = (settings.COMPANY_LATITUDE, settings.COMPANY_LONGITUDE)
            punch_location = (punch_data.latitude, punch_data.longitude)
            distance = geodesic(company_location, punch_location).meters
            
            if distance > settings.PUNCH_RADIUS_METERS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"You are {distance:.0f}m away from office. Must be within {settings.PUNCH_RADIUS_METERS}m"
                )
        
        # Process punch
        punch_result = await attendance_crud.process_punch(
            db,
            employee_id=employee.id,
            punch_type=punch_data.punch_type,
            latitude=punch_data.latitude,
            longitude=punch_data.longitude,
            device_info=punch_data.device_info,
            ip_address=punch_data.ip_address
        )
        
        logger.info(f"Punch {punch_data.punch_type} recorded for employee {employee.id}")
        
        return PunchResponse(
            success=True,
            message=f"Punch {punch_data.punch_type.replace('_', ' ')} recorded successfully",
            punch_time=punch_result.punch_time,
            location_valid=punch_result.is_valid_location
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Punch recording error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record punch"
        )


@router.get("/my-attendance", response_model=List[AttendanceResponse])
async def get_my_attendance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's attendance records"""
    try:
        # Get employee record
        employee = await employee_crud.get_by_user_id(db, user_id=current_user.id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found"
            )
        
        # Get attendance records
        attendance_records = await attendance_crud.get_employee_attendance(
            db,
            employee_id=employee.id,
            start_date=start_date,
            end_date=end_date,
            skip=(page - 1) * size,
            limit=size
        )
        
        return attendance_records
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get attendance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch attendance records"
        )


@router.get("/today-status")
async def get_today_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get today's attendance status"""
    try:
        # Get employee record
        employee = await employee_crud.get_by_user_id(db, user_id=current_user.id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found"
            )
        
        # Get today's attendance
        today = date.today()
        attendance = await attendance_crud.get_attendance_by_date(
            db, employee_id=employee.id, date=today
        )
        
        status = {
            "date": today,
            "is_punched_in": False,
            "punch_in_time": None,
            "punch_out_time": None,
            "total_hours": 0,
            "status": "absent"
        }
        
        if attendance:
            status.update({
                "is_punched_in": attendance.punch_in_time and not attendance.punch_out_time,
                "punch_in_time": attendance.punch_in_time,
                "punch_out_time": attendance.punch_out_time,
                "total_hours": float(attendance.total_hours or 0),
                "status": attendance.status
            })
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get today status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch today's status"
        )


@router.get("/team-attendance")
async def get_team_attendance(
    date_filter: Optional[date] = Query(None),
    department_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get team attendance (for managers/HR)"""
    try:
        # Check if user has permission to view team attendance
        if current_user.role not in ["hr_manager", "hr_executive", "manager", "company_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Get employee record to find company
        employee = await employee_crud.get_by_user_id(db, user_id=current_user.id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found"
            )
        
        # Get team attendance
        team_attendance = await attendance_crud.get_team_attendance(
            db,
            company_id=employee.company_id,
            date_filter=date_filter or date.today(),
            department_id=department_id,
            skip=(page - 1) * size,
            limit=size
        )
        
        return team_attendance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get team attendance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch team attendance"
        )


@router.post("/manual-adjustment")
async def manual_attendance_adjustment(
    adjustment_data: AttendanceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Manual attendance adjustment (HR/Manager only)"""
    try:
        # Check permissions
        if current_user.role not in ["hr_manager", "hr_executive", "company_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for manual adjustment"
            )
        
        # Update attendance record
        updated_attendance = await attendance_crud.manual_adjustment(
            db,
            attendance_id=adjustment_data.attendance_id,
            adjustment_data=adjustment_data,
            adjusted_by=current_user.id
        )
        
        logger.info(f"Manual attendance adjustment by user {current_user.id}")
        
        return {
            "message": "Attendance adjusted successfully",
            "attendance_id": updated_attendance.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual adjustment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to adjust attendance"
        )


@router.get("/statistics")
async def get_attendance_statistics(
    employee_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get attendance statistics"""
    try:
        # Get employee record
        employee = await employee_crud.get_by_user_id(db, user_id=current_user.id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found"
            )
        
        # If specific employee_id requested, check permissions
        target_employee_id = employee_id or employee.id
        if employee_id and employee_id != employee.id:
            if current_user.role not in ["hr_manager", "hr_executive", "manager", "company_admin"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
        
        # Get statistics
        stats = await attendance_crud.get_attendance_statistics(
            db,
            employee_id=target_employee_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch attendance statistics"
        )
