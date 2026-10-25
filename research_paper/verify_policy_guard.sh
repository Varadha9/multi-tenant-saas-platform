#!/usr/bin/env bash
# ==============================================================================
# NexusOps RLS Catalog Guard & Negative Policy Mutation Verification Suite
# Paper: "Dual-Layer Tenant Isolation in Shared-Schema SaaS:
#         Combining ORM Filters with PostgreSQL Row-Level Security"
# Authors: Ibrahim Poonawala, Varad Mandhare, Tanmay Shinde, Prof. Reetika Kerketta
# ==============================================================================

set -euo pipefail

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5433}"
DB_NAME="${DB_NAME:-nexusops}"
OWNER_USER="${OWNER_USER:-nexusops_owner}"
OWNER_PASSWORD="${OWNER_PASSWORD:-nexusops_owner_local}"
APP_USER="${APP_USER:-nexusops_app}"
APP_PASSWORD="${APP_PASSWORD:-nexusops_app_local}"

export PGPASSWORD="${OWNER_PASSWORD}"

echo "=============================================================================="
echo "    NEXUSOPS RLS CATALOG GUARD: MUTATION & EXPRESSION VERIFICATION"
echo "=============================================================================="

# 1. Check database connectivity
if ! pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" >/dev/null 2>&1; then
    echo "[!] PostgreSQL is not responding on ${DB_HOST}:${DB_PORT}."
    echo "    Start the database container using: docker compose -f ../infra/docker/docker-compose.yml up -d postgres"
    echo "    or specify custom DB_HOST and DB_PORT environment variables."
    exit 1
fi

echo "[+] Connected to PostgreSQL at ${DB_HOST}:${DB_PORT}/${DB_NAME} as ${OWNER_USER}"

PROBE_TABLE="test_rls_mutation_probe"
PROBE_VIEW="test_rls_mutation_view"
PASSED_TESTS=0
TOTAL_TESTS=16

# Canonical AST string expected by catalog decompiler
CANONICAL_EXPR="(tenant_id = (NULLIF(current_setting(''app.tenant_id''::text, true), ''''::text))::uuid)"

# Helper function to check if probe table passes guard
check_guard() {
    local violations
    violations=$(PGPASSWORD="${APP_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${APP_USER}" -d "${DB_NAME}" -t -A -c "
        SELECT c.relname
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_policy p ON p.polrelid = c.oid AND p.polname = 'tenant_isolation' AND p.polcmd = '*'
        WHERE n.nspname = 'public' AND c.relname = '${PROBE_TABLE}'
          AND (
               NOT c.relrowsecurity
            OR NOT c.relforcerowsecurity
            OR p.polname IS NULL
            OR NOT p.polpermissive
            OR pg_get_expr(p.polqual, p.polrelid) IS DISTINCT FROM '${CANONICAL_EXPR}'
            OR pg_get_expr(p.polwithcheck, p.polrelid) IS DISTINCT FROM '${CANONICAL_EXPR}'
            OR (SELECT count(*) FROM pg_policy WHERE polrelid = c.oid) != 1
          );
    ")
    if [[ -n "${violations}" ]]; then
        echo "REJECTED"
    else
        echo "ACCEPTED"
    fi
}

check_view_guard() {
    local view_violations
    view_violations=$(PGPASSWORD="${APP_PASSWORD}" psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${APP_USER}" -d "${DB_NAME}" -t -A -c "
        SELECT c.relname
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relkind = 'v' AND c.relname = '${PROBE_VIEW}'
          AND NOT ('security_invoker=true' = ANY(COALESCE(c.reloptions, ARRAY[]::text[]))
               OR 'security_invoker=on' = ANY(COALESCE(c.reloptions, ARRAY[]::text[])));
    ")
    if [[ -n "${view_violations}" ]]; then
        echo "REJECTED"
    else
        echo "ACCEPTED"
    fi
}

cleanup() {
    psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
        DROP VIEW IF EXISTS ${PROBE_VIEW} CASCADE;
        DROP TABLE IF EXISTS ${PROBE_TABLE} CASCADE;
    " >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    CREATE TABLE ${PROBE_TABLE} (id UUID PRIMARY KEY, tenant_id UUID NOT NULL, name TEXT);
    GRANT SELECT, INSERT, UPDATE, DELETE ON ${PROBE_TABLE} TO ${APP_USER};
" >/dev/null

echo ""
echo "--- Running Deliberate Unsafe Policy Mutation Probes ---"

# Mutation 1: No RLS enabled
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 1: Table without RLS enabled -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 1: Table without RLS enabled was erroneously accepted!"
fi

# Mutation 2: RLS enabled but NOT forced
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    ALTER TABLE ${PROBE_TABLE} ENABLE ROW LEVEL SECURITY;
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE}
      USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid)
      WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 2: Table without FORCE ROW LEVEL SECURITY -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 2: Table without FORCE ROW LEVEL SECURITY was erroneously accepted!"
fi

# Mutation 3: FORCE RLS, but WITH CHECK (true) permissive insertion bypass
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    ALTER TABLE ${PROBE_TABLE} FORCE ROW LEVEL SECURITY;
    DROP POLICY tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE}
      USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid)
      WITH CHECK (true);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 3: Permissive 'WITH CHECK (true)' expression -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 3: Permissive 'WITH CHECK (true)' was erroneously accepted!"
fi

