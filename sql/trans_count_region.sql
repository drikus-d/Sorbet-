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
        c.region,
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
    group by period, wtd, mtd, c.region
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
        c.region,
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
    group by period, wtd, mtd, c.region
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
        c.region,
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
    group by period, wtd, mtd, c.region
),
base as (
    select
        'Actual' as act_bud,
        1 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - West', transaction_count, 0)))) as INLAND_WEST,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - Outlying', transaction_count, 0)))) as INLAND_OUTLYING,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - North', transaction_count, 0)))) as INLAND_NORTH,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - South', transaction_count, 0)))) as INLAND_SOUTH,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - East', transaction_count, 0)))) as INLAND_EAST,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Western Cape', transaction_count, 0)))) as WESTERN_CAPE,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'KwaZulu-Natal', transaction_count, 0)))) as KWAZULU_NATAL
    from revenue as r
    where period = 'CURRENT'
    group by all

    union

    select
        'Last Year' as act_bud,
        3 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - West', transaction_count, 0)))) as INLAND_WEST,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - Outlying', transaction_count, 0)))) as INLAND_OUTLYING,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - North', transaction_count, 0)))) as INLAND_NORTH,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - South', transaction_count, 0)))) as INLAND_SOUTH,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - East', transaction_count, 0)))) as INLAND_EAST,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Western Cape', transaction_count, 0)))) as WESTERN_CAPE,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'KwaZulu-Natal', transaction_count, 0)))) as KWAZULU_NATAL
    from revenue as r
    where period = 'PREVIOUS'
    group by all

    union

    select
        'Service Actual' as act_bud,
        5 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - West', transaction_count, 0)))) as INLAND_WEST,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - Outlying', transaction_count, 0)))) as INLAND_OUTLYING,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - North', transaction_count, 0)))) as INLAND_NORTH,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - South', transaction_count, 0)))) as INLAND_SOUTH,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - East', transaction_count, 0)))) as INLAND_EAST,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Western Cape', transaction_count, 0)))) as WESTERN_CAPE,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'KwaZulu-Natal', transaction_count, 0)))) as KWAZULU_NATAL
    from service_revenue as r
    where period = 'CURRENT'
    group by all

    union

    select
        'Service Last Year' as act_bud,
        7 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - West', transaction_count, 0)))) as INLAND_WEST,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - Outlying', transaction_count, 0)))) as INLAND_OUTLYING,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - North', transaction_count, 0)))) as INLAND_NORTH,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - South', transaction_count, 0)))) as INLAND_SOUTH,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - East', transaction_count, 0)))) as INLAND_EAST,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Western Cape', transaction_count, 0)))) as WESTERN_CAPE,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'KwaZulu-Natal', transaction_count, 0)))) as KWAZULU_NATAL
    from service_revenue as r
    where period = 'PREVIOUS'
    group by all

    union

    select
        'Retail Actual' as act_bud,
        9 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - West', transaction_count, 0)))) as INLAND_WEST,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - Outlying', transaction_count, 0)))) as INLAND_OUTLYING,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - North', transaction_count, 0)))) as INLAND_NORTH,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - South', transaction_count, 0)))) as INLAND_SOUTH,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - East', transaction_count, 0)))) as INLAND_EAST,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Western Cape', transaction_count, 0)))) as WESTERN_CAPE,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'KwaZulu-Natal', transaction_count, 0)))) as KWAZULU_NATAL
    from retail_revenue as r
    where period = 'CURRENT'
    group by all

    union

    select
        'Retail Last Year' as act_bud,
        11 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - West', transaction_count, 0)))) as INLAND_WEST,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - Outlying', transaction_count, 0)))) as INLAND_OUTLYING,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - North', transaction_count, 0)))) as INLAND_NORTH,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - South', transaction_count, 0)))) as INLAND_SOUTH,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Inland - East', transaction_count, 0)))) as INLAND_EAST,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'Western Cape', transaction_count, 0)))) as WESTERN_CAPE,
        TO_VARCHAR(round(sum(iff(wtd = 1 and region = 'KwaZulu-Natal', transaction_count, 0)))) as KWAZULU_NATAL
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
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_WEST, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', INLAND_WEST, 0)), 0))-1)*100,2)) || '%' as INLAND_WEST,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_OUTLYING, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', INLAND_OUTLYING, 0)), 0))-1)*100,2)) || '%' as INLAND_OUTLYING,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_NORTH, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', INLAND_NORTH, 0)), 0))-1)*100,2)) || '%' as INLAND_NORTH,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_SOUTH, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', INLAND_SOUTH, 0)), 0))-1)*100,2)) || '%' as INLAND_SOUTH,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_EAST, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', INLAND_EAST, 0)), 0))-1)*100,2)) || '%' as INLAND_EAST,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', WESTERN_CAPE, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', WESTERN_CAPE, 0)), 0))-1)*100,2)) || '%' as WESTERN_CAPE,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', KWAZULU_NATAL, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', KWAZULU_NATAL, 0)), 0))-1)*100,2)) || '%' as KWAZULU_NATAL
    from base
    where act_bud in ('Actual', 'Last Year')
    group by all
    
    union
    
    select 'Service Last Year %' as act_bud,
            8 as act_bud_order,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Service Actual', INLAND_WEST, 0)) / NULLIF(sum(iff(act_bud = 'Service Last Year', INLAND_WEST, 0)), 0))-1)*100,2)) || '%' as INLAND_WEST,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Service Actual', INLAND_OUTLYING, 0)) / NULLIF(sum(iff(act_bud = 'Service Last Year', INLAND_OUTLYING, 0)), 0))-1)*100,2)) || '%' as INLAND_OUTLYING,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Service Actual', INLAND_NORTH, 0)) / NULLIF(sum(iff(act_bud = 'Service Last Year', INLAND_NORTH, 0)), 0))-1)*100,2)) || '%' as INLAND_NORTH,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Service Actual', INLAND_SOUTH, 0)) / NULLIF(sum(iff(act_bud = 'Service Last Year', INLAND_SOUTH, 0)), 0))-1)*100,2)) || '%' as INLAND_SOUTH,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Service Actual', INLAND_EAST, 0)) / NULLIF(sum(iff(act_bud = 'Service Last Year', INLAND_EAST, 0)), 0))-1)*100,2)) || '%' as INLAND_EAST,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Service Actual', WESTERN_CAPE, 0)) / NULLIF(sum(iff(act_bud = 'Service Last Year', WESTERN_CAPE, 0)), 0))-1)*100,2)) || '%' as WESTERN_CAPE,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Service Actual', KWAZULU_NATAL, 0)) / NULLIF(sum(iff(act_bud = 'Service Last Year', KWAZULU_NATAL, 0)), 0))-1)*100,2)) || '%' as KWAZULU_NATAL
    from base
    where act_bud in ('Service Actual', 'Service Last Year')
    group by all
    
    union
    
    select 'Retail Last Year %' as act_bud,
            12 as act_bud_order,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Retail Actual', INLAND_WEST, 0)) / NULLIF(sum(iff(act_bud = 'Retail Last Year', INLAND_WEST, 0)), 0))-1)*100,2)) || '%' as INLAND_WEST,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Retail Actual', INLAND_OUTLYING, 0)) / NULLIF(sum(iff(act_bud = 'Retail Last Year', INLAND_OUTLYING, 0)), 0))-1)*100,2)) || '%' as INLAND_OUTLYING,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Retail Actual', INLAND_NORTH, 0)) / NULLIF(sum(iff(act_bud = 'Retail Last Year', INLAND_NORTH, 0)), 0))-1)*100,2)) || '%' as INLAND_NORTH,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Retail Actual', INLAND_SOUTH, 0)) / NULLIF(sum(iff(act_bud = 'Retail Last Year', INLAND_SOUTH, 0)), 0))-1)*100,2)) || '%' as INLAND_SOUTH,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Retail Actual', INLAND_EAST, 0)) / NULLIF(sum(iff(act_bud = 'Retail Last Year', INLAND_EAST, 0)), 0))-1)*100,2)) || '%' as INLAND_EAST,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Retail Actual', WESTERN_CAPE, 0)) / NULLIF(sum(iff(act_bud = 'Retail Last Year', WESTERN_CAPE, 0)), 0))-1)*100,2)) || '%' as WESTERN_CAPE,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Retail Actual', KWAZULU_NATAL, 0)) / NULLIF(sum(iff(act_bud = 'Retail Last Year', KWAZULU_NATAL, 0)), 0))-1)*100,2)) || '%' as KWAZULU_NATAL
    from base
    where act_bud in ('Retail Actual', 'Retail Last Year')
    group by all
    
    union
    
    select '' as act_bud,
            0 as act_bud_order,
            '' as INLAND_WEST,
            '' as INLAND_OUTLYING,
            '' as INLAND_NORTH,
            '' as INLAND_SOUTH,
            '' as INLAND_EAST,
            '' as WESTERN_CAPE,
            '' as KWAZULU_NATAL 
)

select act_bud as "Region",
            INLAND_WEST as "Inland West",
            INLAND_OUTLYING as "Inland Outlying",
            INLAND_NORTH as "Inland North",
            INLAND_SOUTH as "Inland South",
            INLAND_EAST as "Inland East",
            WESTERN_CAPE as "Western Cape",
            KWAZULU_NATAL as "KwaZulu-Natal"
from summary
order by act_bud_order