with revenue as (
    select
        iff(
            payment_date >= to_date('{wtd_start_date}')
            and payment_date <= to_date('{end_date}'),
            'CURRENT',
            'PREVIOUS'
        ) as period,
        center_id,  
        iff(is_service, revenue, 0) as service_revenue,
        iff(is_retail, revenue, 0) as retail_revenue,
        revenue
    from
        marts.finance.fact_revenue
    where
        is_loyalty_payment = false and 
        (
            (
                payment_date >= to_date('{wtd_start_date}') and payment_date <= to_date('{end_date}')
            )
            or
            (
                payment_date >= dateadd(year, -1, to_date('{wtd_start_date}'))
                and payment_date <= dateadd(year, -1, to_date('{end_date}'))
            )
        )
),

budget as (
select distinct
    c.reporting_center_name as center,
    sum(cb.daily_service_budget) as service_budget,
    sum(cb.daily_retail_budget) as retail_budget,
    sum((cb.daily_service_budget + cb.daily_retail_budget)) as total_budget
from marts.finance.fact_center_budget as cb
inner join marts.common.dim_center  as c
    on cb.center_name = c.reporting_center_name
where
    cb.budget_date >= to_date('{wtd_start_date}') and cb.budget_date <= to_date('{end_date}') 
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
        SUB_REGION,
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
        c.brand,
        c.region,
        c.sub_region,
        c.category,
        c.center,
        c.is_icu,
        iff(c.closing_date <= '{end_date}' and c.closing_date >= '2024-09-01', true, false) as is_closed,
        iff(c.opening_date >= '2024-09-01', true, false) as is_new,
        count(distinct c.center) as store_count,
        sum(iff(period = 'CURRENT', service_revenue, 0)) as current_service_revenue,
        sum(iff(period = 'CURRENT', retail_revenue, 0)) as current_retail_revenue,
        sum(iff(period = 'CURRENT', r.revenue, 0)) as current_total_revenue,
        sum(iff(period = 'PREVIOUS', service_revenue, 0)) as previous_service_revenue,
        sum(iff(period = 'PREVIOUS', retail_revenue, 0)) as previous_retail_revenue,
        sum(iff(period = 'PREVIOUS', r.revenue, 0)) as previous_total_revenue
       from revenue as r
    left join center as c
        on c.center_id = r.center_id
    where brand != 'No Zone' and is_reporting_branch = true 
    and brand is not null
    and (c.closing_date < '2022-03-01' or c.closing_date is null)
    group by all
    ),
records as (
    select
        ba.brand,
        ba.region,
        ba.sub_region,
        ba.category,
        ba.center,
        ba.is_icu,
        ba.is_closed,
        ba.is_new,
        iff(current_total_revenue > 0, ba.store_count, 0) as current_store_count,
        iff(previous_total_revenue > 0, ba.store_count, 0) as previous_store_count,
        ba.current_service_revenue,
        ba.current_retail_revenue,
        ba.current_total_revenue,
        ba.previous_service_revenue,
        ba.previous_retail_revenue,
        ba.previous_total_revenue,
        b.service_budget,
        b.retail_budget,
        b.total_budget
    from base as ba 
    left join budget as b 
        on b.center = ba.center
)
select * from records


