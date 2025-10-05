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
        trim(i.item_category) AS category,
        trim(i.item_sub_category) as sub_category,
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
        AND r.is_service = true  -- Dynamically set is_service filter (True/False)
        AND is_day_package = false  -- Dynamic condition for day_package_filter
    GROUP BY all
),
current_period AS (
    SELECT * FROM base WHERE period = 'CURRENT'
),
previous_period AS (
    SELECT * FROM base WHERE period = 'PREVIOUS'
),
summary as (
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
sub_category_ordered as (
    select *,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue_current desc) sub_cat_order
    from summary
),
total_summary as (
    select  
        category,
        null as sub_category,
        sum(revenue_current) AS revenue_current,
        sum(revenue_py) AS revenue_py,
        sum(units_current) AS units_current,
        sum(units_py) AS units_py,
        9999 as sub_cat_order
    from summary
    group by category
),
total_summary_ordered as (
    select *,
        ROW_NUMBER() OVER (ORDER BY revenue_current desc) cat_order
    from total_summary
),
combined as (
    select s.*,c.cat_order from sub_category_ordered s
    left join total_summary_ordered c
        on s.category = c.category
    union
    select * from total_summary_ordered
),
combined_formatted as (
    SELECT 
        category,
        ifnull(sub_category,'Total ' || category || ' Offering') as sub_category,
        sum(revenue_current) AS revenue_current,
        sum(revenue_py) AS revenue_py,
        sum(units_current) AS units_current,
        sum(units_py) AS units_py,
        TO_VARCHAR(case when sum(revenue_py) = 0 then null else ROUND(((sum(revenue_current)/sum(revenue_py))-1)*100,1) end) || '%' as rand_growth,
        TO_VARCHAR(case when sum(units_py) = 0 then null else ROUND(((sum(units_current)/sum(units_py))-1)*100,1) end) || '%' as unit_growth,
        cat_order,
        sub_cat_order
    FROM combined
    GROUP BY ALL
)
select 
    sub_category AS "Service Top 20 Items",
    revenue_current AS "Revenue Current",
    revenue_py AS "Revenue PY",
    units_current AS "Units Current",
    units_py AS "Units PY",
    rand_growth as "% RAND GROWTH",
    unit_growth as "% UNIT GROWTH"
from combined_formatted
ORDER BY cat_order, sub_cat_order
;
