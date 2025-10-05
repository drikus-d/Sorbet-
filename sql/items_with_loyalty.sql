WITH base AS (
    SELECT
        IFF(
            r.payment_date >= TO_DATE('{start_date}')
            AND r.payment_date <= TO_DATE('{end_date}'),
            'CURRENT',
            'PREVIOUS'
        ) AS period,
        c.reporting_center_name AS center,
        trim(i.{item_group}) AS category,   -- Dynamically set either item_category (retail) or item_sub_category (service)
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
                r.payment_date >= TO_DATE('{start_date}') 
                AND r.payment_date <= TO_DATE('{end_date}')
            )
            OR
            (
                r.payment_date >= DATEADD(YEAR, -1, TO_DATE('{start_date}')) 
                AND r.payment_date <= DATEADD(YEAR, -1, TO_DATE('{end_date}'))
            )
        )
        AND c.is_reporting_branch = TRUE
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        AND {is_service_filter}  -- Dynamically set is_service filter (True/False)
        AND {day_package_condition}  -- Dynamic condition for day_package_filter
    GROUP BY all
),
current_period AS (
    SELECT * FROM base WHERE period = 'CURRENT'
),
previous_period AS (
    SELECT * FROM base WHERE period = 'PREVIOUS'
)
SELECT 
    COALESCE(c.category, p.category) AS category,
    c.center AS current_center,
    p.center AS previous_center,
    c.revenue AS current_total_revenue,
    p.revenue AS previous_total_revenue,
    c.units AS current_total_units,
    p.units AS previous_total_units
FROM 
    current_period c
FULL OUTER JOIN 
    previous_period p
ON 
    c.category = p.category 
    AND c.center = p.center;
