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
from app.models.expense import Expense, ExpensePolicy, Project
from app.models.asset import Asset, AssetAssignment, AssetMaintenance
from app.models.performance import Performance, PerformanceGoal, PerformanceTemplate
from app.models.benefits import EmployeeBenefitPlan, BenefitEnrollment, BenefitDependent, BenefitOpenEnrollment
from app.models.document import Document, DocumentAcknowledgment, DocumentSignature, DocumentTemplate, DocumentFolder
from app.models.onboarding import OnboardingChecklist, OnboardingTask, OnboardingTemplate, OnboardingTemplateTask, OnboardingProgress
from app.models.compliance import ComplianceRequirement, ComplianceAssessment, ComplianceActionItem, ComplianceTraining, ComplianceTrainingEnrollment

__all__ = [
    # User Management
    "User",
    
    # Company & Organization
    "Company", 
    "CompanyUser",
    "Department",
    
    # Employee Management
    "Employee",
    "EmployeeDocument", 
    
    # Attendance & Time
    "Attendance",
    "AttendancePunch",
    "Shift",
    "Holiday",
    
    # Payroll
    "Payroll",
    "PayrollEmployee", 
    "PayrollComponent",
    "SalaryStructure",
    "PayslipTemplate",
    
    # Leave Management
    "Leave",
    "LeaveBalance",
    "LeavePolicy",
    
    # Expense Management
    "Expense",
    "ExpensePolicy",
    "Project",
    
    # Asset Management
    "Asset",
    "AssetAssignment",
    "AssetMaintenance",
    
    # Performance Management
    "Performance",
    "PerformanceGoal",
    "PerformanceTemplate",
    
    # Benefits Administration
    "EmployeeBenefitPlan",
    "BenefitEnrollment",
    "BenefitDependent",
    "BenefitOpenEnrollment",
    
    # Document Management
    "Document",
    "DocumentAcknowledgment",
    "DocumentSignature",
    "DocumentTemplate",
    "DocumentFolder",
    
    # Onboarding
    "OnboardingChecklist",
    "OnboardingTask",
    "OnboardingTemplate",
    "OnboardingTemplateTask",
    "OnboardingProgress",
    
    # Compliance
    "ComplianceRequirement",
    "ComplianceAssessment",
    "ComplianceActionItem",
    "ComplianceTraining",
    "ComplianceTrainingEnrollment",
]
