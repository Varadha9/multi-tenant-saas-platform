# System Architecture

## Overview

The platform follows a **3-tier architecture** with a clear separation between the presentation layer, business logic layer, and data layer. The entire system is designed around the concept of multi-tenancy — one running instance of the application serves multiple isolated business workspaces simultaneously.

---

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│                                                                 │
│   Browser (React.js SPA)      Mobile (Future - React Native)   │
│   acme.platform.com           beta.platform.com                │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────────────────┐
│                      API GATEWAY / NGINX                        │
│                                                                 │
│   - SSL Termination                                             │
│   - Subdomain routing (tenant slug extraction)                  │
│   - Rate limiting                                               │
│   - Load balancing (future)                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                     BACKEND API SERVER                          │
│                     (Node.js + Express)                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Auth         │  │ Tenant       │  │ Module Router        │  │
│  │ Middleware   │→ │ Middleware   │→ │ /api/crm/*           │  │
│  │ (JWT verify) │  │ (scope DB)   │  │ /api/inventory/*     │  │
│  └──────────────┘  └──────────────┘  │ /api/hrms/*          │  │
│                                      │ /api/helpdesk/*      │  │
│  ┌──────────────┐                    └──────────────────────┘  │
│  │ RBAC         │                                               │
│  │ Middleware   │                                               │
│  │ (role check) │                                               │
│  └──────────────┘                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
┌─────────▼──────┐ ┌─────▼──────┐ ┌───▼────────────┐
│  PostgreSQL    │ │   Redis    │ │   AWS S3       │
│  (Primary DB)  │ │  (Cache +  │ │  (File/Image   │
│                │ │  Sessions) │ │   Storage)     │
└────────────────┘ └────────────┘ └────────────────┘
```

---

## Multi-Tenancy Architecture

### Strategy: Shared Database, Shared Schema with Tenant ID

There are 3 common multi-tenancy strategies:

| Strategy | Description | Pros | Cons |
|---|---|---|---|
| Separate Database per Tenant | Each tenant gets their own DB | Maximum isolation | Very expensive, hard to manage |
| Separate Schema per Tenant | One DB, separate schemas | Good isolation | Schema migrations are complex |
| **Shared Schema with Tenant ID** | One DB, one schema, tenant_id column | Cost-effective, easy to scale | Requires strict query discipline |

We use **Shared Schema with Tenant ID** because:
- It's the most practical for an MVP and scales well
- PostgreSQL Row-Level Security (RLS) can enforce isolation at the DB level
- All major SaaS platforms (Notion, Linear, etc.) use this approach

### How Tenant Isolation Works

```
Every business data table has:
  tenant_id UUID NOT NULL REFERENCES tenants(id)

Backend middleware automatically injects tenant_id into every query:

  // Without middleware (WRONG - data leak risk)
  SELECT * FROM contacts;

  // With middleware (CORRECT)
  SELECT * FROM contacts WHERE tenant_id = 'uuid-from-jwt';
```

The `tenant_id` is extracted from the authenticated user's JWT token on every request. The middleware attaches it to `req.tenantId` and all service functions receive it as a required parameter.

---

## Request Lifecycle

```
1. Browser sends: GET acme.platform.com/api/crm/contacts
                  Authorization: Bearer <jwt_token>

2. Nginx extracts subdomain "acme", forwards to backend
   with header: X-Tenant-Slug: acme

3. Auth Middleware:
   - Verifies JWT signature
   - Extracts user_id, tenant_id, role from token payload
   - Attaches to req.user

4. Tenant Middleware:
   - Confirms tenant exists and is active
   - Confirms user belongs to this tenant
   - Attaches tenant config to req.tenant

5. RBAC Middleware:
   - Checks if user's role has permission for this route
   - e.g., Staff cannot DELETE contacts

6. Module Middleware:
   - Checks if CRM module is active for this tenant
   - Returns 403 if module not activated

7. Route Handler:
   - Calls ContactsService.getAll(req.tenantId)
   - Service queries: SELECT * FROM contacts WHERE tenant_id = $1

8. Response sent back to browser
```

---

## Frontend Architecture

```
src/
├── app/
│   ├── store.js              ← Redux store
│   └── router.jsx            ← React Router config
├── features/
│   ├── auth/                 ← Login, Register, Token refresh
│   ├── workspace/            ← Tenant setup, settings
│   ├── crm/                  ← CRM module pages + components
│   ├── inventory/            ← Inventory module
│   ├── hrms/                 ← HRMS module
│   └── helpdesk/             ← HelpDesk module
├── components/
│   ├── layout/               ← Sidebar, Navbar, Shell
│   └── ui/                   ← Buttons, Modals, Tables (shared)
└── hooks/                    ← useAuth, useTenant, useModules
```

The sidebar navigation is **dynamically rendered** based on which modules the tenant has activated. If a tenant hasn't activated HRMS, the HRMS link never appears and the route is protected.

---

## Backend Architecture

```
src/
├── server.js                 ← Express app entry point
├── middleware/
│   ├── auth.middleware.js    ← JWT verification
│   ├── tenant.middleware.js  ← Tenant scoping
│   ├── rbac.middleware.js    ← Role permission checks
│   └── module.middleware.js  ← Module activation checks
├── modules/
│   ├── auth/
│   ├── tenant/
│   ├── crm/
│   ├── inventory/
│   ├── hrms/
│   └── helpdesk/
│       ├── helpdesk.routes.js
│       ├── helpdesk.controller.js
│       └── helpdesk.service.js
├── config/
│   ├── db.js                 ← PostgreSQL connection pool
│   └── env.js                ← Environment variable validation
└── utils/
    ├── ApiError.js           ← Standardized error class
    └── ApiResponse.js        ← Standardized response wrapper
```

Each module follows the same **Routes → Controller → Service** pattern:
- Routes: define endpoints and attach middleware
- Controller: handle HTTP request/response, input validation
- Service: business logic, database queries

---

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│              AWS Cloud                  │
│                                         │
│  ┌──────────┐    ┌──────────────────┐   │
│  │  Route53 │───▶│  CloudFront CDN  │   │
│  │  (DNS)   │    │  (Static Assets) │   │
│  └──────────┘    └──────────────────┘   │
│                           │             │
│                  ┌────────▼──────────┐  │
│                  │   EC2 Instance    │  │
│                  │   Nginx + Node.js │  │
│                  └────────┬──────────┘  │
│                           │             │
│                  ┌────────▼──────────┐  │
│                  │   RDS PostgreSQL  │  │
│                  │   (Managed DB)    │  │
│                  └───────────────────┘  │
│                                         │
│  ┌──────────┐    ┌──────────────────┐   │
│  │   S3     │    │   SES (Email)    │   │
│  │ (Files)  │    │  (Invitations)   │   │
│  └──────────┘    └──────────────────┘   │
└─────────────────────────────────────────┘
```

---

## Scalability Considerations

Even though this is an MVP, the architecture is designed to scale:

- **Horizontal scaling**: The backend is stateless (JWT auth, no server-side sessions), so multiple instances can run behind a load balancer
- **Database connection pooling**: Using `pg-pool` to manage PostgreSQL connections efficiently
- **Caching**: Redis for caching tenant configs and frequently accessed data to reduce DB load
- **CDN**: Static frontend assets served via CDN, not the backend server
- **Background jobs**: Email sending, report generation moved to a job queue (Bull + Redis) to keep API responses fast
