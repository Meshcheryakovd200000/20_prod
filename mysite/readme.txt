Проверка, например:
http://127.0.0.1:8000/shop/users/11/orders/export/

результат:

{"user": {"id": 11, "username": "irina_romanova", "first_name": "Ирина", "last_name": "Романова", "email": "irina@example.com", "is_staff": false, 
"is_active": true, "date_joined": "2026-02-03T01:32:55.031104+00:00"}, "orders": [], "metadata": {"total_orders": 0, "total_products": 0, 
"generated_at": "2026-02-03T01:47:49.188480+00:00", "cache_key": "user_orders_export_v2_11", "cache_ttl": 120, "cache_strategy": "low_level_api"}}
