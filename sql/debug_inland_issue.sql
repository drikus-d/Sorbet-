-- Debug: Check if 'Inland' region exists and has data
select 
    c.region,
    count(*) as center_count,
    sum(r.revenue) as total_revenue,
    count(distinct r.invoice_no) as transaction_count
from marts.finance.fact_revenue r
inner join marts.common.dim_center as c
    on c.center_id = r.center_id
    and c.is_reporting_branch = true
where 
    REPORTING_BRAND_NAME != 'No Zone' 
    and is_reporting_branch = true 
    and REPORTING_BRAND_NAME is not null
    and (c.closing_date < '2022-03-01' or c.closing_date is null)
    and is_loyalty_payment = false
    and c.region in ('Inland', 'Inland - West', 'Inland - Outlying', 'Inland - North', 'Inland - South', 'Inland - East')
    and (
        (payment_date >= to_date('{mtd_start_date}') and payment_date <= to_date('{end_date}'))
        or
        (payment_date >= dateadd(year, -1, to_date('{mtd_start_date}')) and payment_date <= dateadd(year, -1, to_date('{end_date}')))
    )
group by c.region
order by c.region




