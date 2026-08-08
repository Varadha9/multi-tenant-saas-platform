# Authentication and Role-Based Access Control

## Overview

The platform uses **JWT (JSON Web Tokens)** for stateless authentication combined with a custom **Role-Based Access Control (RBAC)** system for authorization. Every request passes through a middleware chain that verifies identity, confirms tenant membership, and checks permissions before reaching the route handler.

---

## Authentication Strategy

### Why JWT?

- Stateless — the server doesn't need to store session data
- The backend can scale horizontally without shared session storage
- The token carries the user's identity and tenant context, reducing DB lookups per request
- Industry standard for REST APIs

### Token Types

| Token | Lifetime | Storage | Purpose |
|---|---|---|---|
| Access Token | 15 minutes | Memory (JS variable) | Authenticate API requests |
| Refresh Token | 7 days | HttpOnly Cookie | Get a new access token when it expires |

The access token is short-lived to minimize damage if it's stolen. The refresh token is stored in an HttpOnly cookie so JavaScript cannot access it, protecting against XSS attacks.

---

## JWT Payload Structure

```json
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "role": "manager",
  "email": "john@acme.com",
  "iat": 1700000000,
  "exp": 1700000900
}
```

The `tenant_id` and `role` are embedded in the token so the middleware doesn't need to hit the database on every request to determine who the user is and what tenant they belong to.

---

## Authentication Flow

### Registration

```
1. User submits: full_name, email, password, workspace_name, workspace_slug
2. Server validates input (email format, password strength, slug uniqueness)
3. Server hashes password with bcrypt (cost factor 12)
4. Server creates: users row + tenants row + tenant_members row (role: owner)
5. Server sends verification email with a signed token
6. Server responds: 201 Created (no tokens yet — email must be verified first)
```

### Login

```
1. User submits: email, password
2. Server finds user by email
3. Server compares password with bcrypt hash
4. Server checks email is verified
5. Server generates:
   - Access Token (JWT, signed with ACCESS_TOKEN_SECRET, expires 15min)
   - Refresh Token (random UUID, hashed and stored in refresh_tokens table)
6. Refresh Token set as HttpOnly cookie
7. Access Token returned in response body
8. Frontend stores Access Token in memory (not localStorage)
```

### Token Refresh

```
1. Access Token expires (or frontend detects 401 response)
2. Frontend sends POST /auth/refresh (no body — refresh token is in cookie)
3. Server reads refresh token from cookie
4. Server hashes it and looks it up in refresh_tokens table
5. Server checks it hasn't expired
6. Server issues new Access Token
7. Server responds with new Access Token
```

### Logout

```
1. Frontend sends POST /auth/logout
2. Server deletes the refresh_tokens row for this token
3. Server clears the HttpOnly cookie
4. Frontend clears the Access Token from memory
```

---

## Middleware Chain

Every protected request passes through this chain in order:

```
Request
  │
  ▼
authMiddleware
  - Reads Authorization: Bearer <token>
  - Verifies JWT signature using ACCESS_TOKEN_SECRET
  - Checks token hasn't expired
  - Attaches decoded payload to req.user
  - Returns 401 if invalid
  │
  ▼
tenantMiddleware
  - Reads tenant slug from subdomain or req.user.tenant_id
  - Confirms tenant exists and is_active = true
  - Confirms req.user belongs to this tenant (tenant_members check)
  - Attaches tenant info to req.tenant
  - Returns 403 if tenant inactive or user not a member
  │
  ▼
rbacMiddleware(requiredRole)
  - Compares req.user.role against the required role for this route
  - Uses role hierarchy: owner > admin > manager > staff
  - Returns 403 if role is insufficient
  │
  ▼
moduleMiddleware(moduleKey)
  - Checks tenant_modules table for this tenant + module
  - Returns 403 "Module not activated" if module is off
  │
  ▼
Route Handler
```

---

## Role-Based Access Control

### Roles

| Role | Who It's For | Level |
|---|---|---|
| `owner` | The person who created the workspace | 4 (highest) |
| `admin` | Trusted managers with full operational access | 3 |
| `manager` | Department heads, team leads | 2 |
| `staff` | Regular employees | 1 (lowest) |

### Role Hierarchy

A higher role always includes all permissions of lower roles. This is enforced by a simple numeric comparison:

```js
const ROLE_LEVELS = {
  staff: 1,
  manager: 2,
  admin: 3,
  owner: 4
};

function hasRole(userRole, requiredRole) {
  return ROLE_LEVELS[userRole] >= ROLE_LEVELS[requiredRole];
}
```

### Permission Matrix

| Action | Staff | Manager | Admin | Owner |
|---|---|---|---|---|
| View any module data | ✅ | ✅ | ✅ | ✅ |
| Create records | ✅ | ✅ | ✅ | ✅ |
| Update records | ✅ | ✅ | ✅ | ✅ |
| Delete records | ❌ | ✅ | ✅ | ✅ |
| Invite members | ❌ | ❌ | ✅ | ✅ |
| Change member roles | ❌ | ❌ | ✅ | ✅ |
| Remove members | ❌ | ❌ | ✅ | ✅ |
| Activate/deactivate modules | ❌ | ❌ | ✅ | ✅ |
| Update workspace settings | ❌ | ❌ | ✅ | ✅ |
| Deactivate workspace | ❌ | ❌ | ❌ | ✅ |
| Change billing plan | ❌ | ❌ | ❌ | ✅ |
| Delete workspace | ❌ | ❌ | ❌ | ✅ |

---

## Invitation Flow

```
1. Admin sends invite: POST /workspace/invite { email, role }
2. Server creates invitations row with:
   - unique token (UUID)
   - expires_at = NOW() + 48 hours
3. Server sends email to invitee with link:
   https://platform.com/accept-invite?token=<uuid>
4. Invitee clicks link, lands on Accept Invite page
5. If invitee has no account → shown registration form
6. If invitee has account → shown login form
7. After auth, server:
   - Validates token hasn't expired
   - Creates tenant_members row: { tenant_id, user_id, role }
   - Marks invitation as accepted
8. Invitee is redirected to the workspace
```

---

## Security Considerations

- Passwords hashed with **bcrypt** (cost factor 12) — never stored in plain text
- Access tokens stored in **memory only** — never in localStorage or sessionStorage (XSS protection)
- Refresh tokens stored in **HttpOnly cookies** — inaccessible to JavaScript (XSS protection)
- All API endpoints use **HTTPS** in production (MITM protection)
- `tenant_id` always comes from the **verified JWT**, never from the request body (prevents tenant spoofing)
- Invitation tokens expire after **48 hours**
- Failed login attempts should be rate-limited (5 attempts per 15 minutes per IP)
- Refresh tokens are **rotated** on each use — old token is invalidated when a new one is issued
