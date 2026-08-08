# Multi-Tenant SaaS Platform Builder

> A modular, enterprise-grade platform where any business can sign up, create its own isolated workspace, pick the modules it needs, invite its team, and manage operations — all from a single system.

---

## Problem Statement

### The Reality of Running a Small Business Today

Imagine you run a 20-person trading company in Pune. Every single day looks like this:

- Your sales team tracks leads in a WhatsApp group and a shared Google Sheet that three people edit simultaneously, causing data to get overwritten
- Your warehouse manager maintains stock levels in an Excel file on his personal laptop — if he's sick, nobody knows what's in stock
- Your HR person tracks attendance in a paper register and calculates salaries manually in another spreadsheet at the end of every month
- When a customer has a complaint, they call your personal mobile number, you write it on a sticky note, and hope you remember to follow up
- None of these systems talk to each other. A customer who placed an order exists in the sales sheet, the inventory sheet, and the complaints notebook as three completely separate, unconnected records

This is not an edge case. This is how the majority of small and medium businesses in India and across the world actually operate.

---

### Why Don't They Just Use Existing Software?

This is the most important question — and the answer is what makes this problem worth solving.

#### The Enterprise Software Problem

Tools like Salesforce, Microsoft Dynamics 365, and SAP exist and are genuinely powerful. But they are built for large enterprises with dedicated IT teams, months-long implementation projects, and budgets in the tens of thousands per month.

| Tool | Starting Cost | Setup Time | Who It's Really For |
|---|---|---|---|
| Salesforce | ₹2,000+/user/month | Weeks to months | 500+ employee companies |
| Microsoft Dynamics 365 | ₹3,500+/user/month | Months | Large enterprises with IT teams |
| SAP Business One | ₹5,000+/user/month | 3–6 months | Mid to large enterprises |
| Zoho One | ₹2,500/user/month | Days to weeks | Mid-market companies |

A 20-person business paying Salesforce rates would spend ₹40,000 every single month — before even accounting for implementation, training, and customization costs. That's not a business expense, that's a financial burden.

Beyond cost, these tools are **bloated**. A retail shop owner doesn't need Salesforce's AI-powered forecasting, territory management, or partner relationship portals. They need to track who they sold what to. Forcing them to navigate a tool built for a Fortune 500 company is a terrible user experience that leads to abandonment.

#### The Free Tools Problem

So businesses turn to free tools — and this creates a different but equally serious set of problems:

**Data is fragmented across tools that don't talk to each other.**
A customer exists in your CRM (Google Sheets), your inventory system (another Excel file), your billing tool (Tally), and your support inbox (Gmail) as four completely separate records. There is no single source of truth. When something goes wrong, you spend hours reconciling data across systems.

**There is no access control.**
When your entire business runs on shared Google Sheets, everyone can see everything — including salary information, confidential client data, and financial records. Or worse, you create a maze of different sheets with different sharing permissions that nobody can keep track of.

**Data lives on personal devices.**
The Excel file on the warehouse manager's laptop. The WhatsApp group that the sales rep takes with them when they quit. The Gmail account that holds all customer correspondence. When an employee leaves, they take institutional knowledge with them.

**There is no audit trail.**
Who changed that stock number? Who deleted that customer record? Who approved that leave request? With spreadsheets and WhatsApp, there is no way to know.

**Scaling is impossible.**
A Google Sheet that works for 5 people breaks down at 20. A WhatsApp group that works for a 3-person sales team becomes unmanageable at 10. Free tools have no growth path.

---

### The Gap in the Market

There is a massive, underserved gap between:

```
[Free tools: Google Sheets, WhatsApp, Excel]
              ↕ THE GAP — no good solution exists here
[Enterprise tools: Salesforce, SAP, Microsoft Dynamics]
```

In this gap live **millions of businesses** — the 63 million MSMEs in India alone — that:
- Are too big to function on spreadsheets and WhatsApp
- Are too small (in budget, team size, and technical capacity) to implement enterprise software
- Need something that works immediately, not after a 3-month implementation project
- Need to pay for what they use, not for 40 features they'll never touch

