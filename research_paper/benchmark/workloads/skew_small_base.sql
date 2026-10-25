\set id random(999501, 1000000)
BEGIN;
SELECT id, tenant_id, name FROM bench_skew_filter WHERE id = :id AND tenant_id = md5('100')::uuid;
COMMIT;
