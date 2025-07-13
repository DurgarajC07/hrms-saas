"""
HRMS Application Package Initialization
"""

# Import all models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.company import Company, CompanyUser, Department
from app.models.employee import Employee, EmployeeDocument
from app.models.attendance import Attendance, AttendancePunch, Shift, Holiday
from app.models.payroll import Payroll, PayrollEmployee, PayrollComponent, SalaryStructure, PayslipTemplate
from app.models.leave import Leave, LeaveBalance, LeavePolicy

__all__ = [
    "User",
    "Company", 
    "CompanyUser",
    "Department",
    "Employee",
    "EmployeeDocument", 
    "Attendance",
    "AttendancePunch",
    "Shift",
    "Holiday",
    "Payroll",
    "PayrollEmployee", 
    "PayrollComponent",
    "SalaryStructure",
    "PayslipTemplate",
    "Leave",
    "LeaveBalance",
    "LeavePolicy"
]
