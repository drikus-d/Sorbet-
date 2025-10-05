WITH base AS (
    SELECT
        IFF(
            r.payment_date >= TO_DATE('{wtd_start_date}') --wtd_start_date
            AND r.payment_date <= TO_DATE('{end_date}'),--end_date
            'CURRENT',
            'PREVIOUS'
        ) AS period,
        c.reporting_center_name AS center,
        -- Dynamically set either item_category (retail) or item_sub_category (service)
        trim(i.item_category_type) AS category,
        trim(i.item_category) as sub_category,
        SUM(r.revenue) AS revenue,
        SUM(r.quantity) AS units,
        iff(itt.item_type_name in ('Day Package Refund', 'Day Package'), true, false) as is_day_package
    FROM
        marts.finance.fact_revenue AS r
    LEFT JOIN marts.finance.dim_item AS i
        ON i.item_id = r.item_id
    left join marts.finance.dim_item_type as itt 
        on itt.item_type_value = r.item_type_value
    INNER JOIN marts.common.dim_center AS c
        ON c.center_id = r.center_id
    WHERE 
        (
            (
                r.payment_date >= TO_DATE('{wtd_start_date}') --wtd_start_date
                AND r.payment_date <= TO_DATE('{end_date}')--end_date
            )
            OR
            (
                r.payment_date >= DATEADD(YEAR, -1, TO_DATE('{wtd_start_date}')) --wtd_start_date
                AND r.payment_date <= DATEADD(YEAR, -1, TO_DATE('{end_date}')) --end_date
            )
        )
        AND c.is_reporting_branch = TRUE
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        AND r.is_retail = true  -- Dynamically set is_service filter (True/False)
        AND is_day_package = false  -- Dynamic condition for day_package_filter
    GROUP BY all
),
current_period AS (
    SELECT * FROM base WHERE period = 'CURRENT'
),
previous_period AS (
    SELECT * FROM base WHERE period = 'PREVIOUS'
),
summary_top_20 as (
    SELECT 
        COALESCE(c.category, p.category) AS category,
        COALESCE(c.sub_category, p.sub_category) AS sub_category,
        sum(round(c.revenue)) AS revenue_current,
        sum(round(p.revenue)) AS revenue_py,
        sum(round(c.units)) AS units_current,
        sum(round(p.units)) AS units_py
    FROM 
        current_period c
    LEFT OUTER JOIN 
        previous_period p
    ON 
        c.category = p.category 
        AND c.sub_category = p.sub_category
        AND c.center = p.center
    GROUP BY ALL
    ORDER BY 3 desc
    LIMIT 20
),
summary_total as (
    SELECT 
        sum(round(c.revenue)) AS revenue_current,
        sum(round(p.revenue)) AS revenue_py,
        sum(round(c.units)) AS units_current,
        sum(round(p.units)) AS units_py
    FROM 
        current_period c
    LEFT OUTER JOIN 
        previous_period p
    ON 
        c.category = p.category 
        AND c.sub_category = p.sub_category
        AND c.center = p.center
    GROUP BY ALL
),
summary_top_20_total as (
    select sum(revenue_current) AS revenue_current,
        sum(revenue_py) AS revenue_py,
        sum(units_current) AS units_current,
        sum(units_py) AS units_py
    from summary_top_20
),
combined_formatted as (
    SELECT 
        'Total Retail Items' as "Retail Items Comparison",
        a.revenue_current as "Group Revenue Current",
        a.revenue_py as "Group Revenue Previous",
        a.units_current as "Group Total Units Current",
        a.units_py as "Group Total Units Previous",
        ROUND((b.revenue_current/a.revenue_current)*100,2) || '%' as "Top 20 Current Revenue Over Total %",
        ROUND((b.revenue_py/a.revenue_py)*100,2) || '%' as "Top 20 Previous Revenue Over Total %",
        ROUND((b.units_current/a.units_current)*100,2) || '%' as "Top 20 Current Units Over Total %",
        ROUND((b.units_py/a.units_py)*100,2) || '%' as "Top 20 Previous Units Over Total %"
    FROM summary_total a
    CROSS JOIN summary_top_20_total b
)
select *
from combined_formatted
;

