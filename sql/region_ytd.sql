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
            and payment_date <= dateadd(year,-1,to_date('{end_date}')))--end_date
            , 
            1,
            0
        ) as mtd,
        -- iff(is_service, revenue, 0) as service_revenue,
        -- iff(is_retail, revenue, 0) as retail_revenue,
        c.region,
        sum(revenue) as revenue
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
    group by all
),

budget as (
select distinct
    c.reporting_center_name as center,
    iff(
        (budget_date >= to_date('{wtd_start_date}') --wtd_start_date            
        and budget_date <= to_date('{end_date}'))--end_date
        or (budget_date >= dateadd(year,-1,to_date('{wtd_start_date}')) --wtd_start_date            
        and budget_date <= dateadd(year,-1,to_date('{end_date}')))--end_date
        , 
        1,
        0
    ) as wtd,
    iff(
        (budget_date >= to_date('{mtd_start_date}') --mtd_start_date            
        and budget_date <= to_date('{end_date}'))--end_date
        or (budget_date >= dateadd(year,-1,to_date('{mtd_start_date}')) --mtd_start_date            
        and budget_date <= dateadd(year,-1,to_date('{end_date}')))--end_date
        , 
        1,
        0
    ) as mtd,
    -- sum(cb.daily_service_budget) as service_budget,
    -- sum(cb.daily_retail_budget) as retail_budget,
    c.region,
    sum((cb.daily_service_budget + cb.daily_retail_budget)) as total_budget
from marts.finance.fact_center_budget as cb
inner join marts.common.dim_center as c
    on cb.center_name = c.reporting_center_name
where
    cb.budget_date >= to_date('{ytd_start_date}') and cb.budget_date <= to_date('{end_date}') 
      and coalesce(c.OPENING_DATE, '2015-01-01') <='{end_date}'
    and c.center_code is not null
    and c.reporting_brand_name != 'No Zone'
    and (c.closing_date < '2022-03-01' or c.closing_date is null)
    and c.is_reporting_branch = true
    and c.center_id is not  null
    group by all
),
base as (
    select
        'Actual' as act_bud,
        --TO_VARCHAR(round(sum(iff(wtd = 1, revenue, 0)))) as wtd,
        --TO_VARCHAR(round(sum(iff(mtd = 1, revenue, 0)))) as mtd,
        --TO_VARCHAR(round(sum(r.revenue))) as ytd
        TO_VARCHAR(round(sum(iff(region = 'Inland - West', revenue, 0)))) as INLAND_WEST,
        TO_VARCHAR(round(sum(iff(region = 'Inland - Outlying', revenue, 0)))) as INLAND_OUTLYING,
        TO_VARCHAR(round(sum(iff(region = 'Inland - North', revenue, 0)))) as INLAND_NORTH,
        TO_VARCHAR(round(sum(iff(region = 'Inland - South', revenue, 0)))) as INLAND_SOUTH,
        TO_VARCHAR(round(sum(iff(region = 'Inland - East', revenue, 0)))) as INLAND_EAST,
        TO_VARCHAR(round(sum(iff(region = 'Western Cape', revenue, 0)))) as WESTERN_CAPE,
        TO_VARCHAR(round(sum(iff(region = 'KwaZulu-Natal', revenue, 0)))) as KWAZULU_NATAL
    from revenue as r
    where period = 'CURRENT'
    group by all

    union

    select
        'Last Year' as act_bud,
        -- TO_VARCHAR(round(sum(iff(wtd = 1, revenue, 0)))) as wtd,
        -- TO_VARCHAR(round(sum(iff(mtd = 1, revenue, 0)))) as mtd,
        -- TO_VARCHAR(round(sum(r.revenue))) as ytd
        TO_VARCHAR(round(sum(iff(region = 'Inland - West', revenue, 0)))) as INLAND_WEST,
        TO_VARCHAR(round(sum(iff(region = 'Inland - Outlying', revenue, 0)))) as INLAND_OUTLYING,
        TO_VARCHAR(round(sum(iff(region = 'Inland - North', revenue, 0)))) as INLAND_NORTH,
        TO_VARCHAR(round(sum(iff(region = 'Inland - South', revenue, 0)))) as INLAND_SOUTH,
        TO_VARCHAR(round(sum(iff(region = 'Inland - East', revenue, 0)))) as INLAND_EAST,
        TO_VARCHAR(round(sum(iff(region = 'Western Cape', revenue, 0)))) as WESTERN_CAPE,
        TO_VARCHAR(round(sum(iff(region = 'KwaZulu-Natal', revenue, 0)))) as KWAZULU_NATAL
    from revenue as r
    where period = 'PREVIOUS'
    group by all

    union

    select
        'Budget' as act_bud,
        -- TO_VARCHAR(round(sum(iff(wtd = 1, total_budget, 0)))) as wtd,
        -- TO_VARCHAR(round(sum(iff(mtd = 1, total_budget, 0)))) as mtd,
        -- TO_VARCHAR(round(sum(total_budget))) as ytd
        TO_VARCHAR(round(sum(iff(region = 'Inland - West', total_budget, 0)))) as "Inland - West",
        TO_VARCHAR(round(sum(iff(region = 'Inland - Outlying', total_budget, 0)))) as "Inland - Outlying",
        TO_VARCHAR(round(sum(iff(region = 'Inland - North', total_budget, 0)))) as "Inland - North",
        TO_VARCHAR(round(sum(iff(region = 'Inland - South', total_budget, 0)))) as "Inland - South",
        TO_VARCHAR(round(sum(iff(region = 'Inland - East', total_budget, 0)))) as "Inland - East",
        TO_VARCHAR(round(sum(iff(region = 'Western Cape', total_budget, 0)))) as "Western Cape",
        TO_VARCHAR(round(sum(iff(region = 'KwaZulu-Natal', total_budget, 0)))) as "KwaZulu-Natal"
    from budget as r
    group by all
),
summary as (
    select *
    from base
    
    union
    
    select 'Last Year %' as act_bud,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_WEST, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', INLAND_WEST, 0)), 0))-1)*100,2)) || '%' as INLAND_WEST,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_OUTLYING, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', INLAND_OUTLYING, 0)), 0))-1)*100,2)) || '%' as INLAND_OUTLYING,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_NORTH, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', INLAND_NORTH, 0)), 0))-1)*100,2)) || '%' as INLAND_NORTH,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_SOUTH, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', INLAND_SOUTH, 0)), 0))-1)*100,2)) || '%' as INLAND_SOUTH,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_EAST, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', INLAND_EAST, 0)), 0))-1)*100,2)) || '%' as INLAND_EAST,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', WESTERN_CAPE, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', WESTERN_CAPE, 0)), 0))-1)*100,2)) || '%' as WESTERN_CAPE,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', KWAZULU_NATAL, 0)) / NULLIF(sum(iff(act_bud = 'Last Year', KWAZULU_NATAL, 0)), 0))-1)*100,2)) || '%' as KWAZULU_NATAL
    from base
    group by all
    
    union
    
    select 'Budget Variance Rands' as act_bud,
            TO_VARCHAR(round(sum(iff(act_bud = 'Actual', INLAND_WEST, 0)) - sum(iff(act_bud = 'Budget', INLAND_WEST, 0)))) as INLAND_WEST,
            TO_VARCHAR(round(sum(iff(act_bud = 'Actual', INLAND_OUTLYING, 0)) - sum(iff(act_bud = 'Budget', INLAND_OUTLYING, 0)))) as INLAND_OUTLYING,
            TO_VARCHAR(round(sum(iff(act_bud = 'Actual', INLAND_NORTH, 0)) - sum(iff(act_bud = 'Budget', INLAND_NORTH, 0)))) as INLAND_NORTH,
            TO_VARCHAR(round(sum(iff(act_bud = 'Actual', INLAND_SOUTH, 0)) - sum(iff(act_bud = 'Budget', INLAND_SOUTH, 0)))) as INLAND_SOUTH,
            TO_VARCHAR(round(sum(iff(act_bud = 'Actual', INLAND_EAST, 0)) - sum(iff(act_bud = 'Budget', INLAND_EAST, 0)))) as INLAND_EAST,
            TO_VARCHAR(round(sum(iff(act_bud = 'Actual', WESTERN_CAPE, 0)) - sum(iff(act_bud = 'Budget', WESTERN_CAPE, 0)))) as WESTERN_CAPE,
            TO_VARCHAR(round(sum(iff(act_bud = 'Actual', KWAZULU_NATAL, 0)) - sum(iff(act_bud = 'Budget', KWAZULU_NATAL, 0)))) as KWAZULU_NATAL   
    from base
    group by all
    
    union
    
    select 'Budget Variance %' as act_bud,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_WEST, 0)) / NULLIF(sum(iff(act_bud = 'Budget', INLAND_WEST, 0)), 0))-1)*100,2)) || '%' as INLAND_WEST,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_OUTLYING, 0)) / NULLIF(sum(iff(act_bud = 'Budget', INLAND_OUTLYING, 0)), 0))-1)*100,2)) || '%' as INLAND_OUTLYING,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_NORTH, 0)) / NULLIF(sum(iff(act_bud = 'Budget', INLAND_NORTH, 0)), 0))-1)*100,2)) || '%' as INLAND_NORTH,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_SOUTH, 0)) / NULLIF(sum(iff(act_bud = 'Budget', INLAND_SOUTH, 0)), 0))-1)*100,2)) || '%' as INLAND_SOUTH,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', INLAND_EAST, 0)) / NULLIF(sum(iff(act_bud = 'Budget', INLAND_EAST, 0)), 0))-1)*100,2)) || '%' as INLAND_EAST,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', WESTERN_CAPE, 0)) / NULLIF(sum(iff(act_bud = 'Budget', WESTERN_CAPE, 0)), 0))-1)*100,2)) || '%' as WESTERN_CAPE,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', KWAZULU_NATAL, 0)) / NULLIF(sum(iff(act_bud = 'Budget', KWAZULU_NATAL, 0)), 0))-1)*100,2)) || '%' as KWAZULU_NATAL   
    from base
    group by all
    
    union
    
    select '' as act_bud,
            'Rand' as INLAND_WEST,
            'Rand' as INLAND_OUTLYING,
            'Rand' as INLAND_NORTH,
            'Rand' as INLAND_SOUTH,
            'Rand' as INLAND_EAST,
            'Rand' as WESTERN_CAPE,
            'Rand' as KWAZULU_NATAL 
)

select act_bud as "Region",
            INLAND_WEST as "Inland - West",
            INLAND_OUTLYING as "Inland - Outlying",
            INLAND_NORTH as "Inland - North",
            INLAND_SOUTH as "Inland - South",
            INLAND_EAST as "Inland - East",
            WESTERN_CAPE as "Western Cape",
            KWAZULU_NATAL as "KwaZulu-Natal"
from summary
order by case act_bud
    when 'Actual' then 1
    when 'Budget' then 2
    when 'Last Year' then 3
    when 'Last Year %' then 4
    when 'Budget Variance Rands' then 5
    when 'Budget Variance %' then 6
    else 0
end