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

-- 1. Variant A: Filter-Only Table (No RLS)
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

CREATE POLICY tenant_isolation ON bench_rls
  FOR ALL TO nexusops_app
  USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid)
  WITH CHECK (tenant_id = nullif(current_setting('app.tenant_id', true), '')::uuid);

-- Grant privileges to runtime role
GRANT SELECT, INSERT, UPDATE, DELETE ON bench_filter TO nexusops_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON bench_rls TO nexusops_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nexusops_app;

-- Seed 1,000,000 rows partitioned across 100 deterministic tenants
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
ANALYZE bench_filter;
ANALYZE bench_rls;
EOSQL

echo "=== 2. Creating pgbench Workload Scripts ==="
cat << 'EOF_SQL' > "${BENCH_DIR}/point_lookup_filter.sql"
\set tenant_num random(1, 100)
\set id random(1, 1000000)
SELECT id, tenant_id, name, email FROM bench_filter WHERE id = :id AND tenant_id = md5(:tenant_num::text)::uuid;
EOF_SQL

cat << 'EOF_SQL' > "${BENCH_DIR}/point_lookup_rls.sql"
\set tenant_num random(1, 100)
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
\set id random(1, 1000000)
SELECT id, tenant_id, name, email FROM bench_rls WHERE id = :id;
EOF_SQL

cat << 'EOF_SQL' > "${BENCH_DIR}/paged_list_filter.sql"
\set tenant_num random(1, 100)
\set offset random(0, 980)
SELECT id, name, email FROM bench_filter WHERE tenant_id = md5(:tenant_num::text)::uuid ORDER BY name LIMIT 20 OFFSET :offset;
EOF_SQL

cat << 'EOF_SQL' > "${BENCH_DIR}/paged_list_rls.sql"
\set tenant_num random(1, 100)
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
\set offset random(0, 980)
SELECT id, name, email FROM bench_rls ORDER BY name LIMIT 20 OFFSET :offset;
EOF_SQL

cat << 'EOF_SQL' > "${BENCH_DIR}/tenant_count_filter.sql"
\set tenant_num random(1, 100)
SELECT count(*) FROM bench_filter WHERE tenant_id = md5(:tenant_num::text)::uuid;
EOF_SQL

cat << 'EOF_SQL' > "${BENCH_DIR}/tenant_count_rls.sql"
\set tenant_num random(1, 100)
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
SELECT count(*) FROM bench_rls;
EOF_SQL

cat << 'EOF_SQL' > "${BENCH_DIR}/point_insert_filter.sql"
\set tenant_num random(1, 100)
\set s random(1000001, 9999999)
INSERT INTO bench_filter (tenant_id, name, email) VALUES (md5(:tenant_num::text)::uuid, 'New User ' || :s, 'new_' || :s || '@tenant.test');
EOF_SQL

cat << 'EOF_SQL' > "${BENCH_DIR}/point_insert_rls.sql"
\set tenant_num random(1, 100)
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
\set s random(1000001, 9999999)
INSERT INTO bench_rls (tenant_id, name, email) VALUES (md5(:tenant_num::text)::uuid, 'New User ' || :s, 'new_' || :s || '@tenant.test');
EOF_SQL

echo "=== 3. Benchmark Protocol Ready (8 clients, 4 threads, 30s, 30 paired runs) ==="
echo "Workloads: Point Lookup, Paged List, Tenant Count, Point Insert"
echo "All scripts and RLS schemas generated at ${BENCH_DIR}."
