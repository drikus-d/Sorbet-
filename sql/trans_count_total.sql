with revenue as (
    select
        iff(
            payment_date >= to_date('{ytd_start_date}') --ytd_start_date
            and payment_date <= to_date('{end_date}'), --end_date
            'CURRENT',
            'PREVIOUS'
        ) as period,
        iff(
            (payment_date >= to_date('{wtd_start_date}') --wtd_start_date            
            and payment_date <= to_date('{end_date}'))--end_date
            or (payment_date >= dateadd(year,-1,to_date('{wtd_start_date}')) --wtd_start_date            
            and payment_date <= dateadd(year,-1,to_date('{end_date}')))--end_date
            , 
            1,
            0
        ) as wtd,
        iff(
            (payment_date >= to_date('{mtd_start_date}') --mtd_start_date            
            and payment_date <= to_date('{end_date}'))--end_date
            or (payment_date >= dateadd(year,-1,to_date('{mtd_start_date}')) --mtd_start_date            
            and payment_date <= to_date('{end_date}'))--end_date
            , 
            1,
            0
        ) as mtd,
        count(distinct r.invoice_no) as transaction_count
    from
        marts.finance.fact_revenue r
    inner join marts.common.dim_center as c
        on c.center_id = r.center_id
            and c.is_reporting_branch = true
    where
        REPORTING_BRAND_NAME != 'No Zone' and is_reporting_branch = true 
        and REPORTING_BRAND_NAME is not null
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and is_loyalty_payment = false and 
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
    group by period, wtd, mtd
),
service_revenue as (
    select
        iff(
            payment_date >= to_date('{ytd_start_date}') --ytd_start_date
            and payment_date <= to_date('{end_date}'), --end_date
            'CURRENT',
            'PREVIOUS'
        ) as period,
        iff(
            (payment_date >= to_date('{wtd_start_date}') --wtd_start_date            
            and payment_date <= to_date('{end_date}'))--end_date
            or (payment_date >= dateadd(year,-1,to_date('{wtd_start_date}')) --wtd_start_date            
            and payment_date <= dateadd(year,-1,to_date('{end_date}')))--end_date
            , 
            1,
            0
        ) as wtd,
        iff(
            (payment_date >= to_date('{mtd_start_date}') --mtd_start_date            
            and payment_date <= to_date('{end_date}'))--end_date
            or (payment_date >= dateadd(year,-1,to_date('{mtd_start_date}')) --mtd_start_date            
            and payment_date <= to_date('{end_date}'))--end_date
            , 
            1,
            0
        ) as mtd,
        count(distinct r.invoice_no) as transaction_count
    from
        marts.finance.fact_revenue r
    inner join marts.common.dim_center as c
        on c.center_id = r.center_id
            and c.is_reporting_branch = true
    where
        REPORTING_BRAND_NAME != 'No Zone' and is_reporting_branch = true 
        and REPORTING_BRAND_NAME is not null
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and is_loyalty_payment = false 
        and r.is_service = true
        and (
            (
                payment_date >= to_date('{ytd_start_date}') and payment_date <= to_date('{end_date}')
            )
            or
            (
                payment_date >= dateadd(year, -1, to_date('{ytd_start_date}'))
                and payment_date <= dateadd(year, -1, to_date('{end_date}'))
            )
        )
    group by period, wtd, mtd
),
retail_revenue as (
    select
        iff(
            payment_date >= to_date('{ytd_start_date}') --ytd_start_date
            and payment_date <= to_date('{end_date}'), --end_date
            'CURRENT',
            'PREVIOUS'
        ) as period,
        iff(
            (payment_date >= to_date('{wtd_start_date}') --wtd_start_date            
            and payment_date <= to_date('{end_date}'))--end_date
            or (payment_date >= dateadd(year,-1,to_date('{wtd_start_date}')) --wtd_start_date            
            and payment_date <= dateadd(year,-1,to_date('{end_date}')))--end_date
            , 
            1,
            0
        ) as wtd,
        iff(
            (payment_date >= to_date('{mtd_start_date}') --mtd_start_date            
            and payment_date <= to_date('{end_date}'))--end_date
            or (payment_date >= dateadd(year,-1,to_date('{mtd_start_date}')) --mtd_start_date            
            and payment_date <= to_date('{end_date}'))--end_date
            , 
            1,
            0
        ) as mtd,
        count(distinct r.invoice_no) as transaction_count
    from
        marts.finance.fact_revenue r
    inner join marts.common.dim_center as c
        on c.center_id = r.center_id
            and c.is_reporting_branch = true
    where
        REPORTING_BRAND_NAME != 'No Zone' and is_reporting_branch = true 
        and REPORTING_BRAND_NAME is not null
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and is_loyalty_payment = false 
        and r.is_retail = true
        and (
            (
                payment_date >= to_date('{ytd_start_date}') and payment_date <= to_date('{end_date}')
            )
            or
            (
                payment_date >= dateadd(year, -1, to_date('{ytd_start_date}'))
                and payment_date <= dateadd(year, -1, to_date('{end_date}'))
            )
        )
    group by period, wtd, mtd
),
base as (
    select
        'Actual' as act_bud,
        1 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1, transaction_count, 0)))) as wtd,
        TO_VARCHAR(round(sum(iff(mtd = 1, transaction_count, 0)))) as mtd,
        TO_VARCHAR(round(sum(r.transaction_count))) as ytd
    from revenue as r
    where period = 'CURRENT'
    group by all

    union

    select
        'Last Year' as act_bud,
        3 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1, transaction_count, 0)))) as wtd,
        TO_VARCHAR(round(sum(iff(mtd = 1, transaction_count, 0)))) as mtd,
        TO_VARCHAR(round(sum(r.transaction_count))) as ytd
    from revenue as r
    where period = 'PREVIOUS'
    group by all

    union

    select
        'Service Actual' as act_bud,
        5 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1, transaction_count, 0)))) as wtd,
        TO_VARCHAR(round(sum(iff(mtd = 1, transaction_count, 0)))) as mtd,
        TO_VARCHAR(round(sum(r.transaction_count))) as ytd
    from service_revenue as r
    where period = 'CURRENT'
    group by all

    union

    select
        'Service Last Year' as act_bud,
        7 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1, transaction_count, 0)))) as wtd,
        TO_VARCHAR(round(sum(iff(mtd = 1, transaction_count, 0)))) as mtd,
        TO_VARCHAR(round(sum(r.transaction_count))) as ytd
    from service_revenue as r
    where period = 'PREVIOUS'
    group by all

    union

    select
        'Retail Actual' as act_bud,
        9 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1, transaction_count, 0)))) as wtd,
        TO_VARCHAR(round(sum(iff(mtd = 1, transaction_count, 0)))) as mtd,
        TO_VARCHAR(round(sum(r.transaction_count))) as ytd
    from retail_revenue as r
    where period = 'CURRENT'
    group by all

    union

    select
        'Retail Last Year' as act_bud,
        11 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1, transaction_count, 0)))) as wtd,
        TO_VARCHAR(round(sum(iff(mtd = 1, transaction_count, 0)))) as mtd,
        TO_VARCHAR(round(sum(r.transaction_count))) as ytd
    from retail_revenue as r
    where period = 'PREVIOUS'
    group by all
),
summary as (
    select *
    from base
    
    union
    
    select 'Last Year %' as act_bud,
            4 as act_bud_order,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', wtd, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', wtd, 0)), 0))-1)*100,2)) || '%' as wtd,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', mtd, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', mtd, 0)), 0))-1)*100,2)) || '%' as mtd,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', ytd, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', ytd, 0)), 0))-1)*100,2)) || '%' as ytd
    from base
    where act_bud in ('Actual', 'Last Year')
    group by all
    
    union
    
    select 'Service Last Year %' as act_bud,
            8 as act_bud_order,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Service Actual', wtd, 0)) / NULLIF(sum(iff(act_bud = 'Service Last Year', wtd, 0)), 0))-1)*100,2)) || '%' as wtd,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Service Actual', mtd, 0)) / NULLIF(sum(iff(act_bud = 'Service Last Year', mtd, 0)), 0))-1)*100,2)) || '%' as mtd,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Service Actual', ytd, 0)) / NULLIF(sum(iff(act_bud = 'Service Last Year', ytd, 0)), 0))-1)*100,2)) || '%' as ytd
    from base
    where act_bud in ('Service Actual', 'Service Last Year')
    group by all
    
    union
    
    select 'Retail Last Year %' as act_bud,
            12 as act_bud_order,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Retail Actual', wtd, 0)) / NULLIF(sum(iff(act_bud = 'Retail Last Year', wtd, 0)), 0))-1)*100,2)) || '%' as wtd,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Retail Actual', mtd, 0)) / NULLIF(sum(iff(act_bud = 'Retail Last Year', mtd, 0)), 0))-1)*100,2)) || '%' as mtd,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Retail Actual', ytd, 0)) / NULLIF(sum(iff(act_bud = 'Retail Last Year', ytd, 0)), 0))-1)*100,2)) || '%' as ytd
    from base
    where act_bud in ('Retail Actual', 'Retail Last Year')
    group by all
    
    union
    
    select '' as act_bud,
            0 as act_bud_order,
            '' as wtd,
            '' as mtd,
            '' as ytd 
)

select act_bud as "Region",
            wtd as "Last Week",
            mtd as "MTD",
            ytd as "YTD"
from summary
order by act_bud_order