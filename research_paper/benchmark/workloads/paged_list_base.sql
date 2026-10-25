\set tenant_num random(1, 100)
\set start_id (:tenant_num - 1) * 10000 + random(1, 9900)
BEGIN;
SELECT id, name, email FROM bench_filter WHERE tenant_id = md5(:tenant_num::text)::uuid AND id >= :start_id ORDER BY id LIMIT 20;
COMMIT;
