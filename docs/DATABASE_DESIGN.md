# Database Design

## Overview

We use **PostgreSQL** as our primary database. The schema is designed around a shared-schema multi-tenancy model where every business data table is scoped by a `tenant_id` foreign key.

---

## Core Schema

### tenants

The root table. Every business that signs up creates one row here.

```sql
CREATE TABLE tenants (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          VARCHAR(255) NOT NULL,
  slug          VARCHAR(100) UNIQUE NOT NULL,  -- used in subdomain: slug.platform.com
  plan          VARCHAR(50) DEFAULT 'free',    -- free | starter | pro | enterprise
  is_active     BOOLEAN DEFAULT true,
  created_at    TIMESTAMP DEFAULT NOW(),
  updated_at    TIMESTAMP DEFAULT NOW()
);
```

### users

Platform-level user accounts. One user can belong to multiple tenants (e.g., a consultant working for two companies).

```sql
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name     VARCHAR(255) NOT NULL,
  avatar_url    TEXT,
  is_verified   BOOLEAN DEFAULT false,
  created_at    TIMESTAMP DEFAULT NOW(),
  updated_at    TIMESTAMP DEFAULT NOW()
);
```

### tenant_members

The join table that connects users to tenants and assigns their role within that tenant.

```sql
CREATE TABLE tenant_members (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role        VARCHAR(50) NOT NULL DEFAULT 'staff',  -- owner | admin | manager | staff
  is_active   BOOLEAN DEFAULT true,
  joined_at   TIMESTAMP DEFAULT NOW(),
  UNIQUE(tenant_id, user_id)
);
```

### tenant_modules

Tracks which modules each tenant has activated.

```sql
CREATE TABLE tenant_modules (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  module_key  VARCHAR(50) NOT NULL,   -- crm | inventory | hrms | helpdesk
  is_active   BOOLEAN DEFAULT true,
  activated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(tenant_id, module_key)
);
```

### invitations

Tracks pending email invitations to join a workspace.

```sql
CREATE TABLE invitations (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  email       VARCHAR(255) NOT NULL,
  role        VARCHAR(50) NOT NULL DEFAULT 'staff',
  token       VARCHAR(255) UNIQUE NOT NULL,
  expires_at  TIMESTAMP NOT NULL,
  accepted_at TIMESTAMP,
  invited_by  UUID NOT NULL REFERENCES users(id),
  created_at  TIMESTAMP DEFAULT NOW()
);
```

### refresh_tokens

Stores refresh tokens for the JWT auth system.

```sql
CREATE TABLE refresh_tokens (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash  VARCHAR(255) UNIQUE NOT NULL,
  expires_at  TIMESTAMP NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW()
);
```

---

## CRM Module Schema

```sql
CREATE TABLE crm_contacts (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  first_name  VARCHAR(100) NOT NULL,
  last_name   VARCHAR(100),
  email       VARCHAR(255),
  phone       VARCHAR(50),
  company     VARCHAR(255),
  status      VARCHAR(50) DEFAULT 'lead',  -- lead | prospect | customer | churned
  assigned_to UUID REFERENCES users(id),
  created_by  UUID NOT NULL REFERENCES users(id),
  created_at  TIMESTAMP DEFAULT NOW(),
  updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE crm_deals (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  contact_id   UUID REFERENCES crm_contacts(id),
  title        VARCHAR(255) NOT NULL,
  value        DECIMAL(12, 2),
  stage        VARCHAR(50) DEFAULT 'new',  -- new | contacted | proposal | negotiation | won | lost
  expected_close_date DATE,
  assigned_to  UUID REFERENCES users(id),
  created_by   UUID NOT NULL REFERENCES users(id),
  created_at   TIMESTAMP DEFAULT NOW(),
  updated_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE crm_activities (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  contact_id  UUID REFERENCES crm_contacts(id),
  deal_id     UUID REFERENCES crm_deals(id),
  type        VARCHAR(50) NOT NULL,  -- call | email | meeting | note
  notes       TEXT,
  performed_by UUID NOT NULL REFERENCES users(id),
  performed_at TIMESTAMP DEFAULT NOW()
);
```

---

## Inventory Module Schema

```sql
CREATE TABLE inv_products (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name         VARCHAR(255) NOT NULL,
  sku          VARCHAR(100),
  description  TEXT,
  unit_price   DECIMAL(12, 2) NOT NULL DEFAULT 0,
  stock_qty    INTEGER NOT NULL DEFAULT 0,
  reorder_level INTEGER DEFAULT 10,
  category     VARCHAR(100),
  created_at   TIMESTAMP DEFAULT NOW(),
  updated_at   TIMESTAMP DEFAULT NOW(),
  UNIQUE(tenant_id, sku)
);

CREATE TABLE inv_suppliers (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name        VARCHAR(255) NOT NULL,
  email       VARCHAR(255),
  phone       VARCHAR(50),
  address     TEXT,
  created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE inv_orders (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  order_type   VARCHAR(20) NOT NULL,  -- purchase | sale
  supplier_id  UUID REFERENCES inv_suppliers(id),
  status       VARCHAR(50) DEFAULT 'pending',  -- pending | confirmed | shipped | delivered | cancelled
  total_amount DECIMAL(12, 2),
  created_by   UUID NOT NULL REFERENCES users(id),
  created_at   TIMESTAMP DEFAULT NOW(),
  updated_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE inv_order_items (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id    UUID NOT NULL REFERENCES inv_orders(id) ON DELETE CASCADE,
  product_id  UUID NOT NULL REFERENCES inv_products(id),
  quantity    INTEGER NOT NULL,
  unit_price  DECIMAL(12, 2) NOT NULL
);
```

