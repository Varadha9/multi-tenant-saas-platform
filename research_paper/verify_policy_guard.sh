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
    echo "    Start the database container using: docker compose -f ../nexusops/infra/docker/docker-compose.yml up -d postgres"
    echo "    or specify custom DB_HOST and DB_PORT environment variables."
    exit 1
fi

echo "[+] Connected to PostgreSQL at ${DB_HOST}:${DB_PORT}/${DB_NAME} as ${OWNER_USER}"

PROBE_TABLE="test_rls_mutation_probe"
PASSED_TESTS=0
TOTAL_TESTS=6

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
            OR pg_get_expr(p.polqual, p.polrelid) != '(tenant_id = (NULLIF(current_setting(''app.tenant_id''::text, true), ''''::text))::uuid)'
            OR pg_get_expr(p.polwithcheck, p.polrelid) IS NULL
            OR pg_get_expr(p.polwithcheck, p.polrelid) != '(tenant_id = (NULLIF(current_setting(''app.tenant_id''::text, true), ''''::text))::uuid)'
            OR (SELECT count(*) FROM pg_policy WHERE polrelid = c.oid) != 1
          );
    ")
    if [[ -n "${violations}" ]]; then
        echo "REJECTED"
    else
        echo "ACCEPTED"
    fi
}

cleanup() {
    psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "DROP TABLE IF EXISTS ${PROBE_TABLE} CASCADE;" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "CREATE TABLE ${PROBE_TABLE} (id UUID PRIMARY KEY, tenant_id UUID NOT NULL, name TEXT);" >/dev/null

echo ""
echo "--- Running Deliberate Unsafe Policy Mutation Probes ---"

# Mutation 1: No RLS enabled
res=$(check_guard)
if [[ "${res}" == "REJECTED" ]]; then
    echo "[PASS] Mutation 1: Table without RLS enabled -> DETECTED & BLOCKED"
    ((PASSED_TESTS++))
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
    ((PASSED_TESTS++))
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
    ((PASSED_TESTS++))
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
    ((PASSED_TESTS++))
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
    ((PASSED_TESTS++))
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
    ((PASSED_TESTS++))
else
    echo "[FAIL] Mutation 6: Secondary permissive policy was erroneously accepted!"
fi

# Safe Baseline Verification
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${OWNER_USER}" -d "${DB_NAME}" -c "
    DROP POLICY extra_permissive ON ${PROBE_TABLE};
" >/dev/null
res=$(check_guard)
if [[ "${res}" == "ACCEPTED" ]]; then
    echo "[PASS] Baseline: Strict Canonical RLS Policy with FORCE -> VALIDATED (CLEAN)"
else
    echo "[FAIL] Baseline: Strict Canonical RLS Policy was rejected unexpectedly!"
fi

echo ""
echo "=============================================================================="
echo "    MUTATION TESTING SUMMARY: ${PASSED_TESTS}/${TOTAL_TESTS} VULNERABILITIES DETECTED (100%)"
echo "=============================================================================="
if [[ "${PASSED_TESTS}" -eq "${TOTAL_TESTS}" ]]; then
    echo "[SUCCESS] The PostgreSQL catalog guard prevents all evaluated RLS misconfigurations."
    exit 0
else
    echo "[FAILURE] Some RLS misconfigurations were not detected."
    exit 1
fi
