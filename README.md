# HRMS SaaS - Human Resource Management System

<div align="center">
  <h1>🏢 Enterprise HRMS SaaS Platform</h1>
  <p><strong>Comprehensive Human Resource Management System built with FastAPI</strong></p>
  
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI)](https://fastapi.tiangolo.com)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org)
  [![Redis](https://img.shields.io/badge/Redis-7.0+-DC382D.svg?style=flat&logo=redis)](https://redis.io)
  [![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker)](https://docker.com)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
</div>

A comprehensive, enterprise-grade Human Resource Management System built with FastAPI, designed to handle millions of users with all essential HR features.

## 🚀 Features

### Core Features

- **Employee Management** - Complete employee lifecycle management
- **Attendance Management** - GPS-based punch in/out with geofencing
- **Payroll Processing** - Automated payroll calculation with tax management
- **Leave Management** - Leave requests, approvals, and tracking
- **Performance Management** - Appraisals and performance tracking
- **Asset Management** - IT asset allocation and tracking
- **Document Management** - Secure document storage and management
- **Onboarding** - Streamlined employee onboarding process
- **Compliance Management** - Regulatory compliance tracking

### Advanced Features

- **Multi-tenant Architecture** - Support for multiple companies
- **Role-based Access Control** - Granular permission system
- **Real-time Analytics** - Comprehensive reporting and dashboards
- **Mobile API Support** - Full mobile app integration
- **Multi-currency Support** - Global payroll processing
- **Multi-language Support** - Internationalization ready
- **Biometric Integration** - Integration with biometric devices
- **Automated Workflows** - Customizable approval workflows

### Enterprise Features

- **Scalable Architecture** - Designed for millions of users
- **High Availability** - Redis caching and load balancing
- **Security** - JWT authentication, encryption, audit trails
- **Background Tasks** - Celery for async processing
- **Monitoring** - Structured logging and health checks
- **API Documentation** - Auto-generated OpenAPI docs

## 🏗️ Architecture

### Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with AsyncPG
- **Cache**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT with refresh tokens
- **Documentation**: OpenAPI/Swagger

### Database Design

- **Multi-tenant**: Company-based data isolation
- **Scalable**: Optimized indexes and queries
- **Audit Trail**: Complete audit logging
- **GDPR Compliant**: Data privacy and retention

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker (optional)

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd hrms
```

2. **Create virtual environment**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Environment setup**

```bash
copy .env.example .env
# Edit .env with your configuration
```

5. **Database setup**

```bash
# Create PostgreSQL database
createdb hrms_db

# Run setup script
python setup.py
```

6. **Start the application**

```bash
uvicorn main:app --reload
```

### Using Docker

1. **Start with Docker Compose**

```bash
docker-compose up -d
```

2. **Initialize database**

```bash
docker-compose exec hrms_api python setup.py
```

## 📖 API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🔐 Authentication

### Default Credentials

**Super Admin:**

- Email: admin@hrms.com
- Password: SuperAdmin123!

**HR Manager:**

- Email: hr@techcorp.com
- Password: HRManager123!

**Employee:**

- Email: john.doe@techcorp.com
- Password: Employee123!

### API Authentication

```bash
# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

# Use token in subsequent requests
Authorization: Bearer <access_token>
```

## 📱 Core API Endpoints

### Authentication

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - User logout

### Employee Management

- `GET /api/v1/employees` - List employees
- `POST /api/v1/employees` - Create employee
- `GET /api/v1/employees/{id}` - Get employee details
- `PUT /api/v1/employees/{id}` - Update employee
- `DELETE /api/v1/employees/{id}` - Delete employee

### Attendance

- `POST /api/v1/attendance/punch` - Punch in/out
- `GET /api/v1/attendance/my-attendance` - Get my attendance
- `GET /api/v1/attendance/today-status` - Today's status
- `GET /api/v1/attendance/team-attendance` - Team attendance

### Payroll

- `GET /api/v1/payroll` - List payrolls
- `POST /api/v1/payroll/generate` - Generate payroll
- `GET /api/v1/payroll/{id}/payslips` - Get payslips
- `POST /api/v1/payroll/{id}/process` - Process payroll

### Leave Management

- `GET /api/v1/leave/requests` - List leave requests
- `POST /api/v1/leave/request` - Submit leave request
- `PUT /api/v1/leave/{id}/approve` - Approve leave
- `PUT /api/v1/leave/{id}/reject` - Reject leave

## 🏢 Multi-tenant Usage

### Company Context

Include company ID in requests:

```bash
# Via header
X-Company-ID: 1

# Via subdomain
company1.hrms.com
```

### Company Management

- `POST /api/v1/companies` - Create company
- `GET /api/v1/companies` - List companies
- `PUT /api/v1/companies/{id}` - Update company
- `GET /api/v1/companies/{id}/settings` - Company settings

## 📊 Features in Detail

### GPS-based Attendance

- **Geofencing**: Configurable radius-based validation
- **Location Tracking**: GPS coordinates for punch records
- **Offline Support**: Queue punches when offline
- **Fraud Prevention**: Multiple validation layers

### Payroll Processing

- **Automated Calculation**: Rule-based salary computation
- **Tax Management**: Multi-jurisdiction tax support
- **Compliance**: Statutory compliance (PF, ESI, etc.)
- **Multi-currency**: Global payroll processing
- **Payslip Generation**: PDF payslip generation

### Performance Management

- **Goal Setting**: SMART goals framework
- **360° Reviews**: Multi-source feedback
- **Continuous Feedback**: Real-time performance tracking
- **Career Development**: Growth path planning

### Compliance & Security

- **Data Encryption**: AES-256 encryption at rest
- **Audit Trails**: Complete user activity logging
- **GDPR Compliance**: Data privacy and right to be forgotten
- **Role-based Security**: Granular access control

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/hrms_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_BUCKET_NAME=hrms-files

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password
```

### Company Settings

- Timezone configuration
- Currency settings
- Payroll frequency
- Working hours and shifts
- Holiday calendar
- Leave policies

## 📈 Performance & Scalability

### Database Optimization

- **Connection Pooling**: Async connection management
- **Indexing**: Optimized database indexes
- **Query Optimization**: Efficient SQL queries
- **Partitioning**: Table partitioning for large datasets

### Caching Strategy

- **Redis Caching**: Application-level caching
- **Session Management**: Token-based sessions
- **Rate Limiting**: API rate limiting
- **CDN Integration**: Static file delivery

### Monitoring

- **Health Checks**: Application health monitoring
- **Metrics**: Performance metrics collection
- **Logging**: Structured logging with request tracing
- **Alerting**: Error and performance alerting

## 🚀 Deployment

### Production Deployment

```bash
# Docker production
docker-compose -f docker-compose.prod.yml up -d

# Or with Kubernetes
kubectl apply -f k8s/
```

### Load Balancing

- Nginx reverse proxy
- Multiple application instances
- Database read replicas
- Redis clustering

### Security Checklist

- [ ] SSL/TLS encryption
- [ ] Database encryption
- [ ] API rate limiting
- [ ] Security headers
- [ ] Regular backups
- [ ] Monitoring and alerting

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Email: support@hrms.com
- Documentation: https://docs.hrms.com

## 🔄 Version History

### v1.0.0 (Current)

- Initial release with core HRMS features
- Multi-tenant architecture
- GPS-based attendance
- Comprehensive payroll system
- Performance management
- Mobile API support

---

**Built with ❤️ for modern HR teams**
