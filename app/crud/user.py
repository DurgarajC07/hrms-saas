from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.crud.base import CRUDBase
from app.models.user import User
from app.models.employee import Employee
from app.schemas.auth import UserRegister
from app.core.security import verify_password, get_password_hash
from typing import Optional
from datetime import datetime


class CRUDUser(CRUDBase[User, UserRegister, dict]):
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().first()
    
    async def create(self, db: AsyncSession, *, obj_in: UserRegister) -> User:
        """Create new user with hashed password"""
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            phone=obj_in.phone,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def update_last_login(self, db: AsyncSession, *, user_id: int) -> User:
        """Update user's last login timestamp"""
        user = await self.get(db, id=user_id)
        if user:
            user.last_login = datetime.utcnow()
            user.failed_login_attempts = 0  # Reset failed attempts on successful login
            await db.commit()
            await db.refresh(user)
        return user
    
    async def increment_failed_login(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Increment failed login attempts"""
        user = await self.get_by_email(db, email=email)
        if user:
            user.failed_login_attempts += 1
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            await db.commit()
            await db.refresh(user)
        return user
    
    async def is_active(self, user: User) -> bool:
        """Check if user is active"""
        return user.status == "active"
    
    async def is_superuser(self, user: User) -> bool:
        """Check if user is superuser"""
        return user.role == "super_admin"


class CRUDEmployee(CRUDBase[Employee, dict, dict]):
    
    async def get_by_user_id(self, db: AsyncSession, *, user_id: int) -> Optional[Employee]:
        """Get employee by user ID"""
        result = await db.execute(select(Employee).where(Employee.user_id == user_id))
        return result.scalars().first()
    
    async def get_by_employee_id(
        self, db: AsyncSession, *, company_id: int, employee_id: str
    ) -> Optional[Employee]:
        """Get employee by company-specific employee ID"""
        result = await db.execute(
            select(Employee).where(
                and_(
                    Employee.company_id == company_id,
                    Employee.employee_id == employee_id
                )
            )
        )
        return result.scalars().first()
    
    async def get_company_employees(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        department_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """Get employees by company with optional filters"""
        query = select(Employee).where(Employee.company_id == company_id)
        
        if department_id:
            query = query.where(Employee.department_id == department_id)
        
        if status:
            query = query.where(Employee.status == status)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


user_crud = CRUDUser(User)
employee_crud = CRUDEmployee(Employee)
