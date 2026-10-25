\set id random(999501, 1000000)
BEGIN;
SELECT set_config('app.tenant_id', md5('100'), true);
SELECT id, tenant_id, name FROM bench_skew_rls WHERE id = :id AND tenant_id = md5('100')::uuid;
COMMIT;
