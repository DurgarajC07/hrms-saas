# HRMS API Documentation

## Overview

The HRMS (Human Resource Management System) API is a comprehensive RESTful API built with FastAPI that provides all the functionality needed to manage human resources in an enterprise environment.

## Base URL

```
Production: https://api.hrms.com/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

### Authentication Endpoints

#### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Register

```http
POST /auth/register
Content-Type: application/json

{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

#### Refresh Token

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Logout

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

## Employee Management

### Get All Employees

```http
GET /employees?page=1&size=20&department_id=1&status=active
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `page` (int): Page number (default: 1)
- `size` (int): Items per page (default: 20, max: 100)
- `department_id` (int, optional): Filter by department
- `status` (string, optional): Filter by status (active, inactive, etc.)

### Get Employee Details

```http
GET /employees/{employee_id}
Authorization: Bearer <access_token>
```

### Create Employee

```http
POST /employees
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@company.com",
  "phone": "+1234567890",
  "employee_id": "EMP001",
  "department_id": 1,
  "job_title": "Software Engineer",
  "hire_date": "2024-01-15",
  "base_salary": 75000.00,
  "employee_type": "full_time"
}
```

### Update Employee

```http
PUT /employees/{employee_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "job_title": "Senior Software Engineer",
  "base_salary": 85000.00,
  "department_id": 2
}
```

## Attendance Management

### Punch In/Out

```http
POST /attendance/punch
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "punch_type": "punch_in",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "device_info": "iPhone 13",
  "ip_address": "192.168.1.100"
}
```

**Punch Types:**

- `punch_in`: Clock in for the day
- `punch_out`: Clock out for the day
- `break_start`: Start break
- `break_end`: End break

### Get My Attendance

```http
GET /attendance/my-attendance?start_date=2024-01-01&end_date=2024-01-31&page=1&size=20
Authorization: Bearer <access_token>
```

### Get Today's Status

```http
GET /attendance/today-status
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "date": "2024-01-15",
  "is_punched_in": true,
  "punch_in_time": "2024-01-15T09:00:00Z",
  "punch_out_time": null,
  "total_hours": 0,
  "status": "present"
}
```

### Get Team Attendance (Manager/HR)

```http
GET /attendance/team-attendance?date_filter=2024-01-15&department_id=1&page=1&size=50
Authorization: Bearer <access_token>
```

### Manual Attendance Adjustment (HR/Manager)

```http
POST /attendance/manual-adjustment
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "attendance_id": 123,
  "manual_punch_in": "2024-01-15T09:00:00Z",
  "manual_punch_out": "2024-01-15T18:00:00Z",
  "adjustment_reason": "System error correction",
  "status": "present"
}
```

### Get Attendance Statistics

```http
GET /attendance/statistics?employee_id=123&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <access_token>
```

## Payroll Management

### Get Payrolls

```http
GET /payroll?page=1&size=20&status=processed&year=2024&month=1
Authorization: Bearer <access_token>
```

### Generate Payroll

```http
POST /payroll/generate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "pay_period_start": "2024-01-01",
  "pay_period_end": "2024-01-31",
  "pay_date": "2024-02-01",
  "department_ids": [1, 2, 3],
  "employee_ids": [10, 20, 30]
}
```

### Get Payslips

```http
GET /payroll/{payroll_id}/payslips?employee_id=123
Authorization: Bearer <access_token>
```

### Process Payroll

```http
POST /payroll/{payroll_id}/process
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "approval_comments": "Approved for payment"
}
```

### Download Payslip

```http
GET /payroll/payslip/{payslip_id}/download
Authorization: Bearer <access_token>
```

## Leave Management

### Get Leave Requests

```http
GET /leave/requests?page=1&size=20&status=pending&leave_type=annual
Authorization: Bearer <access_token>
```

### Submit Leave Request

```http
POST /leave/request
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "leave_type": "annual",
  "start_date": "2024-02-01",
  "end_date": "2024-02-05",
  "days_requested": 5,
  "reason": "Family vacation",
  "coverage_by": 456
}
```

### Approve Leave

```http
PUT /leave/{leave_id}/approve
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "days_approved": 5,
  "comments": "Approved with full days"
}
```

### Reject Leave

```http
PUT /leave/{leave_id}/reject
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "rejection_reason": "Insufficient leave balance"
}
```

### Get Leave Balance

```http
GET /leave/balance?employee_id=123&year=2024
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "annual": {
    "allocated_days": 20,
    "used_days": 5,
    "pending_days": 2,
    "available_days": 13
  },
  "sick": {
    "allocated_days": 10,
    "used_days": 1,
    "pending_days": 0,
    "available_days": 9
  }
}
```

## Company Management

### Get Companies

```http
GET /companies?page=1&size=20
Authorization: Bearer <access_token>
```

### Create Company

```http
POST /companies
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "TechCorp Inc.",
  "legal_name": "TechCorp Incorporated",
  "email": "info@techcorp.com",
  "phone": "+1-555-0123",
  "industry": "technology",
  "company_size": "medium",
  "address_line1": "123 Tech Street",
  "city": "San Francisco",
  "state": "California",
  "country": "United States",
  "postal_code": "94105",
  "timezone": "America/Los_Angeles",
  "currency": "USD"
}
```

### Update Company

```http
PUT /companies/{company_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "TechCorp Industries",
  "phone": "+1-555-0124"
}
```

### Get Company Settings

```http
GET /companies/{company_id}/settings
Authorization: Bearer <access_token>
```

## Performance Management

### Get Performance Reviews

```http
GET /performance/reviews?page=1&size=20&employee_id=123&year=2024
Authorization: Bearer <access_token>
```

### Create Performance Review

```http
POST /performance/reviews
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "employee_id": 123,
  "reviewer_id": 456,
  "review_period_start": "2024-01-01",
  "review_period_end": "2024-06-30",
  "review_type": "mid_year",
  "goals": [
    {
      "title": "Complete Project X",
      "description": "Lead the development of Project X",
      "weight": 40,
      "target_date": "2024-06-01"
    }
  ]
}
```

### Submit Self Assessment

```http
POST /performance/reviews/{review_id}/self-assessment
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "achievements": "Successfully delivered 3 major projects",
  "challenges": "Remote team coordination",
  "goals_for_next_period": "Learn new technologies",
  "rating": 4
}
```

## Reports and Analytics

### Get Dashboard Data

```http
GET /dashboard/overview?company_id=1&date_range=last_30_days
Authorization: Bearer <access_token>
```

### Get Attendance Report

```http
GET /reports/attendance?start_date=2024-01-01&end_date=2024-01-31&department_id=1&format=json
Authorization: Bearer <access_token>
```

**Supported formats:** `json`, `csv`, `pdf`

### Get Payroll Report

```http
GET /reports/payroll?year=2024&month=1&department_id=1&format=pdf
Authorization: Bearer <access_token>
```

### Get Employee Report

```http
GET /reports/employees?department_id=1&status=active&format=csv
Authorization: Bearer <access_token>
```

## Error Responses

The API uses standard HTTP status codes and returns error details in JSON format:

```json
{
  "detail": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limits

- Authentication endpoints: 5 requests per minute
- General API endpoints: 100 requests per minute
- File upload endpoints: 10 requests per minute

## Pagination

List endpoints support pagination with the following parameters:

- `page`: Page number (starts from 1)
- `size`: Items per page (max 100)

Response includes pagination metadata:

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

## File Uploads

File uploads use multipart/form-data:

```http
POST /documents/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <binary_data>
document_type: "resume"
employee_id: 123
```

## WebSocket Support

Real-time updates for attendance and notifications:

```javascript
const ws = new WebSocket("wss://api.hrms.com/ws/notifications");
ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Notification:", data);
};
```

## SDK and Libraries

Official SDKs available for:

- JavaScript/TypeScript
- Python
- PHP
- Java
- C#

## Support

For API support:

- Documentation: https://docs.hrms.com
- Support Email: api-support@hrms.com
- GitHub Issues: https://github.com/hrms/api/issues
