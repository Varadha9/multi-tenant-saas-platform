\set id random(1, 250000)
BEGIN;
SELECT set_config('app.tenant_id', md5('1'), true);
SELECT id, tenant_id, name FROM bench_skew_rls WHERE id = :id AND tenant_id = md5('1')::uuid;
COMMIT;
