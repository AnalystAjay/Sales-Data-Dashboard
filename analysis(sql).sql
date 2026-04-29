USE database_retail;
SHOW GRANTS FOR 'user1'@'localhost';

/*Q1. How can you calculate total sales using Year and Country filters?*/

SELECT year, country, SUM(sales) AS total_sales
FROM sales_data
GROUP BY year, country
ORDER BY year;

/*Q2. How can you analyze month-wise sales trends with proper sorting?*/

SELECT year, month_name, SUM(sales) AS total_sales
FROM sales_data
GROUP BY year, month_name
ORDER BY year;

/*Q3. How can you find the top-performing product in each country?*/

SELECT country, productline, SUM(sales) AS total_sales
FROM sales_data
GROUP BY country, productline
ORDER BY country, total_sales DESC;

/*Q4. How can you classify products as high or low performing?*/

SELECT productline,
       SUM(sales) AS total_sales,
       CASE 
           WHEN SUM(sales) > 500000 THEN 'High'
           ELSE 'Low'
       END AS performance
FROM sales_data
GROUP BY productline;

/*Q5. How can you identify repeat and one-time customers?*/

SELECT 
    CASE 
        WHEN COUNT(ordernumber) > 1 THEN 'Repeat'
        ELSE 'One-time'
    END AS customer_type,
    COUNT(*) AS total_customers
FROM sales_data
GROUP BY customername;

/*Q6. How can you find the top 5 customers in each country?*/

SELECT country, customername, SUM(sales) AS total_spent
FROM sales_data
GROUP BY country, customername
ORDER BY country, total_spent DESC;

/*Q7. How can you find the best city in each country based on sales?*/

SELECT country, city, SUM(sales) AS total_sales
FROM sales_data
GROUP BY country, city
ORDER BY country, total_sales DESC;

/*Q8. How can you compare territory-wise sales growth over years?*/

SELECT territory, year, SUM(sales) AS total_sales
FROM sales_data
GROUP BY territory, year;

/*Q9. How can you calculate profit margin for each product?*/

SELECT productline,SUM(estimated_profit)/SUM(sales)*100 AS profit_margin
FROM sales_data
GROUP BY productline;

/*Q10. How can you analyze cancelled vs shipped orders?*/

SELECT status, COUNT(*) AS total_orders
FROM sales_data
GROUP BY status;

/*Q11. How can you calculate year-over-year sales growth? */

SELECT year,
    SUM(sales) AS total_sales,
    LAG(SUM(sales)) OVER (ORDER BY year) AS prev_sales
FROM sales_data
GROUP BY year;

/*Q12. How can you analyze seasonal sales trends (quarter-wise)? */

SELECT CASE WHEN month_id IN (1,2,3) THEN 'Q1'
        WHEN month_id IN (4,5,6) THEN 'Q2'
        WHEN month_id IN (7,8,9) THEN 'Q3'
        ELSE 'Q4'
    END AS quarter,
    SUM(sales) AS total_sales
FROM sales_data
GROUP BY quarter;
