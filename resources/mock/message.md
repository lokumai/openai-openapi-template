## Result
|status|count|
|---|---|
|active|100|
|cancelled|30|
|pending|40|
|passive|150|

## Explanation
This result represents the number of active, cancelled, pending and passive customers in the year 2025. This is a mock result for the question "How many customers are active, cancelled, pending and passive in the year 2025?"

## Query
```sql
SELECT status, COUNT(*) FROM customers WHERE year = 2025 GROUP BY status;
```
