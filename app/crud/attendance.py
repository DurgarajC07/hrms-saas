from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.crud.base import CRUDBase
from app.models.attendance import Attendance, AttendancePunch, PunchType
from app.models.employee import Employee
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate
import logging

logger = logging.getLogger(__name__)


class CRUDAttendance(CRUDBase[Attendance, AttendanceCreate, AttendanceUpdate]):
    
    async def process_punch(
        self,
        db: AsyncSession,
        *,
        employee_id: int,
        punch_type: PunchType,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AttendancePunch:
        """Process punch in/out with validation"""
        
        punch_time = datetime.utcnow()
        today = punch_time.date()
        
        # Get or create today's attendance record
        attendance = await self.get_attendance_by_date(db, employee_id=employee_id, date=today)
        if not attendance:
            attendance = Attendance(
                employee_id=employee_id,
                date=today,
                company_id=1  # This should come from employee's company
            )
            db.add(attendance)
            await db.flush()
        
        # Create punch record
        punch = AttendancePunch(
            attendance_id=attendance.id,
            employee_id=employee_id,
            punch_type=punch_type,
            punch_time=punch_time,
            latitude=latitude,
            longitude=longitude,
            device_info=device_info,
            ip_address=ip_address,
            is_valid_location=True  # Location validation would be done in the calling function
        )
        db.add(punch)
        
        # Update attendance record based on punch type
        if punch_type == PunchType.PUNCH_IN:
            if not attendance.punch_in_time:
                attendance.punch_in_time = punch_time
                attendance.punch_in_latitude = latitude
                attendance.punch_in_longitude = longitude
        elif punch_type == PunchType.PUNCH_OUT:
            attendance.punch_out_time = punch_time
            attendance.punch_out_latitude = latitude
            attendance.punch_out_longitude = longitude
            
            # Calculate total hours if both punch in/out exist
            if attendance.punch_in_time:
                time_diff = punch_time - attendance.punch_in_time
                attendance.total_hours = Decimal(str(time_diff.total_seconds() / 3600))
        
        await db.commit()
        await db.refresh(punch)
        
        return punch
    
    async def get_attendance_by_date(
        self, 
        db: AsyncSession, 
        *, 
        employee_id: int, 
        date: date
    ) -> Optional[Attendance]:
        """Get attendance record for specific employee and date"""
        result = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.employee_id == employee_id,
                    Attendance.date == date
                )
            )
        )
        return result.scalars().first()
    
    async def get_employee_attendance(
        self,
        db: AsyncSession,
        *,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Attendance]:
        """Get attendance records for an employee within date range"""
        query = select(Attendance).where(Attendance.employee_id == employee_id)
        
        if start_date:
            query = query.where(Attendance.date >= start_date)
        if end_date:
            query = query.where(Attendance.date <= end_date)
        
        query = query.order_by(Attendance.date.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_team_attendance(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        date_filter: date,
        department_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get team attendance for a specific date"""
        query = select(
            Attendance,
            Employee.first_name,
            Employee.last_name,
            Employee.employee_id,
            Employee.job_title
        ).join(
            Employee, Attendance.employee_id == Employee.id
        ).where(
            and_(
                Employee.company_id == company_id,
                Attendance.date == date_filter
            )
        )
        
        if department_id:
            query = query.where(Employee.department_id == department_id)
        
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        records = result.all()
        
        team_attendance = []
        for record in records:
            attendance, first_name, last_name, emp_id, job_title = record
            team_attendance.append({
                "employee_id": attendance.employee_id,
                "employee_name": f"{first_name} {last_name}",
                "employee_code": emp_id,
                "job_title": job_title,
                "date": attendance.date,
                "punch_in_time": attendance.punch_in_time,
                "punch_out_time": attendance.punch_out_time,
                "total_hours": attendance.total_hours,
                "status": attendance.status,
                "is_late": attendance.is_late,
                "late_minutes": attendance.late_minutes
            })
        
        return team_attendance
    
    async def manual_adjustment(
        self,
        db: AsyncSession,
        *,
        attendance_id: int,
        adjustment_data: AttendanceUpdate,
        adjusted_by: int
    ) -> Attendance:
        """Manual attendance adjustment by HR/Manager"""
        attendance = await self.get(db, id=attendance_id)
        if not attendance:
            raise ValueError("Attendance record not found")
        
        # Update manual times
        attendance.manual_punch_in = adjustment_data.manual_punch_in
        attendance.manual_punch_out = adjustment_data.manual_punch_out
        attendance.adjusted_by = adjusted_by
        attendance.adjustment_reason = adjustment_data.adjustment_reason
        attendance.adjustment_date = datetime.utcnow()
        attendance.requires_approval = True
        
        if adjustment_data.status:
            attendance.status = adjustment_data.status
        
        # Recalculate hours if both manual times are provided
        if attendance.manual_punch_in and attendance.manual_punch_out:
            time_diff = attendance.manual_punch_out - attendance.manual_punch_in
            attendance.total_hours = Decimal(str(time_diff.total_seconds() / 3600))
        
        await db.commit()
        await db.refresh(attendance)
        
        return attendance
    
    async def get_attendance_statistics(
        self,
        db: AsyncSession,
        *,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get attendance statistics for an employee"""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Base query
        query = select(Attendance).where(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.date >= start_date,
                Attendance.date <= end_date
            )
        )
        
        result = await db.execute(query)
        records = result.scalars().all()
        
        # Calculate statistics
        total_days = len(records)
        present_days = len([r for r in records if r.status == "present"])
        absent_days = len([r for r in records if r.status == "absent"])
        late_days = len([r for r in records if r.is_late])
        half_days = len([r for r in records if r.status == "half_day"])
        leave_days = len([r for r in records if r.status == "on_leave"])
        
        total_hours = sum([r.total_hours or 0 for r in records])
        overtime_hours = sum([r.overtime_hours or 0 for r in records])
        
        avg_hours = total_hours / total_days if total_days > 0 else 0
        punctuality_percentage = ((total_days - late_days) / total_days * 100) if total_days > 0 else 0
        
        return {
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "late_days": late_days,
            "half_days": half_days,
            "leave_days": leave_days,
            "total_hours": total_hours,
            "overtime_hours": overtime_hours,
            "average_hours_per_day": avg_hours,
            "punctuality_percentage": round(punctuality_percentage, 2)
        }


attendance_crud = CRUDAttendance(Attendance)
