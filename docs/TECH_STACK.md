# Tech Stack

## Overview

Every technology choice is made with three priorities in mind:
1. **Practical for a final year project** — well-documented, large community, easy to find help
2. **Industry relevant** — technologies used in real production SaaS products
3. **Scalable** — the architecture can grow beyond the MVP without a full rewrite

---

## Frontend

### React.js
- **Why**: The most widely used frontend library. Component-based architecture maps perfectly to our modular system — each module is a set of React components.
- **Version**: React 18
- **Key features used**: Hooks, Context API, lazy loading for module code-splitting

### Tailwind CSS
- **Why**: Utility-first CSS framework that lets us build consistent UI fast without writing custom CSS files. No fighting with CSS specificity.
- **Alternative considered**: Material UI — rejected because it's opinionated and harder to customize for a unique product look

### React Router v6
- **Why**: Standard routing for React SPAs. Supports nested routes which we use for module layouts (e.g., `/crm/contacts`, `/crm/deals` share the CRM layout).

### Redux Toolkit
- **Why**: Global state management for auth state, active tenant info, and active modules list. These need to be accessible across the entire app.
- **Alternative considered**: Zustand — simpler but Redux Toolkit is more industry-standard and better for a team project

### Axios
- **Why**: HTTP client for API calls. Supports request/response interceptors which we use to automatically attach the Authorization header and handle token refresh on 401 responses.

### React Query (TanStack Query)
- **Why**: Server state management — handles caching, background refetching, and loading/error states for API data. Removes the need to manually manage loading states in components.

---

## Backend

### Node.js + Express.js
- **Why**: JavaScript on both frontend and backend means the team shares knowledge and can work across the stack. Express is minimal and gives us full control over middleware, which is critical for our multi-tenant middleware chain.
- **Alternative considered**: Django (Python) — powerful but the team is more comfortable with JavaScript. Also, Express's middleware model is a better fit for our layered auth/tenant/RBAC pipeline.

### PostgreSQL
- **Why**: 
  - Relational database is the right choice for our structured, relational data (tenants → members → modules → business data)
  - ACID compliance ensures data integrity — critical for business data
  - Supports UUID primary keys natively
  - Row-Level Security (RLS) feature can add an extra layer of tenant isolation
  - Excellent support for JSON columns if we need flexible data in the future
- **Alternative considered**: MongoDB — rejected because our data is highly relational and a document database would make joins and referential integrity much harder

### node-postgres (pg)
- **Why**: The standard PostgreSQL client for Node.js. We use `pg.Pool` for connection pooling — reusing database connections instead of opening a new one per request.

### bcrypt
- **Why**: Industry standard for password hashing. The cost factor (work factor) can be increased over time as hardware gets faster, keeping passwords secure.

### jsonwebtoken
- **Why**: Standard library for creating and verifying JWTs. Simple API, well-maintained.

### Joi / Zod
- **Why**: Request body validation. Every API endpoint validates its input before processing. Zod is preferred because it's TypeScript-first and gives us type inference.

---

## Infrastructure and DevOps

### Redis
- **Why**: 
  - Caching tenant configuration (active modules, plan info) to avoid hitting PostgreSQL on every request
  - Session/token blacklisting for logout
  - Job queue backend (with Bull) for background tasks like sending emails
- **What it caches**: Tenant config is cached for 5 minutes. Cache is invalidated when tenant settings change.

### AWS S3
- **Why**: Object storage for file uploads (employee profile photos, product images, ticket attachments). Cheap, reliable, and integrates with CloudFront for CDN delivery.

### AWS SES (Simple Email Service)
- **Why**: Sending transactional emails — email verification, password reset, workspace invitations. Cost-effective at scale.
- **Alternative for development**: NodeMailer with a Gmail SMTP or Mailtrap for testing

### Nginx
- **Why**: Reverse proxy that sits in front of the Node.js server. Handles:
  - SSL termination (HTTPS)
  - Subdomain routing (extracts tenant slug and forwards to backend)
  - Serving static frontend files
  - Rate limiting

### Docker
- **Why**: Containerizes the application so it runs identically in development, staging, and production. `docker-compose` for local development with Node.js + PostgreSQL + Redis all running together.

---

## Development Tools

### ESLint + Prettier
- **Why**: Code style consistency across the team. ESLint catches bugs, Prettier enforces formatting. No more arguments about tabs vs spaces.

### Git + GitHub
- **Why**: Version control and collaboration. Branch strategy: `main` (production), `develop` (integration), feature branches per task.

### Postman
- **Why**: API testing and documentation during development. The team can share a Postman collection so everyone can test endpoints without writing frontend code first.

### pgAdmin / TablePlus
- **Why**: GUI for PostgreSQL. Easier to inspect data and run queries during development than using the command line.

---

## Full Stack Summary

```
┌─────────────────────────────────────────────────────┐
│  FRONTEND                                           │
│  React 18 + Tailwind CSS + Redux Toolkit            │
│  React Router + React Query + Axios                 │
└─────────────────────────────────────────────────────┘
                        │
                     REST API
                        │
┌─────────────────────────────────────────────────────┐
│  BACKEND                                            │
│  Node.js + Express.js                               │
│  JWT Auth + bcrypt + Joi/Zod validation             │
└─────────────────────────────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
┌─────────▼──────┐ ┌────▼────┐ ┌─────▼──────┐
│  PostgreSQL    │ │  Redis  │ │   AWS S3   │
│  (Primary DB)  │ │ (Cache) │ │  (Files)   │
└────────────────┘ └─────────┘ └────────────┘
```

---

## Why Not [Alternative]?

| Alternative | Why We Didn't Choose It |
|---|---|
| Next.js | SSR adds complexity we don't need for a dashboard app. Pure React SPA is simpler. |
| GraphQL | REST is simpler to implement and debug for a team project. GraphQL's benefits show at larger scale. |
| MongoDB | Our data is relational. Using a document DB would fight against our data model. |
| Firebase | Vendor lock-in. Limited control over data model and query patterns. |
| Prisma ORM | Adds abstraction that hides SQL. We want the team to understand the actual queries being run. |
| TypeScript | Would be ideal but adds setup overhead. Can be migrated to later. |
