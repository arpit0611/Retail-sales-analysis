-- Optional SQL exercises for SQLite.
-- First import retail_sales.csv into a table called retail_sales (e.g., using DB Browser for SQLite).
-- Raw CSV includes exact duplicates, so use DISTINCT in a subquery for comparability.

-- 1. Unique orders
SELECT COUNT(DISTINCT Order_ID) AS orders FROM retail_sales;

-- 2. Revenue by category (null discounts assumed 0; matches the Python cleaning rule)
SELECT Category,
       ROUND(SUM(Quantity * Unit_Price_INR * (1 - COALESCE(Discount_Pct, 0) / 100.0)), 2) AS revenue_inr
FROM (SELECT DISTINCT * FROM retail_sales)
GROUP BY Category
ORDER BY revenue_inr DESC;

-- 3. Orders by payment method
SELECT Payment_Method, COUNT(*) AS orders
FROM (SELECT DISTINCT * FROM retail_sales)
GROUP BY Payment_Method
ORDER BY orders DESC;

-- 4. Revenue by month
SELECT substr(Order_Date, 1, 7) AS month,
       ROUND(SUM(Quantity * Unit_Price_INR * (1 - COALESCE(Discount_Pct, 0) / 100.0)), 2) AS revenue_inr
FROM (SELECT DISTINCT * FROM retail_sales)
GROUP BY month
ORDER BY month;