No existing product serves this segment well. Zoho comes closest but is still complex, expensive per user, and sells features in bundles rather than letting businesses pick exactly what they need.

---

### The Core Problems — Summarized

| # | Problem | Impact |
|---|---|---|
| 1 | Business tools are either too expensive or too basic | Businesses either overpay or underperform |
| 2 | Data is scattered across disconnected tools | No single source of truth, constant reconciliation |
| 3 | No access control on free tools | Data security and privacy risks |
| 4 | Setup takes weeks or months for enterprise tools | Businesses delay digitization indefinitely |
| 5 | Paying for features you don't need | Wasted money, cluttered interface, poor adoption |
| 6 | No audit trail or accountability | No visibility into who did what and when |
| 7 | Data lives on personal devices | Institutional knowledge lost when employees leave |

---

## Our Solution

### The One-Line Version

> A platform where any business can sign up, create their own isolated workspace, activate only the modules they need, invite their team with specific roles, and start managing operations — in minutes, not weeks.

---

### The Big Idea: A Platform, Not a Product

Most business software is a product — it does one thing (or a fixed set of things) and every customer gets the same experience.

We are building a **platform**. The platform itself provides the infrastructure — authentication, workspaces, user management, roles, billing. On top of that infrastructure, businesses assemble their own toolset by activating modules.

Think of it like this:

```
Shopify doesn't sell you a store. It gives you the platform to build your store.
We don't sell you a CRM. We give you the platform to build your business operating system.
```

A retail business activates Inventory + CRM.
A services agency activates CRM + HelpDesk.
A manufacturing company activates Inventory + HRMS + HelpDesk.
A startup activates all four.

Every business gets exactly what they need. Nothing more, nothing less.

---

### How It Solves Each Problem

| Problem | How We Solve It |
|---|---|
| Too expensive | Freemium model — free for small teams, affordable paid plans. No per-user pricing trap. |
| Too complex | Clean, modern UI designed for non-technical users. Setup in under 10 minutes. |
| Data scattered | All modules share one database and one workspace. A customer in CRM is the same record linked in HelpDesk. |
| No access control | Built-in RBAC — Owner, Admin, Manager, Staff roles. Every user sees only what they're supposed to. |
| Paying for unused features | Activate only the modules you need. Deactivate them when you don't. |
| No audit trail | Every action is logged — who created, edited, or deleted what, and when. |
| Data on personal devices | Everything lives in the cloud, scoped to the business workspace. Employees come and go, the data stays. |

---

### The Four Pillars of the Solution

#### 1. Multi-Tenant Workspaces

Every business that signs up gets a completely isolated workspace — their own private environment within the platform. Their data never mixes with any other business's data.

- Each workspace has a unique subdomain: `acme.platform.com`
- All data is scoped to the workspace at the database level — not just at the application level
- If the platform serves 10,000 businesses, each one operates as if they have their own private system
- Employees of Company A can never see, access, or even know about Company B's data

This is the foundation that makes everything else possible. Without true data isolation, you don't have a multi-tenant platform — you just have a shared database with a login screen.

#### 2. Plug-and-Play Module System

Modules are independent feature sets that a business can turn on or off from their workspace settings. The platform ships with four core modules:

| Module | What It Does | Who Uses It |
|---|---|---|
| **CRM** | Track leads, contacts, deals, and sales pipeline | Sales teams |
| **Inventory** | Manage products, stock levels, orders, and suppliers | Operations / Warehouse |
| **HRMS** | Employee records, attendance, leave management | HR department |
| **HelpDesk** | Customer support tickets, agent assignment, resolution tracking | Support team |

When a module is activated:
- It appears in the sidebar navigation immediately
- The backend starts accepting API requests for that module
- The team can start using it right away — no configuration required

When a module is deactivated:
- It disappears from the UI
- The data is preserved — reactivating it brings everything back
- The backend blocks all requests to that module's endpoints

This is not just a UI toggle. Module access is enforced at the **middleware level** on every single API request.

#### 3. Role-Based Access Control (RBAC)

