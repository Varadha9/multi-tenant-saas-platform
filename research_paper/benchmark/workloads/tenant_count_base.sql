\set tenant_num random(1, 100)
BEGIN;
SELECT count(*) FROM bench_filter WHERE tenant_id = md5(:tenant_num::text)::uuid;
COMMIT;
