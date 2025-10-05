with revenue as (
    select
        iff(
            payment_date >= to_date('{ytd_start_date}') --ytd_start_date
            and payment_date <= to_date('{end_date}'), --end_date
            'CURRENT',
            'PREVIOUS'
        ) as period,
        center_id,  
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
        sum(revenue) as revenue
    from
        marts.finance.fact_revenue
    where
        is_loyalty_payment = false and 
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
center as (
    select
        CENTER_ID,
        REPORTING_BRAND_NAME as brand,
        REPORTING_CENTER_NAME as center,
        center_code,
        REGION,
        CATEGORY,
        STORE_SIZE,
        OPENING_DATE,
        CLOSING_DATE,
        IS_ICU,
        is_reporting_branch
    from
        marts.common.dim_center
    where is_reporting_branch = true
	and (closing_date < '2022-03-01' or closing_date is null)
),
base as (
    select
        'Actual' as act_bud,
        1 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1, revenue, 0)))) as wtd,
        TO_VARCHAR(round(sum(iff(mtd = 1, revenue, 0)))) as mtd,
        TO_VARCHAR(round(sum(r.revenue))) as ytd        
    from revenue as r
    left join center as c
        on c.center_id = r.center_id
    where brand != 'No Zone' and is_reporting_branch = true 
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and brand is not null
        and period = 'CURRENT'
    group by all

    union

    select
        'Last Year' as act_bud,
        3 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1, revenue, 0)))) as wtd,
        TO_VARCHAR(round(sum(iff(mtd = 1, revenue, 0)))) as mtd,
        TO_VARCHAR(round(sum(r.revenue))) as ytd
    from revenue as r
    left join center as c
        on c.center_id = r.center_id
    where brand != 'No Zone' and is_reporting_branch = true 
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and brand is not null
        and period = 'PREVIOUS'
    group by all

    union

    select
        'Budget' as act_bud,
        2 as act_bud_order,
        TO_VARCHAR(round(sum(iff(wtd = 1, total_budget, 0)))) as wtd,
        TO_VARCHAR(round(sum(iff(mtd = 1, total_budget, 0)))) as mtd,
        TO_VARCHAR(round(sum(total_budget))) as ytd
    from budget as r
    group by all
),
summary as (
    select *
    from base
    
    union
    
    select 'Last Year %' as act_bud,
            4 as act_bud_order,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', wtd, 0)) / sum(iff(act_bud = 'Last Year', wtd, 0)))-1)*100,1)) || '%' as wtd,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', mtd, 0)) / sum(iff(act_bud = 'Last Year', mtd, 0)))-1)*100,1)) || '%' as mtd,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', ytd, 0)) / sum(iff(act_bud = 'Last Year', ytd, 0)))-1)*100,1)) || '%' as ytd   
    from base
    group by all
    
    union
    
    select 'Budget Variance Rands' as act_bud,
            5 as act_bud_order,
            TO_VARCHAR(round(sum(iff(act_bud = 'Actual', wtd, 0)) - sum(iff(act_bud = 'Budget', wtd, 0)))) as wtd,
            TO_VARCHAR(round(sum(iff(act_bud = 'Actual', mtd, 0)) - sum(iff(act_bud = 'Budget', mtd, 0)))) as mtd,
            TO_VARCHAR(round(sum(iff(act_bud = 'Actual', ytd, 0)) - sum(iff(act_bud = 'Budget', ytd, 0)))) as ytd   
    from base
    group by all
    
    union
    
    select 'Budget Variance %' as act_bud,
            6 as act_bud_order,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', wtd, 0)) / sum(iff(act_bud = 'Budget', wtd, 0)))-1)*100,1)) || '%' as wtd,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', mtd, 0)) / sum(iff(act_bud = 'Budget', mtd, 0)))-1)*100,1)) || '%' as mtd,
            TO_VARCHAR(ROUND(((sum(iff(act_bud = 'Actual', ytd, 0)) / sum(iff(act_bud = 'Budget', ytd, 0)))-1)*100,1)) || '%' as ytd   
    from base
    group by all
    
    union
    
    select '' as act_bud,
            0 as act_bud_order,
            'Rand' as wtd,
            'Rand' as mtd,
            'Rand' as ytd 
)

select act_bud as "Total Sales",
            wtd as "Last Week",
            mtd as "MTD",
            ytd as "YTD"
from summary
order by act_bud_order