---

## HRMS Module Schema

```sql
CREATE TABLE hr_employees (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  user_id         UUID REFERENCES users(id),
  employee_code   VARCHAR(50),
  department      VARCHAR(100),
  designation     VARCHAR(100),
  date_of_joining DATE,
  employment_type VARCHAR(50) DEFAULT 'full-time',  -- full-time | part-time | contract
  salary          DECIMAL(12, 2),
  manager_id      UUID REFERENCES hr_employees(id),
  is_active       BOOLEAN DEFAULT true,
  created_at      TIMESTAMP DEFAULT NOW(),
  UNIQUE(tenant_id, employee_code)
);

CREATE TABLE hr_attendance (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  employee_id  UUID NOT NULL REFERENCES hr_employees(id),
  date         DATE NOT NULL,
  check_in     TIMESTAMP,
  check_out    TIMESTAMP,
  status       VARCHAR(20) DEFAULT 'present',  -- present | absent | half-day | holiday
  UNIQUE(tenant_id, employee_id, date)
);

CREATE TABLE hr_leave_requests (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  employee_id  UUID NOT NULL REFERENCES hr_employees(id),
  leave_type   VARCHAR(50) NOT NULL,  -- sick | casual | earned | unpaid
  from_date    DATE NOT NULL,
  to_date      DATE NOT NULL,
  reason       TEXT,
  status       VARCHAR(20) DEFAULT 'pending',  -- pending | approved | rejected
  reviewed_by  UUID REFERENCES users(id),
  created_at   TIMESTAMP DEFAULT NOW()
);
```

---

## HelpDesk Module Schema

```sql
CREATE TABLE hd_tickets (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  ticket_no    SERIAL,
  subject      VARCHAR(255) NOT NULL,
  description  TEXT,
  status       VARCHAR(50) DEFAULT 'open',  -- open | in_progress | resolved | closed
  priority     VARCHAR(20) DEFAULT 'medium',  -- low | medium | high | urgent
  assigned_to  UUID REFERENCES users(id),
  created_by   UUID NOT NULL REFERENCES users(id),
  resolved_at  TIMESTAMP,
  created_at   TIMESTAMP DEFAULT NOW(),
  updated_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE hd_ticket_comments (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id   UUID NOT NULL REFERENCES hd_tickets(id) ON DELETE CASCADE,
  author_id   UUID NOT NULL REFERENCES users(id),
  body        TEXT NOT NULL,
  is_internal BOOLEAN DEFAULT false,  -- internal notes vs customer-visible replies
  created_at  TIMESTAMP DEFAULT NOW()
);
```

---

## Indexes

Performance-critical indexes to add:

```sql
-- Tenant scoping (most important - on every business table)
CREATE INDEX idx_crm_contacts_tenant ON crm_contacts(tenant_id);
CREATE INDEX idx_crm_deals_tenant ON crm_deals(tenant_id);
CREATE INDEX idx_inv_products_tenant ON inv_products(tenant_id);
CREATE INDEX idx_hr_employees_tenant ON hr_employees(tenant_id);
CREATE INDEX idx_hd_tickets_tenant ON hd_tickets(tenant_id);

-- Lookup indexes
CREATE INDEX idx_tenant_members_user ON tenant_members(user_id);
CREATE INDEX idx_tenant_members_tenant ON tenant_members(tenant_id);
CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_hd_tickets_status ON hd_tickets(tenant_id, status);
```

---

## Entity Relationship Overview

```
tenants
  ├── tenant_members (users ↔ tenants with roles)
  ├── tenant_modules (which modules are active)
  ├── invitations
  │
  ├── crm_contacts
  │     └── crm_deals
  │           └── crm_activities
  │
  ├── inv_products
  ├── inv_suppliers
  ├── inv_orders
  │     └── inv_order_items
  │
  ├── hr_employees
  │     ├── hr_attendance
  │     └── hr_leave_requests
  │
  └── hd_tickets
        └── hd_ticket_comments
```

---

## Data Isolation Rule

This is the most critical rule in the entire codebase:

> **Every query that reads or writes business data MUST include `WHERE tenant_id = $tenantId`**

This is enforced at the service layer. The `tenant_id` is never trusted from the request body — it always comes from the verified JWT token via middleware.

```js
// WRONG - never do this
const contacts = await db.query('SELECT * FROM crm_contacts');

// CORRECT - always scope by tenant
const contacts = await db.query(
  'SELECT * FROM crm_contacts WHERE tenant_id = $1',
  [req.tenantId]
);
```