Every member of a workspace has a role that determines exactly what they can see and do. Roles are hierarchical:

```
Owner  →  Full control. Billing, workspace deletion, all settings.
  ↓
Admin  →  Manage members, activate modules, all operational access.
  ↓
Manager  →  Manage within their module. Approve leaves, assign tickets, etc.
  ↓
Staff  →  Day-to-day work. Create and update records, cannot delete.
```

This means:
- A warehouse staff member can update stock levels but cannot delete products or see salary data
- A sales manager can see all deals but cannot remove team members from the workspace
- An HR admin can manage employee records but cannot touch CRM data if they don't have that role
- The business owner has complete control over everything

Roles are enforced at the API level — not just hidden in the UI. Even if someone bypasses the frontend, the backend will reject unauthorized requests.

#### 4. Unified Workspace — One System, All Data Connected

Because all modules live within the same workspace and share the same database, data is connected across modules in a way that's impossible with separate tools:

- A contact in CRM can be linked to a support ticket in HelpDesk
- An employee in HRMS is the same user account that logs into the platform
- A sales order in Inventory can be traced back to a deal in CRM
- The dashboard shows a unified view of the entire business — not four separate dashboards from four separate tools

This is the compounding value of a platform over a collection of tools. The more modules a business activates, the more connected and valuable their data becomes.

---

### What Makes This Different from Existing Solutions

| | Our Platform | Zoho One | Odoo | Salesforce |
|---|---|---|---|---|
| Price | Free → ₹999/mo | ₹2,500/user/mo | ₹1,200/user/mo | ₹2,000+/user/mo |
| Setup time | < 10 minutes | Hours to days | Days to weeks | Weeks to months |
| Module flexibility | Activate any module individually | Fixed app bundles | Modular but complex to configure | Add-on marketplace |
| Target user | Non-technical SMB owner | SMB with some IT support | Businesses with technical team | Enterprise IT departments |
| Learning curve | Minimal | Moderate | High | Very High |
| Data ownership | Full — your workspace, your data | Vendor-controlled | Self-hosted option | Vendor-controlled |

---

### The Vision

The immediate goal is an MVP with four modules serving Indian SMBs. But the platform architecture is designed for something bigger:

- Any module can be added to the platform — Finance, Projects, Document Management, Analytics
- Third-party developers could build and publish modules to a marketplace (like Shopify apps)
- Businesses could customize their workspace with their own branding (white-labeling)
- The same platform could power industry-specific versions — a clinic management system, a school management system, a logistics platform — all built on the same multi-tenant core

The platform is the product. The modules are just the beginning.

---

## Comparable Products

| Product | What They Do |
|---|---|
| Zoho One | Suite of 40+ business apps |
| Odoo | Open-source modular ERP |
| Salesforce | Enterprise CRM + ecosystem |
| Microsoft Dynamics 365 | Enterprise ERP + CRM |

**Our difference:** We target SMBs and startups with a freemium model, true module-level flexibility, and a setup time of minutes.

---

## Core Features

### Multi-Tenancy
- Every business that signs up gets a completely isolated workspace
- Data is scoped per tenant — no business can ever see another's data
- Each tenant gets a unique subdomain: `acme.platform.com`

### Plug-and-Play Modules
Businesses activate only what they need:

| Module | Purpose |
|---|---|
| CRM | Leads, contacts, deals, pipeline |
| Inventory | Products, stock, orders, suppliers |
| HRMS | Employees, attendance, leave, payroll |
| HelpDesk | Support tickets, agents, SLA tracking |

### Role-Based Access Control (RBAC)
- Owner → full access
- Admin → manage modules and users
- Manager → manage within their module
- Staff → limited read/write access
- Custom roles per tenant

### Workspace Management
- Invite team members via email
- Assign and revoke roles
- Module-level permissions
- Audit logs for every action

---

## Project Structure

