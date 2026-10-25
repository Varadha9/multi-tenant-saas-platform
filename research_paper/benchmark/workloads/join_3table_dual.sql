\set tenant_num random(1, 100)
\set order_id (:tenant_num - 1) * 1000 + random(1, 1000)
BEGIN;
SELECT set_config('app.tenant_id', md5(:tenant_num::text), true);
SELECT o.id, o.order_num, i.item_name, p.amount_cents, p.status
FROM bench_rls_orders o
JOIN bench_rls_order_items i ON i.tenant_id = o.tenant_id AND i.order_id = o.id
JOIN bench_rls_order_payments p ON p.tenant_id = o.tenant_id AND p.order_id = o.id
WHERE o.tenant_id = md5(:tenant_num::text)::uuid AND o.id = :order_id;
COMMIT;
