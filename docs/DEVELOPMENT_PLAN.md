# Development Plan

## Overview

The project is divided into 5 phases over approximately 15 weeks. Each phase builds on the previous one and ends with a working, demonstrable state of the application.

---

## Milestones at a Glance

| Phase | Focus | Duration | Deliverable |
|---|---|---|---|
| Phase 1 | Foundation — Auth + Tenant Setup | Weeks 1–3 | Working login, workspace creation, member invite |
| Phase 2 | Module Engine + CRM | Weeks 4–6 | Module activation system + full CRM module |
| Phase 3 | Inventory + HRMS | Weeks 7–9 | Two more working modules |
| Phase 4 | HelpDesk + Dashboard | Weeks 10–12 | Final module + analytics dashboard |
| Phase 5 | Polish + Testing + Deploy | Weeks 13–15 | Deployed, tested, documented product |

---

## Phase 1: Foundation (Weeks 1–3)

### Goal
A user can register, create a workspace, log in, and invite team members. No modules yet — just the core platform shell.

### Backend Tasks
- [ ] Project setup: Node.js + Express + PostgreSQL + folder structure
- [ ] Database: Create core tables (tenants, users, tenant_members, invitations, refresh_tokens)
- [ ] Auth: POST /auth/register — create user + tenant + owner membership
- [ ] Auth: POST /auth/login — validate credentials, issue JWT + refresh token
- [ ] Auth: POST /auth/refresh — refresh access token via cookie
- [ ] Auth: POST /auth/logout — invalidate refresh token
- [ ] Auth: Email verification flow
- [ ] Middleware: authMiddleware, tenantMiddleware, rbacMiddleware
- [ ] Workspace: GET /workspace — return tenant info + active modules
- [ ] Workspace: POST /workspace/invite — send invitation email
- [ ] Workspace: GET /workspace/members — list all members
- [ ] Workspace: PATCH /workspace/members/:id/role — change role
- [ ] Workspace: DELETE /workspace/members/:id — remove member
- [ ] Invitation: GET /invite/:token — validate and accept invitation

### Frontend Tasks
- [ ] Project setup: React + Tailwind + Redux + React Router
- [ ] Auth pages: Register, Login, Verify Email, Forgot Password
- [ ] Auth state: Redux slice for user + tenant + tokens
- [ ] Axios interceptor: attach token, handle 401 refresh
- [ ] App shell: Sidebar layout (empty modules for now), top navbar
- [ ] Workspace settings page: member list, invite form, role management
- [ ] Protected route wrapper: redirect to login if not authenticated

### End of Phase 1 Demo
- Register a new business → workspace created
- Login → see empty dashboard with workspace name
- Invite a colleague → they receive email, accept, and can log in to the same workspace

---

## Phase 2: Module Engine + CRM (Weeks 4–6)

### Goal
The module activation system works. The CRM module is fully functional.

### Backend Tasks
- [ ] Module system: tenant_modules table + activate/deactivate endpoints
- [ ] Module middleware: check if module is active before allowing requests
- [ ] CRM: All contacts CRUD endpoints
- [ ] CRM: All deals CRUD endpoints
- [ ] CRM: Pipeline endpoint (deals grouped by stage)
- [ ] CRM: Activities endpoints (log call, email, meeting, note)
- [ ] CRM: Assign contact/deal to team member

### Frontend Tasks
- [ ] Module settings page: list all modules, toggle activate/deactivate
- [ ] Dynamic sidebar: render module links based on active modules
- [ ] CRM: Contacts list page (table with search + filter)
- [ ] CRM: Contact detail page (info + linked deals + activity timeline)
- [ ] CRM: Add/Edit contact form (modal or page)
- [ ] CRM: Deals list page
- [ ] CRM: Deal pipeline board (Kanban columns by stage)
- [ ] CRM: Add/Edit deal form
- [ ] CRM: Log activity form

### End of Phase 2 Demo
- Activate CRM from workspace settings → CRM appears in sidebar
- Add contacts, create deals, move deals through pipeline stages
- Log a call on a contact, see it in the activity timeline

---

## Phase 3: Inventory + HRMS (Weeks 7–9)

### Goal
Two more modules are fully functional.

### Backend Tasks
- [ ] Inventory: Products CRUD + low-stock endpoint
- [ ] Inventory: Suppliers CRUD
- [ ] Inventory: Orders CRUD + status update + auto stock adjustment
- [ ] HRMS: Employees CRUD
- [ ] HRMS: Attendance check-in/check-out + history
- [ ] HRMS: Leave request submit + approve/reject