```
Multi-Tenant SaaS/
├── README.md                  ← You are here
├── docs/
│   ├── SYSTEM_ARCHITECTURE.md ← Architecture diagrams and decisions
│   ├── DATABASE_DESIGN.md     ← Schema design and tenant isolation strategy
│   ├── API_DESIGN.md          ← REST API structure and all endpoints
│   ├── MODULES.md             ← Detailed breakdown of each module
│   ├── AUTH_AND_RBAC.md       ← Authentication flow and role system
│   ├── TECH_STACK.md          ← Technology choices with reasoning
│   ├── DEVELOPMENT_PLAN.md    ← Timeline, milestones, task assignments
│   └── BUSINESS_MODEL.md      ← Pricing, market fit, competitor analysis
├── frontend/                  ← React.js application
├── backend/                   ← Node.js / Django REST API
└── database/                  ← Migrations and seed data
```

---

## Tech Stack (Summary)

| Layer | Technology |
|---|---|
| Frontend | React.js, Tailwind CSS, React Router |
| Backend | Node.js + Express.js |
| Database | PostgreSQL |
| Authentication | JWT + Refresh Tokens |
| Authorization | Custom RBAC middleware |
| Hosting | AWS EC2 / Railway / Render |
| Storage | AWS S3 |
| Email | NodeMailer / SendGrid |

> Full reasoning for each choice is in [docs/TECH_STACK.md](docs/TECH_STACK.md)

---

## How Multi-Tenancy Works

```
User visits: acme.platform.com
        ↓
Middleware extracts tenant slug: "acme"
        ↓
Resolves to Tenant ID: tenant_id = "uuid-xxxx"
        ↓
All DB queries scoped: WHERE tenant_id = 'uuid-xxxx'
        ↓
Tenant sees only their data
```

Every single database table that holds business data has a `tenant_id` column. The backend middleware automatically injects this into every query. No tenant can ever access another tenant's data.

> Deep dive in [docs/DATABASE_DESIGN.md](docs/DATABASE_DESIGN.md)

---

## Module System

Modules are not hardcoded into the platform. Each tenant has a `tenant_modules` table that tracks which modules are active. The frontend dynamically renders navigation and routes based on active modules. The backend enforces module access at the middleware level.

```
Tenant activates "CRM"
        ↓
tenant_modules row created: { tenant_id, module: "crm", active: true }
        ↓
Frontend shows CRM in sidebar
        ↓
Backend allows requests to /api/crm/* for this tenant
```

> Full module specs in [docs/MODULES.md](docs/MODULES.md)

---

## Authentication Flow

```
1. User registers / logs in
2. Server validates credentials
3. Server issues: Access Token (15min) + Refresh Token (7 days)
4. Access Token sent in Authorization header
5. Refresh Token stored in HttpOnly cookie
6. Every request passes through: Auth Middleware → Tenant Middleware → RBAC Middleware
```

> Full auth and RBAC design in [docs/AUTH_AND_RBAC.md](docs/AUTH_AND_RBAC.md)

---

## Development Phases

| Phase | What Gets Built | Timeline |
|---|---|---|
| Phase 1 | Auth, Tenant creation, Workspace setup | Weeks 1-3 |
| Phase 2 | Module engine, CRM module | Weeks 4-6 |
| Phase 3 | Inventory + HRMS modules | Weeks 7-9 |
| Phase 4 | HelpDesk + Dashboard + Analytics | Weeks 10-12 |
| Phase 5 | Billing, Polish, Testing, Deployment | Weeks 13-15 |

> Full plan with task assignments in [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md)

---

## Team

| Name | Role |
|---|---|
| [Member 1] | Backend + Database |
| [Member 2] | Frontend + UI/UX |
| [Member 3] | Auth + DevOps |
| [Member 4] | Modules + Testing |

---

## Documentation Index

- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [Database Design](docs/DATABASE_DESIGN.md)
- [API Design](docs/API_DESIGN.md)
- [Modules Breakdown](docs/MODULES.md)
- [Auth and RBAC](docs/AUTH_AND_RBAC.md)
- [Tech Stack](docs/TECH_STACK.md)
- [Development Plan](docs/DEVELOPMENT_PLAN.md)
- [Business Model](docs/BUSINESS_MODEL.md)
