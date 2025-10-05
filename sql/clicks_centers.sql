with base_lines as (
    select
        c.reporting_center_name as center,
        sum(r.revenue) as revenue,
        
        count(distinct r.invoice_no) as total_transaction_count,
        count(distinct r.guest_code) as unique_guest_count,
        count(
            distinct iff(r.is_first_visit = true, r.guest_code, null)
        ) as new_guest_count,

        -- Clicks Section
        sum(
            iff(r.is_clicks_loyalty = true, r.revenue, 0)
        ) as clicks_revenue,
        count(
            distinct iff(r.is_clicks_loyalty = true, r.invoice_no, null)
        ) as clicks_transaction_count,
        count(
            distinct iff(r.is_clicks_loyalty = true, r.guest_code, null)
        ) as clicks_unique_guest_count,
        count(
            distinct iff(
                r.is_first_visit = true,
                iff(r.is_clicks_loyalty = true, r.guest_code, null),
                null
            )
        ) as clicks_new_guest_count,

        -- Non Clicks Section
        sum(
            iff(r.is_clicks_loyalty = false, r.revenue, 0)
        ) as non_clicks_revenue,
        count(
            distinct iff(r.is_clicks_loyalty = false, r.invoice_no, null)
        ) as non_clicks_transaction_count,
        count(
            distinct iff(r.is_clicks_loyalty = false, r.guest_code, null)
        ) as non_clicks_unique_guest_count,
        count(
            distinct iff(
                r.is_first_visit = true,
                iff(r.is_clicks_loyalty = false, r.guest_code, null),
                null
            )
        ) as non_clicks_new_guest_count

    from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c on c.center_id = r.center_id
     where
            (
                payment_date >= to_date('{start_date}')
                and payment_date <= to_date('{end_date}')
            )
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
    group by
        all
)
select 
    center, 
    revenue,
    clicks_revenue,
    non_clicks_revenue,
    total_transaction_count,
    clicks_transaction_count,
    non_clicks_transaction_count,
    new_guest_count,
    unique_guest_count,
    clicks_new_guest_count,
    clicks_unique_guest_count
from base_lines