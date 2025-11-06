# Performance Notes

## Indexing Strategy

To optimize query performance, we've implemented the following indexing strategy in MySQL:

### B-tree Indexes

1. `customers.mobile_number` - For fast customer lookups
2. `orders.mobile_number` - For joining customers and orders
3. `orders.order_date_time` - For date range queries
4. `customers.region` - For regional aggregations

### Composite Indexes

1. `(mobile_number, order_date_time)` - For efficient joins and date filtering

## EXPLAIN Analysis

### Repeat Customers Query

```sql
EXPLAIN SELECT c.customer_id, c.customer_name, c.mobile_number, c.region, COUNT(o.order_id) as order_count
FROM customers c
JOIN orders o ON c.mobile_number = o.mobile_number
GROUP BY c.customer_id, c.customer_name, c.mobile_number, c.region
HAVING COUNT(o.order_id) > 1
ORDER BY order_count DESC;
```

**Result:**
- Uses index on `orders.mobile_number` for JOIN
- Uses GROUP BY optimization
- Efficient for finding repeat customers

### Monthly Order Trends Query

```sql
EXPLAIN SELECT YEAR(order_date_time) as year, MONTH(order_date_time) as month, 
COUNT(order_id) as order_count, SUM(total_amount) as total_revenue
FROM orders
GROUP BY YEAR(order_date_time), MONTH(order_date_time)
ORDER BY year, month;
```

**Result:**
- Uses index on `orders.order_date_time` for GROUP BY
- Efficient aggregation with date functions

### Regional Revenue Query

```sql
EXPLAIN SELECT c.region, 
COUNT(DISTINCT c.customer_id) as customer_count,
COUNT(o.order_id) as order_count,
SUM(o.total_amount) as total_revenue,
AVG(o.total_amount) as avg_order_value
FROM customers c
JOIN orders o ON c.mobile_number = o.mobile_number
GROUP BY c.region
ORDER BY total_revenue DESC;
```

**Result:**
- Uses indexes on both `customers.region` and `orders.mobile_number`
- Efficient JOIN and aggregation

## Optimization Rationale

1. **Mobile Number Indexes**: Critical for JOIN operations between customers and orders
2. **Date Indexes**: Essential for time-series analysis and filtering
3. **Region Indexes**: Speed up regional aggregations
4. **Composite Indexes**: Optimize common query patterns that filter on multiple columns

## Performance Recommendations

1. Monitor query performance regularly with `EXPLAIN`
2. Consider partitioning large tables by date for historical data
3. Use connection pooling for database connections
4. Cache frequently accessed KPIs in memory or Redis
5. Consider read replicas for analytical queries