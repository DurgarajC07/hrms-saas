#!/usr/bin/env python3
"""
HRMS Setup and Initialization Script
This script sets up the HRMS application with sample data
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import AsyncSessionLocal, init_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole, UserStatus
from app.models.company import Company, CompanySize, Industry, CompanyStatus
from app.models.employee import Employee, EmployeeType, EmployeeStatus, Gender
from sqlalchemy import select
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_super_admin():
    """Create initial super admin user"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if super admin already exists
            result = await db.execute(
                select(User).where(User.role == UserRole.SUPER_ADMIN)
            )
            existing_admin = result.scalars().first()
            
            if existing_admin:
                logger.info("Super admin already exists")
                return existing_admin
            
            # Create super admin
            super_admin = User(
                email="admin@hrms.com",
                username="superadmin",
                hashed_password=get_password_hash("SuperAdmin123!"),
                first_name="Super",
                last_name="Admin",
                role=UserRole.SUPER_ADMIN,
                status=UserStatus.ACTIVE,
                email_verified=True
            )
            
            db.add(super_admin)
            await db.commit()
            await db.refresh(super_admin)
            
            logger.info("Super admin created successfully")
            return super_admin
            
        except Exception as e:
            logger.error(f"Error creating super admin: {e}")
            await db.rollback()
            raise


async def create_sample_company():
    """Create a sample company for testing"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if sample company exists
            result = await db.execute(
                select(Company).where(Company.name == "TechCorp Inc.")
            )
            existing_company = result.scalars().first()
            
            if existing_company:
                logger.info("Sample company already exists")
                return existing_company
            
            # Create sample company
            company = Company(
                name="TechCorp Inc.",
                legal_name="TechCorp Incorporated",
                registration_number="TC123456789",
                tax_id="TAX123456789",
                industry=Industry.TECHNOLOGY,
                company_size=CompanySize.MEDIUM,
                status=CompanyStatus.ACTIVE,
                email="info@techcorp.com",
                phone="+1-555-0123",
                website="https://techcorp.com",
                address_line1="123 Tech Street",
                city="San Francisco",
                state="California",
                country="United States",
                postal_code="94105",
                latitude=37.7749,
                longitude=-122.4194,
                punch_radius=100,
                timezone="America/Los_Angeles",
                currency="USD",
                max_employees=500,
                subscription_plan="enterprise"
            )
            
            db.add(company)
            await db.commit()
            await db.refresh(company)
            
            logger.info("Sample company created successfully")
            return company
            
        except Exception as e:
            logger.error(f"Error creating sample company: {e}")
            await db.rollback()
            raise


async def create_sample_users():
    """Create sample users and employees"""
    async with AsyncSessionLocal() as db:
        try:
            # Get sample company
            result = await db.execute(
                select(Company).where(Company.name == "TechCorp Inc.")
            )
            company = result.scalars().first()
            
            if not company:
                logger.error("Sample company not found")
                return
            
            # Sample users data
            sample_users = [
                {
                    "email": "hr@techcorp.com",
                    "username": "hrmanager",
                    "password": "HRManager123!",
                    "first_name": "Alice",
                    "last_name": "Johnson",
                    "role": UserRole.HR_MANAGER,
                    "job_title": "HR Manager",
                    "employee_type": EmployeeType.FULL_TIME
                },
                {
                    "email": "john.doe@techcorp.com",
                    "username": "johndoe",
                    "password": "Employee123!",
                    "first_name": "John",
                    "last_name": "Doe",
                    "role": UserRole.EMPLOYEE,
                    "job_title": "Software Engineer",
                    "employee_type": EmployeeType.FULL_TIME
                },
                {
                    "email": "jane.smith@techcorp.com",
                    "username": "janesmith",
                    "password": "Employee123!",
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "role": UserRole.EMPLOYEE,
                    "job_title": "Product Manager",
                    "employee_type": EmployeeType.FULL_TIME
                }
            ]
            
            for user_data in sample_users:
                # Check if user already exists
                result = await db.execute(
                    select(User).where(User.email == user_data["email"])
                )
                existing_user = result.scalars().first()
                
                if existing_user:
                    logger.info(f"User {user_data['email']} already exists")
                    continue
                
                # Create user
                user = User(
                    email=user_data["email"],
                    username=user_data["username"],
                    hashed_password=get_password_hash(user_data["password"]),
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=user_data["role"],
                    status=UserStatus.ACTIVE,
                    email_verified=True
                )
                
                db.add(user)
                await db.flush()  # Get user ID
                
                # Create employee record
                from app.core.security import generate_employee_id
                employee = Employee(
                    company_id=company.id,
                    user_id=user.id,
                    employee_id=generate_employee_id(company.id),
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    work_email=user_data["email"],
                    employee_type=user_data["employee_type"],
                    status=EmployeeStatus.ACTIVE,
                    hire_date="2024-01-01",
                    job_title=user_data["job_title"],
                    base_salary=75000.00
                )
                
                db.add(employee)
                
                logger.info(f"Created user and employee: {user_data['email']}")
            
            await db.commit()
            logger.info("Sample users created successfully")
            
        except Exception as e:
            logger.error(f"Error creating sample users: {e}")
            await db.rollback()
            raise


async def main():
    """Main setup function"""
    try:
        logger.info("Starting HRMS setup...")
        
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Create super admin
        await create_super_admin()
        
        # Create sample company
        await create_sample_company()
        
        # Create sample users
        await create_sample_users()
        
        logger.info("HRMS setup completed successfully!")
        
        print("\n" + "="*50)
        print("HRMS Setup Complete!")
        print("="*50)
        print("Super Admin Credentials:")
        print("Email: admin@hrms.com")
        print("Password: SuperAdmin123!")
        print("\nSample HR Manager:")
        print("Email: hr@techcorp.com")
        print("Password: HRManager123!")
        print("\nSample Employee:")
        print("Email: john.doe@techcorp.com")
        print("Password: Employee123!")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
