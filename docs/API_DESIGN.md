# API Design

## Overview

The backend exposes a RESTful JSON API. All endpoints are prefixed with `/api/v1`. Every request to a protected route must include a valid JWT access token in the `Authorization` header.

---

## Base URL

```
Development:  http://localhost:5000/api/v1
Production:   https://api.platform.com/api/v1
```

---

## Authentication Header

```
Authorization: Bearer <access_token>
```

---

## Standard Response Format

All responses follow this structure:

```json
// Success
{
  "success": true,
  "message": "Contacts fetched successfully",
  "data": { ... }
}

// Error
{
  "success": false,
  "message": "You do not have permission to perform this action",
  "error": "FORBIDDEN"
}

// Paginated List
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

---

## Auth Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/auth/register` | Register new user + create tenant | No |
| POST | `/auth/login` | Login, returns access + refresh token | No |
| POST | `/auth/logout` | Invalidate refresh token | Yes |
| POST | `/auth/refresh` | Get new access token using refresh token | No (cookie) |
| POST | `/auth/verify-email` | Verify email with token | No |
| POST | `/auth/forgot-password` | Send password reset email | No |
| POST | `/auth/reset-password` | Reset password with token | No |

### POST /auth/register

```json
// Request
{
  "full_name": "John Doe",
  "email": "john@acme.com",
  "password": "SecurePass123!",
  "workspace_name": "Acme Corp",
  "workspace_slug": "acme"
}

// Response 201
{
  "success": true,
  "message": "Account created. Please verify your email.",
  "data": {
    "user_id": "uuid",
    "tenant_slug": "acme"
  }
}
```

### POST /auth/login

```json
// Request
{
  "email": "john@acme.com",
  "password": "SecurePass123!"
}

// Response 200
{
  "success": true,
  "data": {
    "access_token": "eyJhbGci...",
    "user": {
      "id": "uuid",
      "full_name": "John Doe",
      "email": "john@acme.com"
    },
    "tenant": {
      "id": "uuid",
      "name": "Acme Corp",
      "slug": "acme",
      "plan": "free"
    }
  }
}
```

---

## Tenant / Workspace Endpoints

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/workspace` | Get current tenant info | Any |
| PATCH | `/workspace` | Update workspace name/settings | Owner, Admin |
| GET | `/workspace/members` | List all members | Any |
| POST | `/workspace/invite` | Invite a user by email | Owner, Admin |
| PATCH | `/workspace/members/:userId/role` | Change a member's role | Owner, Admin |
| DELETE | `/workspace/members/:userId` | Remove a member | Owner, Admin |
| GET | `/workspace/modules` | List all modules and their status | Any |
| POST | `/workspace/modules/:moduleKey/activate` | Activate a module | Owner, Admin |
| POST | `/workspace/modules/:moduleKey/deactivate` | Deactivate a module | Owner |

---

## CRM Endpoints

All routes require CRM module to be active for the tenant.

### Contacts

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/crm/contacts` | List contacts (paginated, filterable) | Any |
| POST | `/crm/contacts` | Create a new contact | Staff+ |
| GET | `/crm/contacts/:id` | Get single contact | Any |
| PATCH | `/crm/contacts/:id` | Update contact | Staff+ |
| DELETE | `/crm/contacts/:id` | Delete contact | Manager+ |

### Deals

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/crm/deals` | List deals | Any |
| POST | `/crm/deals` | Create a deal | Staff+ |
| GET | `/crm/deals/:id` | Get single deal | Any |
| PATCH | `/crm/deals/:id` | Update deal | Staff+ |
| DELETE | `/crm/deals/:id` | Delete deal | Manager+ |
| GET | `/crm/pipeline` | Get deals grouped by stage | Any |

### Activities

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/crm/activities` | List activities | Any |
| POST | `/crm/activities` | Log an activity | Staff+ |

---

## Inventory Endpoints

### Products

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/inventory/products` | List products | Any |
| POST | `/inventory/products` | Create product | Manager+ |
| GET | `/inventory/products/:id` | Get product | Any |
| PATCH | `/inventory/products/:id` | Update product | Manager+ |
| DELETE | `/inventory/products/:id` | Delete product | Admin+ |
| GET | `/inventory/products/low-stock` | Products below reorder level | Any |

### Orders

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/inventory/orders` | List orders | Any |
| POST | `/inventory/orders` | Create order | Staff+ |
| GET | `/inventory/orders/:id` | Get order details | Any |
| PATCH | `/inventory/orders/:id/status` | Update order status | Manager+ |

### Suppliers

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/inventory/suppliers` | List suppliers | Any |
| POST | `/inventory/suppliers` | Add supplier | Manager+ |
| PATCH | `/inventory/suppliers/:id` | Update supplier | Manager+ |
| DELETE | `/inventory/suppliers/:id` | Delete supplier | Admin+ |

---

## HRMS Endpoints

### Employees

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/hrms/employees` | List employees | Any |
| POST | `/hrms/employees` | Add employee | Admin+ |
| GET | `/hrms/employees/:id` | Get employee profile | Any |
| PATCH | `/hrms/employees/:id` | Update employee | Admin+ |
| DELETE | `/hrms/employees/:id` | Deactivate employee | Admin+ |

### Attendance

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| POST | `/hrms/attendance/check-in` | Employee check-in | Staff+ |
| POST | `/hrms/attendance/check-out` | Employee check-out | Staff+ |
| GET | `/hrms/attendance` | Get attendance records | Manager+ |
| GET | `/hrms/attendance/my` | Get own attendance | Any |

### Leave

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/hrms/leaves` | List all leave requests | Manager+ |
| POST | `/hrms/leaves` | Submit leave request | Staff+ |
| GET | `/hrms/leaves/my` | Get own leave requests | Any |
| PATCH | `/hrms/leaves/:id/approve` | Approve leave | Manager+ |
| PATCH | `/hrms/leaves/:id/reject` | Reject leave | Manager+ |

---

## HelpDesk Endpoints

### Tickets

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/helpdesk/tickets` | List tickets | Any |
| POST | `/helpdesk/tickets` | Create ticket | Any |
| GET | `/helpdesk/tickets/:id` | Get ticket + comments | Any |
| PATCH | `/helpdesk/tickets/:id` | Update ticket | Staff+ |
| PATCH | `/helpdesk/tickets/:id/assign` | Assign ticket to agent | Manager+ |
| PATCH | `/helpdesk/tickets/:id/status` | Change ticket status | Staff+ |

### Comments

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| POST | `/helpdesk/tickets/:id/comments` | Add comment/reply | Any |
| GET | `/helpdesk/tickets/:id/comments` | Get all comments | Any |

---

## Query Parameters (Common)

Most list endpoints support these query parameters:

```
GET /crm/contacts?page=1&limit=20&search=john&sort=created_at&order=desc

page     → page number (default: 1)
limit    → items per page (default: 20, max: 100)
search   → search term (searches name, email, etc.)
sort     → field to sort by
order    → asc | desc
```

---

## HTTP Status Codes Used

| Code | Meaning |
|---|---|
| 200 | OK — successful GET, PATCH |
| 201 | Created — successful POST |
| 204 | No Content — successful DELETE |
| 400 | Bad Request — validation error |
| 401 | Unauthorized — missing or invalid token |
| 403 | Forbidden — valid token but insufficient role |
| 404 | Not Found — resource doesn't exist |
| 409 | Conflict — duplicate entry (e.g., slug already taken) |
| 500 | Internal Server Error |
