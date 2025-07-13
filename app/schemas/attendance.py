from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class PunchType(str, Enum):
    PUNCH_IN = "punch_in"
    PUNCH_OUT = "punch_out"
    BREAK_START = "break_start"
    BREAK_END = "break_end"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    ON_LEAVE = "on_leave"
    HOLIDAY = "holiday"
    WEEKEND = "weekend"


class PunchRequest(BaseModel):
    punch_type: PunchType
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    
    @validator('latitude')
    def validate_latitude(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError('Longitude must be between -180 and 180')
        return v


class PunchResponse(BaseModel):
    success: bool
    message: str
    punch_time: datetime
    location_valid: bool


class AttendanceCreate(BaseModel):
    employee_id: int
    date: date
    punch_in_time: Optional[datetime] = None
    punch_out_time: Optional[datetime] = None
    status: AttendanceStatus = AttendanceStatus.PRESENT


class AttendanceUpdate(BaseModel):
    attendance_id: int
    manual_punch_in: Optional[datetime] = None
    manual_punch_out: Optional[datetime] = None
    adjustment_reason: str
    status: Optional[AttendanceStatus] = None


class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    date: date
    punch_in_time: Optional[datetime]
    punch_out_time: Optional[datetime]
    total_hours: Optional[Decimal]
    overtime_hours: Optional[Decimal]
    status: AttendanceStatus
    is_late: bool
    late_minutes: int
    early_departure: bool
    early_departure_minutes: int
    
    class Config:
        from_attributes = True


class AttendanceList(BaseModel):
    items: List[AttendanceResponse]
    total: int
    page: int
    size: int
    pages: int


class AttendanceStatistics(BaseModel):
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    half_days: int
    leave_days: int
    total_hours: Decimal
    overtime_hours: Decimal
    average_hours_per_day: Decimal
    punctuality_percentage: float
