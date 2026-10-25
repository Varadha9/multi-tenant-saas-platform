\set tenant_num random(1, 100)
\set id (:tenant_num - 1) * 10000 + random(1, 10000)
BEGIN;
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
SELECT id, tenant_id, name, email FROM bench_rls WHERE id = :id AND tenant_id = md5(:tenant_num::text)::uuid;
COMMIT;
