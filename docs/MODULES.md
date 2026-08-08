# Modules Breakdown

## Overview

The platform is built around a plug-and-play module system. Each module is an independent feature set that a tenant can activate or deactivate from their workspace settings. Modules share the same auth and tenant infrastructure but are otherwise self-contained.

---

## Module Registry

| Module Key | Display Name | Description |
|---|---|---|
| `crm` | CRM | Customer Relationship Management |
| `inventory` | Inventory | Stock, Products, Orders, Suppliers |
| `hrms` | HRMS | Human Resource Management System |
| `helpdesk` | HelpDesk | Customer Support Ticket System |

---

## How the Module System Works

### Activation

When a tenant activates a module:
1. A row is inserted into `tenant_modules`: `{ tenant_id, module_key: 'crm', is_active: true }`
2. The frontend fetches active modules on login and stores them in state
3. The sidebar dynamically renders navigation links for active modules only
4. The backend `module.middleware.js` checks `tenant_modules` before allowing requests to module routes

### Deactivation

When a tenant deactivates a module:
1. The `tenant_modules` row is updated: `is_active = false`
2. The data is NOT deleted — it's preserved in case they reactivate
3. The frontend hides the module from navigation
4. The backend returns `403 Module Not Active` for any requests to that module's routes

---

## Module 1: CRM (Customer Relationship Management)

### Purpose
Help businesses track leads, manage customer relationships, and monitor their sales pipeline.

### Key Concepts

- **Contact**: A person or company the business interacts with. Can be a lead, prospect, or existing customer.
- **Deal**: A potential sale linked to a contact. Has a monetary value and moves through pipeline stages.
- **Pipeline**: A visual board showing deals grouped by stage (Kanban-style).
- **Activity**: A logged interaction — a call made, email sent, meeting held, or note added.

### Features

- Contact list with search, filter by status, and sort
- Contact detail page showing all linked deals and activity history
- Deal pipeline board (drag-and-drop between stages)
- Deal stages: New → Contacted → Proposal Sent → Negotiation → Won / Lost
- Activity log on each contact and deal
- Assign contacts and deals to team members
- Basic dashboard: total contacts, open deals, deals won this month, pipeline value

### User Stories

- As a sales rep, I can add a new lead with their contact details
- As a sales rep, I can log a call I had with a contact
- As a manager, I can see all open deals and their current stage
- As a manager, I can reassign a deal to a different sales rep
- As an admin, I can see the total pipeline value and conversion rate

---

## Module 2: Inventory Management

### Purpose
Help businesses track their products, manage stock levels, handle purchase and sales orders, and manage suppliers.

### Key Concepts

- **Product**: An item the business buys or sells. Has a SKU, price, and stock quantity.
- **Stock Level**: Current quantity of a product. Updated automatically when orders are processed.
- **Reorder Level**: A threshold — when stock drops below this, the product appears in the low-stock alert list.
- **Purchase Order**: An order placed with a supplier to restock products.
- **Sales Order**: An order from a customer, which reduces stock.
- **Supplier**: A vendor the business buys products from.

### Features

- Product catalog with search and category filter
- Real-time stock quantity tracking
- Low-stock alerts (products below reorder level)
- Purchase order creation and status tracking (Pending → Confirmed → Delivered)
- Sales order creation and status tracking
- Stock automatically adjusts when an order is marked as Delivered/Completed
- Supplier directory
- Basic dashboard: total products, low-stock count, pending orders, total inventory value

### User Stories

- As a staff member, I can view current stock levels for all products
- As a manager, I can create a purchase order to restock a product
- As a manager, I can mark an order as delivered, which updates stock automatically
- As an admin, I can add new products and set their reorder levels
- As any user, I can see which products are running low

---

## Module 3: HRMS (Human Resource Management System)

### Purpose
Help businesses manage their workforce — employee records, daily attendance, leave management, and basic payroll information.

### Key Concepts

- **Employee**: A person who works at the business. Linked to a platform user account (optional).
- **Attendance**: Daily check-in and check-out records for each employee.
- **Leave Request**: A formal request by an employee to take time off.
- **Department**: A group of employees (e.g., Sales, Engineering, Support).

### Features

- Employee directory with profile pages
- Employee details: department, designation, date of joining, employment type, salary, manager
- Daily attendance tracking (check-in / check-out)
- Attendance history and monthly summary per employee
- Leave request submission by employees
- Leave approval/rejection by managers
- Leave types: Sick, Casual, Earned, Unpaid
- Basic dashboard: total employees, present today, on leave today, pending leave requests

### User Stories

- As an employee, I can check in and check out each day
- As an employee, I can submit a leave request with a reason
- As a manager, I can approve or reject leave requests from my team
- As an admin, I can add new employees and set their department and salary
- As an admin, I can view attendance records for any employee

---

## Module 4: HelpDesk

### Purpose
Help businesses manage customer support by tracking issues as tickets, assigning them to agents, and resolving them with a clear audit trail.

### Key Concepts

- **Ticket**: A support request. Has a subject, description, priority, and status.
- **Agent**: A team member assigned to handle tickets.
- **Comment**: A reply or internal note on a ticket. Internal notes are only visible to agents, not customers.
- **Priority**: How urgent the ticket is — Low, Medium, High, Urgent.
- **SLA (future)**: Service Level Agreement — a target time to resolve tickets based on priority.

### Features

- Ticket creation by any user or customer
- Ticket list with filter by status, priority, and assigned agent
- Ticket detail page with full comment thread
- Assign tickets to specific agents
- Internal notes (visible only to agents) vs public replies
- Status workflow: Open → In Progress → Resolved → Closed
- Priority levels: Low, Medium, High, Urgent
- Basic dashboard: open tickets, resolved today, average resolution time, tickets by priority

### User Stories

- As a customer/user, I can submit a support ticket with a description of my issue
- As an agent, I can see all tickets assigned to me
- As an agent, I can reply to a ticket and change its status
- As a manager, I can assign an unassigned ticket to an agent
- As a manager, I can see all open tickets and their priorities

---

## Module Comparison Table

| Feature | CRM | Inventory | HRMS | HelpDesk |
|---|---|---|---|---|
| Primary entity | Contact/Deal | Product/Order | Employee | Ticket |
| Who uses it | Sales team | Operations | HR + All staff | Support team |
| Key metric | Pipeline value | Stock levels | Attendance rate | Resolution time |
| Data sensitivity | Medium | Medium | High (salary) | Medium |

---

## Future Modules (Roadmap)

| Module | Description |
|---|---|
| Finance | Invoices, expenses, basic P&L |
| Projects | Task management, milestones, team assignments |
| Documents | File storage and sharing per workspace |
| Analytics | Cross-module reporting and dashboards |
| Customer Portal | External portal for customers to submit and track tickets |
