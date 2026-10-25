\set tenant_num random(1, 100)
\set s random(1000001, 9999999)
BEGIN;
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
INSERT INTO bench_rls (tenant_id, name, email) VALUES (md5(:tenant_num::text)::uuid, 'New User ' || :s, 'new_' || :s || '@tenant.test');
COMMIT;
