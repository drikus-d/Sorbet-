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
grouped_all as (
    select
        period,
        wtd,
        mtd,
        'Total' as tier_name,
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
base_union_tables as (
    select * from grouped_all
),
current_data as (
    select * from base_union_tables where period = 'CURRENT'
),
previous_data as (
    select * from base_union_tables where period = 'PREVIOUS'
),
basket_calculations as (
    select
        'Actual' as act_bud,
        1 as act_bud_order,
        round(sum(iff(c.wtd = 1, c.sales, 0))/NULLIF(sum(iff(c.wtd = 1, c.transaction, 0)), 0)) as wtd,
        round(sum(iff(c.mtd = 1, c.sales, 0))/NULLIF(sum(iff(c.mtd = 1, c.transaction, 0)), 0)) as mtd,
        round(sum(c.sales)/NULLIF(sum(c.transaction), 0)) as ytd
    from current_data c
    
    union
    
    select
        'Last Year' as act_bud,
        2 as act_bud_order,
        round(sum(iff(p.wtd = 1, p.sales, 0))/NULLIF(sum(iff(p.wtd = 1, p.transaction, 0)), 0)) as wtd,
        round(sum(iff(p.mtd = 1, p.sales, 0))/NULLIF(sum(iff(p.mtd = 1, p.transaction, 0)), 0)) as mtd,
        round(sum(p.sales)/NULLIF(sum(p.transaction), 0)) as ytd
    from previous_data p
    
    union
    
    select
        'Retail Actual' as act_bud,
        4 as act_bud_order,
        round(sum(iff(c.wtd = 1, c.retail_sales, 0))/NULLIF(sum(iff(c.wtd = 1, c.retail_transactions, 0)), 0)) as wtd,
        round(sum(iff(c.mtd = 1, c.retail_sales, 0))/NULLIF(sum(iff(c.mtd = 1, c.retail_transactions, 0)), 0)) as mtd,
        round(sum(c.retail_sales)/NULLIF(sum(c.retail_transactions), 0)) as ytd
    from current_data c
    
    union
    
    select
        'Retail Last Year' as act_bud,
        5 as act_bud_order,
        round(sum(iff(p.wtd = 1, p.retail_sales, 0))/NULLIF(sum(iff(p.wtd = 1, p.retail_transactions, 0)), 0)) as wtd,
        round(sum(iff(p.mtd = 1, p.retail_sales, 0))/NULLIF(sum(iff(p.mtd = 1, p.retail_transactions, 0)), 0)) as mtd,
        round(sum(p.retail_sales)/NULLIF(sum(p.retail_transactions), 0)) as ytd
    from previous_data p
    
    union
    
    select
        'Service Actual' as act_bud,
        7 as act_bud_order,
        round(sum(iff(c.wtd = 1, c.service_sales, 0))/NULLIF(sum(iff(c.wtd = 1, c.service_transactions, 0)), 0)) as wtd,
        round(sum(iff(c.mtd = 1, c.service_sales, 0))/NULLIF(sum(iff(c.mtd = 1, c.service_transactions, 0)), 0)) as mtd,
        round(sum(c.service_sales)/NULLIF(sum(c.service_transactions), 0)) as ytd
    from current_data c
    
    union
    
    select
        'Service Last Year' as act_bud,
        8 as act_bud_order,
        round(sum(iff(p.wtd = 1, p.service_sales, 0))/NULLIF(sum(iff(p.wtd = 1, p.service_transactions, 0)), 0)) as wtd,
        round(sum(iff(p.mtd = 1, p.service_sales, 0))/NULLIF(sum(iff(p.mtd = 1, p.service_transactions, 0)), 0)) as mtd,
        round(sum(p.service_sales)/NULLIF(sum(p.service_transactions), 0)) as ytd
    from previous_data p
    
    union
    
    select
        'Last Year %' as act_bud,
        3 as act_bud_order,
        round(((sum(iff(c.wtd = 1, c.sales, 0))/NULLIF(sum(iff(c.wtd = 1, c.transaction, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.sales, 0))/NULLIF(sum(iff(p.wtd = 1, p.transaction, 0)), 0), 0) - 1) * 100, 2) as wtd,
        round(((sum(iff(c.mtd = 1, c.sales, 0))/NULLIF(sum(iff(c.mtd = 1, c.transaction, 0)), 0)) / NULLIF(sum(iff(p.mtd = 1, p.sales, 0))/NULLIF(sum(iff(p.mtd = 1, p.transaction, 0)), 0), 0) - 1) * 100, 2) as mtd,
        round(((sum(c.sales)/NULLIF(sum(c.transaction), 0)) / NULLIF(sum(p.sales)/NULLIF(sum(p.transaction), 0), 0) - 1) * 100, 2) as ytd
    from current_data c
    cross join previous_data p
    
    union
    
    select
        'Retail Last Year %' as act_bud,
        6 as act_bud_order,
        round(((sum(iff(c.wtd = 1, c.retail_sales, 0))/NULLIF(sum(iff(c.wtd = 1, c.retail_transactions, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.retail_sales, 0))/NULLIF(sum(iff(p.wtd = 1, p.retail_transactions, 0)), 0), 0) - 1) * 100, 2) as wtd,
        round(((sum(iff(c.mtd = 1, c.retail_sales, 0))/NULLIF(sum(iff(c.mtd = 1, c.retail_transactions, 0)), 0)) / NULLIF(sum(iff(p.mtd = 1, p.retail_sales, 0))/NULLIF(sum(iff(p.mtd = 1, p.retail_transactions, 0)), 0), 0) - 1) * 100, 2) as mtd,
        round(((sum(c.retail_sales)/NULLIF(sum(c.retail_transactions), 0)) / NULLIF(sum(p.retail_sales)/NULLIF(sum(p.retail_transactions), 0), 0) - 1) * 100, 2) as ytd
    from current_data c
    cross join previous_data p
    
    union
    
    select
        'Service Last Year %' as act_bud,
        9 as act_bud_order,
        round(((sum(iff(c.wtd = 1, c.service_sales, 0))/NULLIF(sum(iff(c.wtd = 1, c.service_transactions, 0)), 0)) / NULLIF(sum(iff(p.wtd = 1, p.service_sales, 0))/NULLIF(sum(iff(p.wtd = 1, p.service_transactions, 0)), 0), 0) - 1) * 100, 2) as wtd,
        round(((sum(iff(c.mtd = 1, c.service_sales, 0))/NULLIF(sum(iff(c.mtd = 1, c.service_transactions, 0)), 0)) / NULLIF(sum(iff(p.mtd = 1, p.service_sales, 0))/NULLIF(sum(iff(p.mtd = 1, p.service_transactions, 0)), 0), 0) - 1) * 100, 2) as mtd,
        round(((sum(c.service_sales)/NULLIF(sum(c.service_transactions), 0)) / NULLIF(sum(p.service_sales)/NULLIF(sum(p.service_transactions), 0), 0) - 1) * 100, 2) as ytd
    from current_data c
    cross join previous_data p
)

select act_bud, wtd, mtd, ytd from basket_calculations
order by act_bud_order