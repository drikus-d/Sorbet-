-- Get each individual date with its sales data, including days with no sales
with date_range as (
    select 
        dateadd(day, seq4(), to_date('{start_date}')) as payment_date
    from table(generator(rowcount => 7))
),
sales_data_ty as (
    select
        payment_date,
        sum(revenue) as sales_ty
    from marts.finance.fact_revenue r
    join marts.common.dim_center c on r.center_id = c.center_id
    where
        payment_date >= to_date('{start_date}')
        and payment_date <= to_date('{end_date}')
        and c.is_reporting_branch = true
        and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
    group by
        payment_date
),
sales_data_ly as (
    select
        payment_date,
        sum(revenue) as sales_ly
    from marts.finance.fact_revenue r
    join marts.common.dim_center c on r.center_id = c.center_id
    where
        payment_date >= dateadd(year, -1, to_date('{start_date}'))
        and payment_date <= dateadd(year, -1, to_date('{end_date}'))
        and c.is_reporting_branch = true
        and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
    group by
        payment_date
),
budget_data as (
    select
        cb.budget_date as payment_date,
        sum(cb.daily_service_budget + cb.daily_retail_budget) as sales_budget
    from marts.finance.fact_center_budget cb
    join marts.common.dim_center c on cb.center_name = c.reporting_center_name
    where
        cb.budget_date >= to_date('{start_date}')
        and cb.budget_date <= to_date('{end_date}')
        and c.is_reporting_branch = true
        and (c.closing_date < '2022-03-01' or c.closing_date is null)
    group by
        cb.budget_date
)
select
    dr.payment_date as dates_cy,
    'TEMP_DAY' as day_name,  -- Will be replaced by Python
    coalesce(sd_ty.sales_ty, 0) as sales_ty,
    coalesce(sd_ly.sales_ly, 0) as sales_ly,
    coalesce(bd.sales_budget, 0) as sales_budget
from date_range dr
left join sales_data_ty sd_ty on dr.payment_date = sd_ty.payment_date
left join sales_data_ly sd_ly on dr.payment_date = dateadd(year, 1, sd_ly.payment_date)
left join budget_data bd on dr.payment_date = bd.payment_date
order by dr.payment_date