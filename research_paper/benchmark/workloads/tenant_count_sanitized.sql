\set tenant_num random(1, 100)
BEGIN;
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
SELECT count(*) FROM bench_filter WHERE tenant_id = md5(:tenant_num::text)::uuid;
COMMIT;
