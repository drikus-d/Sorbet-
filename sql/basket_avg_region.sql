with base as (
    select
        iff(
            r.payment_date >= to_date('{ytd_start_date}')
            and r.payment_date <= to_date('{end_date}'),
            'CURRENT',
            'PREVIOUS'
        ) as period,
        iff(
            (payment_date >= to_date('{wtd_start_date}') and payment_date <= to_date('{end_date}'))
            or (payment_date >= dateadd(year,-1,to_date('{wtd_start_date}')) and payment_date <= dateadd(year,-1,to_date('{end_date}'))), 
            1,
            0
        ) as wtd,
        iff(
            (payment_date >= to_date('{mtd_start_date}') and payment_date <= to_date('{end_date}'))
            or (payment_date >= dateadd(year,-1,to_date('{mtd_start_date}')) and payment_date <= dateadd(year,-1,to_date('{end_date}'))), 
            1,
            0
        ) as mtd,
        c.region,
        r.guest_code,
        r.is_birthday_discount,
        r.revenue,
        r.discount,
        r.invoice_no,
        r.is_loyalty_payment,
        r.is_service,
        r.is_retail
            from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c
                on c.center_id = r.center_id
        left join marts.finance.dim_tier as t
            on t.tier_id = r.tier_id
    where
        (
            (
                payment_date >= to_date('{ytd_start_date}') and payment_date <= to_date('{end_date}')
            )
            or
            (
                payment_date >= dateadd(year, -1, to_date('{ytd_start_date}'))
                and payment_date <= dateadd(year, -1, to_date('{end_date}'))
            )
        )
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and c.REPORTING_BRAND_NAME != 'No Zone' and c.is_reporting_branch = true 
        and c.REPORTING_BRAND_NAME is not null
),
grouped_by_region as (
    select
        period,
        wtd,
        mtd,
        region,
        sum(iff(is_loyalty_payment = false, revenue, 0)) as sales,
        count(distinct(iff(is_loyalty_payment = false, invoice_no, null))) as transaction,
        count(distinct(iff(is_loyalty_payment = false, guest_code, null))) as unique_guest_count,
        sum(iff(is_loyalty_payment = true, revenue, 0)) as redemption_value,
        sum(iff(is_birthday_discount = true, discount, 0)) as birthday_discount,
        sum(iff(is_loyalty_payment = false and is_service = true, revenue, 0)) as service_sales,
        count(distinct iff(is_loyalty_payment = false and is_service = true, invoice_no, null)) as service_transactions,
        sum(iff(is_loyalty_payment = false and is_retail = true, revenue, 0)) as retail_sales,
        count(distinct iff(is_loyalty_payment = false and is_retail = true, invoice_no, null)) as retail_transactions
    from base 
    group by all
),
pivoted_data as (
    select
        period,
        wtd,
        mtd,
        sum(iff(region = 'Inland - West', sales, 0)) as INLAND_WEST,
        sum(iff(region = 'Inland - Outlying', sales, 0)) as INLAND_OUTLYING,
        sum(iff(region = 'Inland - North', sales, 0)) as INLAND_NORTH,
        sum(iff(region = 'Inland - South', sales, 0)) as INLAND_SOUTH,
        sum(iff(region = 'Inland - East', sales, 0)) as INLAND_EAST,
        sum(iff(region = 'Western Cape', sales, 0)) as WESTERN_CAPE,
        sum(iff(region = 'KwaZulu-Natal', sales, 0)) as KWAZULU_NATAL,
        sum(iff(region = 'Inland - West', transaction, 0)) as INLAND_WEST_TRANS,
        sum(iff(region = 'Inland - Outlying', transaction, 0)) as INLAND_OUTLYING_TRANS,
        sum(iff(region = 'Inland - North', transaction, 0)) as INLAND_NORTH_TRANS,
        sum(iff(region = 'Inland - South', transaction, 0)) as INLAND_SOUTH_TRANS,
        sum(iff(region = 'Inland - East', transaction, 0)) as INLAND_EAST_TRANS,
        sum(iff(region = 'Western Cape', transaction, 0)) as WESTERN_CAPE_TRANS,
        sum(iff(region = 'KwaZulu-Natal', transaction, 0)) as KWAZULU_NATAL_TRANS,
        sum(iff(region = 'Inland - West', service_sales, 0)) as INLAND_WEST_SERVICE,
        sum(iff(region = 'Inland - Outlying', service_sales, 0)) as INLAND_OUTLYING_SERVICE,
        sum(iff(region = 'Inland - North', service_sales, 0)) as INLAND_NORTH_SERVICE,
        sum(iff(region = 'Inland - South', service_sales, 0)) as INLAND_SOUTH_SERVICE,
        sum(iff(region = 'Inland - East', service_sales, 0)) as INLAND_EAST_SERVICE,
        sum(iff(region = 'Western Cape', service_sales, 0)) as WESTERN_CAPE_SERVICE,
        sum(iff(region = 'KwaZulu-Natal', service_sales, 0)) as KWAZULU_NATAL_SERVICE,
        sum(iff(region = 'Inland - West', service_transactions, 0)) as INLAND_WEST_SERVICE_TRANS,
        sum(iff(region = 'Inland - Outlying', service_transactions, 0)) as INLAND_OUTLYING_SERVICE_TRANS,
        sum(iff(region = 'Inland - North', service_transactions, 0)) as INLAND_NORTH_SERVICE_TRANS,
        sum(iff(region = 'Inland - South', service_transactions, 0)) as INLAND_SOUTH_SERVICE_TRANS,
        sum(iff(region = 'Inland - East', service_transactions, 0)) as INLAND_EAST_SERVICE_TRANS,
        sum(iff(region = 'Western Cape', service_transactions, 0)) as WESTERN_CAPE_SERVICE_TRANS,
        sum(iff(region = 'KwaZulu-Natal', service_transactions, 0)) as KWAZULU_NATAL_SERVICE_TRANS,
        sum(iff(region = 'Inland - West', retail_sales, 0)) as INLAND_WEST_RETAIL,
        sum(iff(region = 'Inland - Outlying', retail_sales, 0)) as INLAND_OUTLYING_RETAIL,
        sum(iff(region = 'Inland - North', retail_sales, 0)) as INLAND_NORTH_RETAIL,
        sum(iff(region = 'Inland - South', retail_sales, 0)) as INLAND_SOUTH_RETAIL,
        sum(iff(region = 'Inland - East', retail_sales, 0)) as INLAND_EAST_RETAIL,
        sum(iff(region = 'Western Cape', retail_sales, 0)) as WESTERN_CAPE_RETAIL,
        sum(iff(region = 'KwaZulu-Natal', retail_sales, 0)) as KWAZULU_NATAL_RETAIL,
        sum(iff(region = 'Inland - West', retail_transactions, 0)) as INLAND_WEST_RETAIL_TRANS,
        sum(iff(region = 'Inland - Outlying', retail_transactions, 0)) as INLAND_OUTLYING_RETAIL_TRANS,
        sum(iff(region = 'Inland - North', retail_transactions, 0)) as INLAND_NORTH_RETAIL_TRANS,
        sum(iff(region = 'Inland - South', retail_transactions, 0)) as INLAND_SOUTH_RETAIL_TRANS,
        sum(iff(region = 'Inland - East', retail_transactions, 0)) as INLAND_EAST_RETAIL_TRANS,
        sum(iff(region = 'Western Cape', retail_transactions, 0)) as WESTERN_CAPE_RETAIL_TRANS,
        sum(iff(region = 'KwaZulu-Natal', retail_transactions, 0)) as KWAZULU_NATAL_RETAIL_TRANS
    from grouped_by_region
    group by period, wtd, mtd
),
current_data as (
    select * from pivoted_data where period = 'CURRENT'
),
previous_data as (
    select * from pivoted_data where period = 'PREVIOUS'
),
basket_calculations as (
    select 'Actual' as act_bud,
        round(sum(iff(c.wtd = 1, c.INLAND_WEST, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_WEST_TRANS, 0)), 0)) as INLAND_WEST,
        round(sum(iff(c.wtd = 1, c.INLAND_OUTLYING, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_OUTLYING_TRANS, 0)), 0)) as INLAND_OUTLYING,
        round(sum(iff(c.wtd = 1, c.INLAND_NORTH, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_NORTH_TRANS, 0)), 0)) as INLAND_NORTH,
        round(sum(iff(c.wtd = 1, c.INLAND_SOUTH, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_SOUTH_TRANS, 0)), 0)) as INLAND_SOUTH,
        round(sum(iff(c.wtd = 1, c.INLAND_EAST, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_EAST_TRANS, 0)), 0)) as INLAND_EAST,
        round(sum(iff(c.wtd = 1, c.WESTERN_CAPE, 0))/NULLIF(sum(iff(c.wtd = 1, c.WESTERN_CAPE_TRANS, 0)), 0)) as WESTERN_CAPE,
        round(sum(iff(c.wtd = 1, c.KWAZULU_NATAL, 0))/NULLIF(sum(iff(c.wtd = 1, c.KWAZULU_NATAL_TRANS, 0)), 0)) as KWAZULU_NATAL
    from current_data c

    union

    select 'Last Year' as act_bud,
        round(sum(iff(p.wtd = 1, p.INLAND_WEST, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_WEST_TRANS, 0)), 0)) as INLAND_WEST,
        round(sum(iff(p.wtd = 1, p.INLAND_OUTLYING, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_OUTLYING_TRANS, 0)), 0)) as INLAND_OUTLYING,
        round(sum(iff(p.wtd = 1, p.INLAND_NORTH, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_NORTH_TRANS, 0)), 0)) as INLAND_NORTH,
        round(sum(iff(p.wtd = 1, p.INLAND_SOUTH, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_SOUTH_TRANS, 0)), 0)) as INLAND_SOUTH,
        round(sum(iff(p.wtd = 1, p.INLAND_EAST, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_EAST_TRANS, 0)), 0)) as INLAND_EAST,
        round(sum(iff(p.wtd = 1, p.WESTERN_CAPE, 0))/NULLIF(sum(iff(p.wtd = 1, p.WESTERN_CAPE_TRANS, 0)), 0)) as WESTERN_CAPE,
        round(sum(iff(p.wtd = 1, p.KWAZULU_NATAL, 0))/NULLIF(sum(iff(p.wtd = 1, p.KWAZULU_NATAL_TRANS, 0)), 0)) as KWAZULU_NATAL
    from previous_data p

    union

    select 'Last Year %' as act_bud,
        round(((sum(iff(c.wtd = 1, c.INLAND_WEST, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_WEST_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_WEST, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_WEST_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_WEST,
        round(((sum(iff(c.wtd = 1, c.INLAND_OUTLYING, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_OUTLYING_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_OUTLYING, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_OUTLYING_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_OUTLYING,
        round(((sum(iff(c.wtd = 1, c.INLAND_NORTH, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_NORTH_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_NORTH, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_NORTH_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_NORTH,
        round(((sum(iff(c.wtd = 1, c.INLAND_SOUTH, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_SOUTH_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_SOUTH, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_SOUTH_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_SOUTH,
        round(((sum(iff(c.wtd = 1, c.INLAND_EAST, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_EAST_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_EAST, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_EAST_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_EAST,
        round(((sum(iff(c.wtd = 1, c.WESTERN_CAPE, 0))/NULLIF(sum(iff(c.wtd = 1, c.WESTERN_CAPE_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.WESTERN_CAPE, 0))/NULLIF(sum(iff(p.wtd = 1, p.WESTERN_CAPE_TRANS, 0)), 0), 0) - 1) * 100, 2) as WESTERN_CAPE,
        round(((sum(iff(c.wtd = 1, c.KWAZULU_NATAL, 0))/NULLIF(sum(iff(c.wtd = 1, c.KWAZULU_NATAL_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.KWAZULU_NATAL, 0))/NULLIF(sum(iff(p.wtd = 1, p.KWAZULU_NATAL_TRANS, 0)), 0), 0) - 1) * 100, 2) as KWAZULU_NATAL
    from current_data c
    cross join previous_data p

    union

    select 'Retail Actual' as act_bud,
        round(sum(iff(c.wtd = 1, c.INLAND_WEST_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_WEST_RETAIL_TRANS, 0)), 0)) as INLAND_WEST,
        round(sum(iff(c.wtd = 1, c.INLAND_OUTLYING_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_OUTLYING_RETAIL_TRANS, 0)), 0)) as INLAND_OUTLYING,
        round(sum(iff(c.wtd = 1, c.INLAND_NORTH_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_NORTH_RETAIL_TRANS, 0)), 0)) as INLAND_NORTH,
        round(sum(iff(c.wtd = 1, c.INLAND_SOUTH_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_SOUTH_RETAIL_TRANS, 0)), 0)) as INLAND_SOUTH,
        round(sum(iff(c.wtd = 1, c.INLAND_EAST_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_EAST_RETAIL_TRANS, 0)), 0)) as INLAND_EAST,
        round(sum(iff(c.wtd = 1, c.WESTERN_CAPE_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.WESTERN_CAPE_RETAIL_TRANS, 0)), 0)) as WESTERN_CAPE,
        round(sum(iff(c.wtd = 1, c.KWAZULU_NATAL_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.KWAZULU_NATAL_RETAIL_TRANS, 0)), 0)) as KWAZULU_NATAL
    from current_data c

    union

    select 'Retail Last Year' as act_bud,
        round(sum(iff(p.wtd = 1, p.INLAND_WEST_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_WEST_RETAIL_TRANS, 0)), 0)) as INLAND_WEST,
        round(sum(iff(p.wtd = 1, p.INLAND_OUTLYING_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_OUTLYING_RETAIL_TRANS, 0)), 0)) as INLAND_OUTLYING,
        round(sum(iff(p.wtd = 1, p.INLAND_NORTH_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_NORTH_RETAIL_TRANS, 0)), 0)) as INLAND_NORTH,
        round(sum(iff(p.wtd = 1, p.INLAND_SOUTH_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_SOUTH_RETAIL_TRANS, 0)), 0)) as INLAND_SOUTH,
        round(sum(iff(p.wtd = 1, p.INLAND_EAST_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_EAST_RETAIL_TRANS, 0)), 0)) as INLAND_EAST,
        round(sum(iff(p.wtd = 1, p.WESTERN_CAPE_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.WESTERN_CAPE_RETAIL_TRANS, 0)), 0)) as WESTERN_CAPE,
        round(sum(iff(p.wtd = 1, p.KWAZULU_NATAL_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.KWAZULU_NATAL_RETAIL_TRANS, 0)), 0)) as KWAZULU_NATAL
    from previous_data p

    union

    select 'Retail Last Year %' as act_bud,
        round(((sum(iff(c.wtd = 1, c.INLAND_WEST_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_WEST_RETAIL_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_WEST_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_WEST_RETAIL_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_WEST,
        round(((sum(iff(c.wtd = 1, c.INLAND_OUTLYING_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_OUTLYING_RETAIL_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_OUTLYING_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_OUTLYING_RETAIL_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_OUTLYING,
        round(((sum(iff(c.wtd = 1, c.INLAND_NORTH_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_NORTH_RETAIL_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_NORTH_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_NORTH_RETAIL_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_NORTH,
        round(((sum(iff(c.wtd = 1, c.INLAND_SOUTH_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_SOUTH_RETAIL_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_SOUTH_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_SOUTH_RETAIL_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_SOUTH,
        round(((sum(iff(c.wtd = 1, c.INLAND_EAST_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_EAST_RETAIL_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_EAST_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_EAST_RETAIL_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_EAST,
        round(((sum(iff(c.wtd = 1, c.WESTERN_CAPE_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.WESTERN_CAPE_RETAIL_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.WESTERN_CAPE_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.WESTERN_CAPE_RETAIL_TRANS, 0)), 0), 0) - 1) * 100, 2) as WESTERN_CAPE,
        round(((sum(iff(c.wtd = 1, c.KWAZULU_NATAL_RETAIL, 0))/NULLIF(sum(iff(c.wtd = 1, c.KWAZULU_NATAL_RETAIL_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.KWAZULU_NATAL_RETAIL, 0))/NULLIF(sum(iff(p.wtd = 1, p.KWAZULU_NATAL_RETAIL_TRANS, 0)), 0), 0) - 1) * 100, 2) as KWAZULU_NATAL
    from current_data c
    cross join previous_data p
    
    union
    
    select 'Service Actual' as act_bud,
        round(sum(iff(c.wtd = 1, c.INLAND_WEST_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_WEST_SERVICE_TRANS, 0)), 0)) as INLAND_WEST,
        round(sum(iff(c.wtd = 1, c.INLAND_OUTLYING_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_OUTLYING_SERVICE_TRANS, 0)), 0)) as INLAND_OUTLYING,
        round(sum(iff(c.wtd = 1, c.INLAND_NORTH_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_NORTH_SERVICE_TRANS, 0)), 0)) as INLAND_NORTH,
        round(sum(iff(c.wtd = 1, c.INLAND_SOUTH_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_SOUTH_SERVICE_TRANS, 0)), 0)) as INLAND_SOUTH,
        round(sum(iff(c.wtd = 1, c.INLAND_EAST_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_EAST_SERVICE_TRANS, 0)), 0)) as INLAND_EAST,
        round(sum(iff(c.wtd = 1, c.WESTERN_CAPE_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.WESTERN_CAPE_SERVICE_TRANS, 0)), 0)) as WESTERN_CAPE,
        round(sum(iff(c.wtd = 1, c.KWAZULU_NATAL_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.KWAZULU_NATAL_SERVICE_TRANS, 0)), 0)) as KWAZULU_NATAL
    from current_data c
    
    union
    
    select 'Service Last Year' as act_bud,
        round(sum(iff(p.wtd = 1, p.INLAND_WEST_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_WEST_SERVICE_TRANS, 0)), 0)) as INLAND_WEST,
        round(sum(iff(p.wtd = 1, p.INLAND_OUTLYING_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_OUTLYING_SERVICE_TRANS, 0)), 0)) as INLAND_OUTLYING,
        round(sum(iff(p.wtd = 1, p.INLAND_NORTH_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_NORTH_SERVICE_TRANS, 0)), 0)) as INLAND_NORTH,
        round(sum(iff(p.wtd = 1, p.INLAND_SOUTH_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_SOUTH_SERVICE_TRANS, 0)), 0)) as INLAND_SOUTH,
        round(sum(iff(p.wtd = 1, p.INLAND_EAST_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_EAST_SERVICE_TRANS, 0)), 0)) as INLAND_EAST,
        round(sum(iff(p.wtd = 1, p.WESTERN_CAPE_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.WESTERN_CAPE_SERVICE_TRANS, 0)), 0)) as WESTERN_CAPE,
        round(sum(iff(p.wtd = 1, p.KWAZULU_NATAL_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.KWAZULU_NATAL_SERVICE_TRANS, 0)), 0)) as KWAZULU_NATAL
    from previous_data p

    union

    select 'Service Last Year %' as act_bud,
        round(((sum(iff(c.wtd = 1, c.INLAND_WEST_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_WEST_SERVICE_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_WEST_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_WEST_SERVICE_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_WEST,
        round(((sum(iff(c.wtd = 1, c.INLAND_OUTLYING_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_OUTLYING_SERVICE_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_OUTLYING_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_OUTLYING_SERVICE_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_OUTLYING,
        round(((sum(iff(c.wtd = 1, c.INLAND_NORTH_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_NORTH_SERVICE_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_NORTH_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_NORTH_SERVICE_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_NORTH,
        round(((sum(iff(c.wtd = 1, c.INLAND_SOUTH_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_SOUTH_SERVICE_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_SOUTH_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_SOUTH_SERVICE_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_SOUTH,
        round(((sum(iff(c.wtd = 1, c.INLAND_EAST_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.INLAND_EAST_SERVICE_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.INLAND_EAST_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.INLAND_EAST_SERVICE_TRANS, 0)), 0), 0) - 1) * 100, 2) as INLAND_EAST,
        round(((sum(iff(c.wtd = 1, c.WESTERN_CAPE_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.WESTERN_CAPE_SERVICE_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.WESTERN_CAPE_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.WESTERN_CAPE_SERVICE_TRANS, 0)), 0), 0) - 1) * 100, 2) as WESTERN_CAPE,
        round(((sum(iff(c.wtd = 1, c.KWAZULU_NATAL_SERVICE, 0))/NULLIF(sum(iff(c.wtd = 1, c.KWAZULU_NATAL_SERVICE_TRANS, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.KWAZULU_NATAL_SERVICE, 0))/NULLIF(sum(iff(p.wtd = 1, p.KWAZULU_NATAL_SERVICE_TRANS, 0)), 0), 0) - 1) * 100, 2) as KWAZULU_NATAL
    from current_data c
    cross join previous_data p
)

select * from basket_calculations
order by 
    case act_bud
    when 'Actual' then 1
    when 'Last Year' then 2
    when 'Last Year %' then 3
    when 'Retail Actual' then 4
    when 'Retail Last Year' then 5
    when 'Retail Last Year %' then 6
    when 'Service Actual' then 7
    when 'Service Last Year' then 8
    when 'Service Last Year %' then 9
    else 10
end