### Frontend Tasks
- [ ] Inventory: Products list + add/edit product form
- [ ] Inventory: Low-stock alert list
- [ ] Inventory: Orders list + create order form + status update
- [ ] Inventory: Suppliers list + add/edit supplier form
- [ ] HRMS: Employee directory + employee profile page
- [ ] HRMS: Add/edit employee form
- [ ] HRMS: Attendance page (check-in/out button + history table)
- [ ] HRMS: Leave requests list + submit form + approve/reject buttons

### End of Phase 3 Demo
- Activate Inventory → manage products, create a purchase order, mark it delivered (stock updates)
- Activate HRMS → add employees, check in for the day, submit a leave request, approve it as manager

---

## Phase 4: HelpDesk + Dashboard (Weeks 10–12)

### Goal
Final module complete. Each module has a summary dashboard. Main workspace dashboard shows cross-module stats.

### Backend Tasks
- [ ] HelpDesk: Tickets CRUD + assign + status change
- [ ] HelpDesk: Comments (public + internal notes)
- [ ] Dashboard: Stats endpoints for each module (counts, summaries)
- [ ] Dashboard: Main workspace overview stats

### Frontend Tasks
- [ ] HelpDesk: Ticket list with filter by status/priority
- [ ] HelpDesk: Ticket detail page with comment thread
- [ ] HelpDesk: Create ticket form
- [ ] HelpDesk: Assign ticket + change status controls
- [ ] CRM Dashboard: total contacts, open deals, pipeline value, won this month
- [ ] Inventory Dashboard: total products, low stock count, pending orders
- [ ] HRMS Dashboard: total employees, present today, pending leaves
- [ ] HelpDesk Dashboard: open tickets, resolved today, by priority
- [ ] Main Dashboard: combined overview of all active modules

### End of Phase 4 Demo
- Full walkthrough of all 4 modules
- Dashboard shows live stats from all modules

---

## Phase 5: Polish, Testing, Deployment (Weeks 13–15)

### Goal
The application is production-ready, tested, and deployed.

### Tasks
- [ ] Write unit tests for all service functions (Jest)
- [ ] Write integration tests for critical API endpoints
- [ ] Frontend: loading states, error states, empty states for all pages
- [ ] Frontend: form validation error messages
- [ ] Frontend: responsive design check (tablet + mobile)
- [ ] Security audit: check all endpoints for missing auth/tenant/RBAC middleware
- [ ] Performance: add database indexes, check slow queries
- [ ] Set up Docker + docker-compose for local dev
- [ ] Deploy backend to AWS EC2 or Railway
- [ ] Deploy frontend to Vercel or Netlify
- [ ] Set up PostgreSQL on AWS RDS or Railway
- [ ] Configure Nginx with SSL (Let's Encrypt)
- [ ] Set up wildcard subdomain DNS (*.platform.com)
- [ ] Write final project report and presentation

---

## Task Assignment Template

> Fill in your team member names

| Area | Assigned To |
|---|---|
| Backend — Auth + Middleware | [Member Name] |
| Backend — CRM + HelpDesk modules | [Member Name] |
| Backend — Inventory + HRMS modules | [Member Name] |
| Frontend — Auth + Shell + Workspace | [Member Name] |
| Frontend — CRM + HelpDesk UI | [Member Name] |
| Frontend — Inventory + HRMS UI | [Member Name] |
| Database design + migrations | [Member Name] |
| DevOps — Docker + Deployment | [Member Name] |
| Testing | All members |

---

## Git Branch Strategy

```
main          ← production-ready code only
  └── develop ← integration branch, all features merge here first
        ├── feature/auth-backend
        ├── feature/tenant-middleware
        ├── feature/crm-contacts
        ├── feature/inventory-products
        └── feature/hrms-employees
```

Rules:
- Never commit directly to `main`
- Every feature gets its own branch from `develop`
- Create a Pull Request to merge into `develop`
- At least one other team member reviews the PR before merging
- `develop` is merged into `main` at the end of each phase

---

## Definition of Done

A task is considered done when:
1. The feature works as described
2. The API endpoint is tested in Postman
3. The frontend UI handles loading, error, and empty states
4. The code is reviewed by at least one other team member
5. It's merged into `develop`
