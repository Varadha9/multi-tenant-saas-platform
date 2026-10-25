\set id random(1, 250000)
BEGIN;
SELECT id, tenant_id, name FROM bench_skew_filter WHERE id = :id AND tenant_id = md5('1')::uuid;
COMMIT;
