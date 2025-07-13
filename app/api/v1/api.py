from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, performance, attendance, expenses, benefits,
    users, companies, employees, payroll, leave, assets, documents,
    reports, dashboard, onboarding, compliance
)

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# User management
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Company management
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])

# Employee management
api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])

# Attendance management
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])

# Payroll management
api_router.include_router(payroll.router, prefix="/payroll", tags=["Payroll"])

# Leave management
api_router.include_router(leave.router, prefix="/leave", tags=["Leave Management"])

# Performance management
api_router.include_router(performance.router, prefix="/performance", tags=["Performance"])

# Asset management
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])

# Document management
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])

# Reports and analytics
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

# Dashboard
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# Onboarding
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])

# Compliance
api_router.include_router(compliance.router, prefix="/compliance", tags=["Compliance"])

# Expense management
api_router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])

# Benefits administration
api_router.include_router(benefits.router, prefix="/benefits", tags=["Benefits"])