# Mutation 4: FORCE RLS, but USING (true) permissive read bypass
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE}
      USING (true)
      WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 4: Permissive 'USING (true)' expression -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 4: Permissive 'USING (true)' was erroneously accepted!"
fi

# Mutation 5: Missing WITH CHECK clause entirely
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE}
      USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 5: Omitted WITH CHECK clause -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 5: Omitted WITH CHECK clause was erroneously accepted!"
fi

# Mutation 6: Secondary permissive policy injection
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE}
      USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid)
      WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid);
    CREATE POLICY extra_permissive ON ${PROBE_TABLE} USING (true);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 6: Secondary permissive policy injection -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 6: Secondary permissive policy was erroneously accepted!"
fi

# Mutation 7: Wrong tenant column in policy
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY extra_permissive ON ${PROBE_TABLE};
    DROP POLICY tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE}
      USING (name = current_setting('app.tenant_id', true))
      WITH CHECK (name = current_setting('app.tenant_id', true));
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 7: Policy predicate targeting wrong attribute -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 7: Policy predicate targeting wrong attribute was erroneously accepted!"
fi

# Mutation 8: Policy omitting NULLIF fallback
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE}
      USING (tenant_id = current_setting('app.tenant_id')::uuid)
      WITH CHECK (tenant_id = current_setting('app.tenant_id')::uuid);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 8: Non-canonical predicate omitting NULLIF -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 8: Non-canonical predicate was erroneously accepted!"
fi

# Mutation 9: RESTRICTIVE policy without permissive base
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE} AS RESTRICTIVE
      USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid)
      WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 9: RESTRICTIVE policy without permissive base -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 9: RESTRICTIVE policy without permissive base was erroneously accepted!"
fi

# Mutation 10: View created without security_invoker
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    CREATE VIEW ${PROBE_VIEW} AS SELECT * FROM ${PROBE_TABLE};
" >/dev/null
res=$(check_view_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 10: View created without security_invoker -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 10: View created without security_invoker was erroneously accepted!"
fi

# Mutation 11: Policy restricted to FOR SELECT only (missing write coverage)
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY IF EXISTS tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE} FOR SELECT
      USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 11: Policy restricted to FOR SELECT only -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 11: FOR SELECT only policy was erroneously accepted!"
fi

# Mutation 12: Policy restricted to FOR INSERT only (missing read coverage)
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY IF EXISTS tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE} FOR INSERT
      WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 12: Policy restricted to FOR INSERT only -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 12: FOR INSERT only policy was erroneously accepted!"
fi

# Mutation 13: Permissive 'OR true' in USING clause
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY IF EXISTS tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE}
      USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid OR true)
      WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 13: Permissive 'OR true' inside USING clause -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 13: Permissive 'OR true' in USING clause was erroneously accepted!"
fi

# Mutation 14: Permissive 'OR true' in WITH CHECK clause
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY IF EXISTS tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE}
      USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid)
      WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid OR true);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 14: Permissive 'OR true' inside WITH CHECK clause -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 14: Permissive 'OR true' in WITH CHECK clause was erroneously accepted!"
fi

# Mutation 15: Policy with hardcoded UUID literal instead of session setting
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY IF EXISTS tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE}
      USING (tenant_id = 'a0000000-0000-0000-0000-000000000001'::uuid)
      WITH CHECK (tenant_id = 'a0000000-0000-0000-0000-000000000001'::uuid);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 15: Hardcoded UUID literal bypassing GUC -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 15: Hardcoded UUID literal policy was erroneously accepted!"
fi

# Mutation 16: Policy with wrong session variable name
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY IF EXISTS tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE}
      USING (tenant_id = nullif(current_setting('app.wrong_setting', true), '')::uuid)
      WITH CHECK (tenant_id = nullif(current_setting('app.wrong_setting', true), '')::uuid);
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 16: Wrong session variable name in GUC decompiler -> DETECTED & BLOCKED"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "[FAIL] Mutation 16: Wrong session variable policy was erroneously accepted!"
fi

# Safe Baseline Verification
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP VIEW ${PROBE_VIEW};
    CREATE VIEW ${PROBE_VIEW} WITH (security_invoker = true) AS SELECT * FROM ${PROBE_TABLE};
    DROP POLICY tenant_isolation ON ${PROBE_TABLE};
    CREATE POLICY tenant_isolation ON ${PROBE_TABLE}
      USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid)
      WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid);
" >/dev/null
res_table=$(check_guard)
res_view=$(check_view_guard)
if [[ "${res_table}" == "ACCEPTED" && "${res_view}" == "ACCEPTED" ]]; then
    echo "[PASS] Baseline: Strict Canonical RLS Policy + security_invoker View -> VALIDATED (CLEAN)"
else
    echo "[FAIL] Baseline: Strict Canonical RLS Policy was rejected unexpectedly!"
fi

echo ""
pct=$(( PASSED_TESTS * 100 / TOTAL_TESTS ))
echo "=============================================================================="
echo "    MUTATION TESTING SUMMARY: ${PASSED_TESTS}/${TOTAL_TESTS} VULNERABILITIES DETECTED (${pct}%)"
echo "=============================================================================="
if [[ "${PASSED_TESTS}" -eq "${TOTAL_TESTS}" ]]; then
    echo "[SUCCESS] The PostgreSQL catalog guard prevents all evaluated RLS misconfigurations."
    exit 0
else
    echo "[FAILURE] Some RLS misconfigurations were not detected."
    exit 1
fi
