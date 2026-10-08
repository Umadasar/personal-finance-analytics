-- =============================================
-- BUSINESS ANALYSIS
-- =============================================


-- ---------------------------------------------
-- 1. Expense distribution by category
-- ---------------------------------------------

WITH CATEGORY_TOTALS AS (
    SELECT
        CATEGORY,
        SUM(AMOUNT) AS TOTAL_EXPENSE
    FROM PERSONAL_FINANCE_DB.RAW.TRANSACTIONS
    WHERE TYPE = 'Expense'
    GROUP BY CATEGORY
)

SELECT
    CATEGORY,
    TOTAL_EXPENSE,

    ROUND(
        TOTAL_EXPENSE * 100
        / NULLIF(SUM(TOTAL_EXPENSE) OVER (), 0),
        2
    ) AS PERCENT_OF_TOTAL,

    RANK() OVER (
        ORDER BY TOTAL_EXPENSE DESC
    ) AS EXPENSE_RANK

FROM CATEGORY_TOTALS

ORDER BY TOTAL_EXPENSE DESC;


-- ---------------------------------------------
-- 2. Top 3 expense categories per month
-- ---------------------------------------------

SELECT
    *,
    RANK() OVER (
        PARTITION BY YEAR, MONTH
        ORDER BY TOTAL_EXPENSE DESC
    ) AS EXPENSE_RANK

FROM PERSONAL_FINANCE_DB.ANALYTICS.CATEGORY_SPENDING

QUALIFY EXPENSE_RANK <= 3;


-- ---------------------------------------------
-- 3. Monthly savings rate
-- ---------------------------------------------

SELECT
    YEAR,
    MONTH,
    TOTAL_INCOME,
    TOTAL_EXPENSES,
    NET_SAVINGS,

    ROUND(
        NET_SAVINGS * 100
        / NULLIF(TOTAL_INCOME, 0),
        2
    ) AS SAVINGS_RATE_PERCENT

FROM PERSONAL_FINANCE_DB.ANALYTICS.MONTHLY_SUMMARY

ORDER BY YEAR, MONTH;


-- ---------------------------------------------
-- 4. Monthly savings-rate comparison
-- ---------------------------------------------

WITH SAVINGS AS (
    SELECT
        YEAR,
        MONTH,

        ROUND(
            NET_SAVINGS * 100
            / NULLIF(TOTAL_INCOME, 0),
            2
        ) AS SAVINGS_RATE_PERCENT

    FROM PERSONAL_FINANCE_DB.ANALYTICS.MONTHLY_SUMMARY
)

SELECT
    *,

    LAG(SAVINGS_RATE_PERCENT)
        OVER (ORDER BY YEAR, MONTH)
        AS PREV_MONTH_SAVINGS_RATE,

    SAVINGS_RATE_PERCENT
    -
    LAG(SAVINGS_RATE_PERCENT)
        OVER (ORDER BY YEAR, MONTH)
        AS CHANGE_SAVINGS_RATE

FROM SAVINGS

ORDER BY YEAR, MONTH;


-- ---------------------------------------------
-- 5. Annual financial summary
-- ---------------------------------------------

SELECT
    YEAR,

    SUM(TOTAL_INCOME) AS ANNUAL_INCOME,

    SUM(TOTAL_EXPENSES) AS ANNUAL_EXPENSES,

    SUM(NET_SAVINGS) AS ANNUAL_NET_SAVINGS,

    ROUND(
        SUM(NET_SAVINGS) * 100
        / NULLIF(SUM(TOTAL_INCOME), 0),
        2
    ) AS ANNUAL_SAVINGS_RATE

FROM PERSONAL_FINANCE_DB.ANALYTICS.MONTHLY_SUMMARY

GROUP BY YEAR

ORDER BY YEAR;


-- ---------------------------------------------
-- 6. Year-over-Year financial performance
-- ---------------------------------------------

WITH ANNUAL AS (
    SELECT
        YEAR,
        SUM(TOTAL_INCOME) AS ANNUAL_INCOME,
        SUM(TOTAL_EXPENSES) AS ANNUAL_EXPENSES,
        SUM(NET_SAVINGS) AS ANNUAL_NET_SAVINGS

    FROM PERSONAL_FINANCE_DB.ANALYTICS.MONTHLY_SUMMARY

    GROUP BY YEAR
),

YOY AS (
    SELECT
        *,

        LAG(ANNUAL_INCOME)
            OVER (ORDER BY YEAR) AS PREV_YEAR_INCOME,

        LAG(ANNUAL_EXPENSES)
            OVER (ORDER BY YEAR) AS PREV_YEAR_EXPENSES,

        LAG(ANNUAL_NET_SAVINGS)
            OVER (ORDER BY YEAR) AS PREV_YEAR_NET_SAVINGS

    FROM ANNUAL
)

SELECT
    YEAR,
    ANNUAL_INCOME,
    ANNUAL_EXPENSES,
    ANNUAL_NET_SAVINGS,

    ROUND(
        (ANNUAL_INCOME - PREV_YEAR_INCOME) * 100
        / NULLIF(PREV_YEAR_INCOME, 0),
        2
    ) AS INCOME_YOY_PERCENT,

    ROUND(
        (ANNUAL_EXPENSES - PREV_YEAR_EXPENSES) * 100
        / NULLIF(PREV_YEAR_EXPENSES, 0),
        2
    ) AS EXPENSE_YOY_PERCENT,

    ROUND(
        (ANNUAL_NET_SAVINGS - PREV_YEAR_NET_SAVINGS) * 100
        / NULLIF(PREV_YEAR_NET_SAVINGS, 0),
        2
    ) AS SAVINGS_YOY_PERCENT

FROM YOY

ORDER BY YEAR;