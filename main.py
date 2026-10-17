# STEP 0

# SQL Library and Pandas Library
import sqlite3
from pathlib import Path

import pandas as pd

# Connect to the database
conn = sqlite3.connect(Path(__file__).with_name('data.sqlite'))

# STEP 1
df_boston = pd.read_sql("""
    SELECT e.firstName, e.lastName, e.jobTitle
    FROM employees AS e
    JOIN offices AS o ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston'
    ORDER BY e.firstName, e.lastName
""", conn)

# STEP 2
df_zero_emp = pd.read_sql("""
    SELECT o.*
    FROM offices AS o
    LEFT JOIN employees AS e ON o.officeCode = e.officeCode
    WHERE e.employeeNumber IS NULL
""", conn)

# STEP 3
df_employee = pd.read_sql("""
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees AS e
    LEFT JOIN offices AS o ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName
""", conn)

# STEP 4
df_contacts = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName, c.phone,
           c.salesRepEmployeeNumber
    FROM customers AS c
    LEFT JOIN orders AS o ON c.customerNumber = o.customerNumber
    WHERE o.orderNumber IS NULL
    ORDER BY c.contactLastName, c.contactFirstName
""", conn)

# STEP 5
df_payment = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName,
           CAST(p.amount AS REAL) AS amount, p.paymentDate
    FROM customers AS c
    JOIN payments AS p ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS REAL) DESC
""", conn)

# STEP 6
df_credit = pd.read_sql("""
    SELECT e.employeeNumber, e.firstName, e.lastName,
           COUNT(c.customerNumber) AS n_customers
    FROM employees AS e
    JOIN customers AS c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber, e.firstName, e.lastName
    HAVING AVG(CAST(c.creditLimit AS REAL)) > 90000
    ORDER BY n_customers DESC, e.employeeNumber
""", conn)

# STEP 7
df_product_sold = pd.read_sql("""
    SELECT p.productName, COUNT(DISTINCT od.orderNumber) AS numorders,
           SUM(CAST(od.quantityOrdered AS INTEGER)) AS totalunits
    FROM products AS p
    JOIN orderdetails AS od ON p.productCode = od.productCode
    GROUP BY p.productCode, p.productName
    ORDER BY totalunits DESC, p.productCode
""", conn)

# STEP 8
df_total_customers = pd.read_sql("""
    SELECT p.productName, p.productCode,
           COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products AS p
    JOIN orderdetails AS od ON p.productCode = od.productCode
    JOIN orders AS o ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode, p.productName
    ORDER BY numpurchasers DESC, p.productCode
""", conn)

# STEP 9
df_customers = pd.read_sql("""
    SELECT COUNT(c.customerNumber) AS n_customers, o.officeCode, o.city
    FROM offices AS o
    LEFT JOIN employees AS e ON o.officeCode = e.officeCode
    LEFT JOIN customers AS c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY o.officeCode, o.city
    ORDER BY o.officeCode
""", conn)

# STEP 10
df_under_20 = pd.read_sql("""
    WITH underperforming_products AS (
        SELECT od.productCode
        FROM orderdetails AS od
        JOIN orders AS o ON od.orderNumber = o.orderNumber
        GROUP BY od.productCode
        HAVING COUNT(DISTINCT o.customerNumber) < 20
    )
    SELECT DISTINCT e.employeeNumber, e.firstName, e.lastName,
                    office.city, office.officeCode
    FROM employees AS e
    JOIN offices AS office ON e.officeCode = office.officeCode
    JOIN customers AS c ON e.employeeNumber = c.salesRepEmployeeNumber
    JOIN orders AS o ON c.customerNumber = o.customerNumber
    JOIN orderdetails AS od ON o.orderNumber = od.orderNumber
    WHERE od.productCode IN (SELECT productCode FROM underperforming_products)
    ORDER BY e.lastName, e.firstName, e.employeeNumber
""", conn)

conn.close()
