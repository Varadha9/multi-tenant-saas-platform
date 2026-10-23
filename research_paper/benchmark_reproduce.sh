#!/usr/bin/env bash
# ==============================================================================
# NexusOps Multi-Tenant Isolation Benchmark Reproduction Suite
# Paper: "Dual-Layer Tenant Isolation in Shared-Schema SaaS:
#         Combining ORM Filters with PostgreSQL Row-Level Security"
# Authors: Ibrahim Poonawala, Varad Mandhare, Tanmay Shinde, Prof. Reetika Kerketta
# ==============================================================================

set -euo pipefail

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5433}"
DB_USER="${DB_USER:-nexusops_app}"
DB_NAME="${DB_NAME:-nexusops}"
PGPASSWORD="${PGPASSWORD:-nexusops_app_local}"
export PGPASSWORD

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCH_DIR="${SCRIPT_DIR}/benchmark"
mkdir -p "${BENCH_DIR}"

echo "=== 1. Initializing Benchmark Schema & 1,000,000 Rows ==="
PGPASSWORD=nexusops_owner_local psql -h "${DB_HOST}" -p "${DB_PORT}" -U nexusops_owner -d "${DB_NAME}" << 'EOSQL'
DROP TABLE IF EXISTS bench_filter CASCADE;
DROP TABLE IF EXISTS bench_rls CASCADE;

-- 1. Variant A: Filter-Only Baseline Table (No RLS)
CREATE TABLE bench_filter (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_bench_filter_tenant_name ON bench_filter(tenant_id, name);

-- 2. Variant B: Forced RLS Table (Permissive Policy with WITH CHECK)
CREATE TABLE bench_rls (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_bench_rls_tenant_name ON bench_rls(tenant_id, name);

ALTER TABLE bench_rls ENABLE ROW LEVEL SECURITY;
ALTER TABLE bench_rls FORCE ROW LEVEL SECURITY;

-- Production-aligned permissive policy for nexusops_app (pure equality on tenant_id)
CREATE POLICY tenant_isolation ON bench_rls
  FOR ALL TO nexusops_app
  USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid)
  WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid);

-- Grant privileges to runtime role
GRANT SELECT, INSERT, UPDATE, DELETE ON bench_filter TO nexusops_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON bench_rls TO nexusops_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nexusops_app;

-- Seed 1,000,000 rows partitioned across 100 deterministic tenants (10,000 rows each)
DO $$
DECLARE
    t INT;
    tid UUID;
BEGIN
    FOR t IN 1..100 LOOP
        tid := md5(t::text)::uuid;
        INSERT INTO bench_filter (tenant_id, name, email)
        SELECT 
            tid,
            'Contact ' || (t * 10000 + s),
            'contact_' || s || '@tenant' || t || '.test'
        FROM generate_series(1, 10000) AS s;
    END LOOP;
END $$;

INSERT INTO bench_rls SELECT * FROM bench_filter;
VACUUM ANALYZE bench_filter;
VACUUM ANALYZE bench_rls;
EOSQL

echo "=== 2. Creating Transaction-Scoped pgbench Workload Scripts ==="
# Workload 1: Point Lookup
# Variant 1: Filter Baseline
cat << 'EOF_SQL' > "${BENCH_DIR}/point_lookup_filter.sql"
\set tenant_num random(1, 100)
\set id random(1, 1000000)
BEGIN;
SELECT id, tenant_id, name, email FROM bench_filter WHERE id = :id AND tenant_id = md5(:tenant_num::text)::uuid;
COMMIT;
EOF_SQL

# Variant 2: Filter + Sanitization GUC
cat << 'EOF_SQL' > "${BENCH_DIR}/point_lookup_sanitized.sql"
\set tenant_num random(1, 100)
\set id random(1, 1000000)
BEGIN;
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
SELECT id, tenant_id, name, email FROM bench_filter WHERE id = :id AND tenant_id = md5(:tenant_num::text)::uuid;
COMMIT;
EOF_SQL

# Variant 3: Dual-Layer (Filter + Forced RLS)
cat << 'EOF_SQL' > "${BENCH_DIR}/point_lookup_dual.sql"
\set tenant_num random(1, 100)
\set id random(1, 1000000)
BEGIN;
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
SELECT id, tenant_id, name, email FROM bench_rls WHERE id = :id AND tenant_id = md5(:tenant_num::text)::uuid;
COMMIT;
EOF_SQL

# Workload 2: Paged List (Keyset pagination at randomized start key)
cat << 'EOF_SQL' > "${BENCH_DIR}/paged_list_filter.sql"
\set tenant_num random(1, 100)
\set start_num random(1, 9800)
BEGIN;
SELECT id, name, email FROM bench_filter WHERE tenant_id = md5(:tenant_num::text)::uuid AND name >= ('Contact ' || :start_num) ORDER BY name LIMIT 20;
COMMIT;
EOF_SQL

cat << 'EOF_SQL' > "${BENCH_DIR}/paged_list_dual.sql"
\set tenant_num random(1, 100)
\set start_num random(1, 9800)
BEGIN;
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
SELECT id, name, email FROM bench_rls WHERE tenant_id = md5(:tenant_num::text)::uuid AND name >= ('Contact ' || :start_num) ORDER BY name LIMIT 20;
COMMIT;
EOF_SQL

# Workload 3: Tenant Count
cat << 'EOF_SQL' > "${BENCH_DIR}/tenant_count_filter.sql"
\set tenant_num random(1, 100)
BEGIN;
SELECT count(*) FROM bench_filter WHERE tenant_id = md5(:tenant_num::text)::uuid;
COMMIT;
EOF_SQL

cat << 'EOF_SQL' > "${BENCH_DIR}/tenant_count_dual.sql"
\set tenant_num random(1, 100)
BEGIN;
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
SELECT count(*) FROM bench_rls WHERE tenant_id = md5(:tenant_num::text)::uuid;
COMMIT;
EOF_SQL

# Workload 4: Point Insert
cat << 'EOF_SQL' > "${BENCH_DIR}/point_insert_filter.sql"
\set tenant_num random(1, 100)
\set s random(1000001, 9999999)
BEGIN;
INSERT INTO bench_filter (tenant_id, name, email) VALUES (md5(:tenant_num::text)::uuid, 'New User ' || :s, 'new_' || :s || '@tenant.test');
COMMIT;
EOF_SQL

cat << 'EOF_SQL' > "${BENCH_DIR}/point_insert_dual.sql"
\set tenant_num random(1, 100)
\set s random(1000001, 9999999)
BEGIN;
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
INSERT INTO bench_rls (tenant_id, name, email) VALUES (md5(:tenant_num::text)::uuid, 'New User ' || :s, 'new_' || :s || '@tenant.test');
COMMIT;
EOF_SQL

echo "=== 3. Benchmark Protocol Ready (8 clients, 4 threads, 30s, 30 paired runs) ==="
echo "Workloads: Point Lookup, Paged List, Tenant Count, Point Insert"
echo "All scripts and RLS schemas generated at ${BENCH_DIR}."
chmod +x "${SCRIPT_DIR}/benchmark_reproduce.sh"
