with base_lines as (
    select
        iff(
            (r.payment_date >= to_date('{start_date}')
            and r.payment_date <= to_date('{end_date}')),
            'CURRENT',
            iff(
                (r.payment_date >= dateadd(year,-1,to_date('{start_date}'))
                and r.payment_date <= dateadd(year,-1,to_date('{end_date}'))),
                'PREVIOUS',
                null
            )
        ) as period,
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
            (
                payment_date >= to_date('{start_date}')
                and payment_date <= to_date('{end_date}')
            )
            or (
                payment_date >= dateadd(year, -1, to_date('{start_date}'))
                and payment_date <= dateadd(year, -1, to_date('{end_date}'))
            )
        )
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
        and period is not null
    group by
        period
),
rolling_12_months as
(
    select
        iff(
            r.payment_date > dateadd(year, -1,to_date('{end_date}'))
            and r.payment_date <= to_date('{end_date}'),
            'CURRENT',
            'PREVIOUS'
        ) as period,
        count(distinct r.invoice_no) as total_transaction_count_rolling_12_months,
        count(distinct r.guest_code) as unique_guest_count_rolling_12_months
    from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c on c.center_id = r.center_id
    where
        (
            (
                payment_date > dateadd(year, -1,to_date('{end_date}'))
                and payment_date <= to_date('{end_date}')
            )
            or (
                payment_date > dateadd(year, -2,to_date('{end_date}'))
                and payment_date <= dateadd(year, -1,to_date('{end_date}'))
            )
        )
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
    group by
        period
),
rolling_12_months_clicks_clubcard as
(
    select
        iff(
            r.payment_date > dateadd(year, -1,to_date('{end_date}'))
            and r.payment_date <= to_date('{end_date}'),
            'CURRENT',
            'PREVIOUS'
        ) as period,
        count(distinct r.invoice_no) as total_transaction_count_rolling_12_months_clicks_clubcard,
        count(distinct r.guest_code) as unique_guest_count_rolling_12_months_clicks_clubcard
    from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c on c.center_id = r.center_id
    where
        (
            (
                payment_date > dateadd(year, -1,to_date('{end_date}'))
                and payment_date <= to_date('{end_date}')
            )
            or (
                payment_date > dateadd(year, -2,to_date('{end_date}'))
                and payment_date <= dateadd(year, -1,to_date('{end_date}'))
            )
        )
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
        and (CLICKS_CLUBCARD IS NOT NULL
            and LTRIM(RTRIM(CLICKS_CLUBCARD)) <> ''
            and LTRIM(RTRIM(CLICKS_CLUBCARD)) <> '-')
    group by
        period
),
rolling_12_months_service as
(
    select
        iff(
            r.payment_date > dateadd(year, -1,to_date('{end_date}'))
            and r.payment_date <= to_date('{end_date}'),
            'CURRENT',
            'PREVIOUS'
        ) as period,
        count(distinct r.invoice_no) as total_transaction_count_rolling_12_months_service,
        count(distinct r.guest_code) as unique_guest_count_rolling_12_months_service
    from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c on c.center_id = r.center_id
    where
        (
            (
                payment_date > dateadd(year, -1,to_date('{end_date}'))
                and payment_date <= to_date('{end_date}')
            )
            or (
                payment_date > dateadd(year, -2,to_date('{end_date}'))
                and payment_date <= dateadd(year, -1,to_date('{end_date}'))
            )
        )
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
        and r.is_service = true
    group by
        period
),
rolling_12_months_retail as
(
    select
        iff(
            r.payment_date > dateadd(year, -1,to_date('{end_date}'))
            and r.payment_date <= to_date('{end_date}'),
            'CURRENT',
            'PREVIOUS'
        ) as period,
        count(distinct r.invoice_no) as total_transaction_count_rolling_12_months_retail,
        count(distinct r.guest_code) as unique_guest_count_rolling_12_months_retail
    from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c on c.center_id = r.center_id
    where
        (
            (
                payment_date > dateadd(year, -1,to_date('{end_date}'))
                and payment_date <= to_date('{end_date}')
            )
            or (
                payment_date > dateadd(year, -2,to_date('{end_date}'))
                and payment_date <= dateadd(year, -1,to_date('{end_date}'))
            )
        )
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
        and r.is_retail = true
    group by
        period
),
rolling_12_months_clicks_clubcard_service as
(
    select
        iff(
            r.payment_date > dateadd(year, -1,to_date('{end_date}'))
            and r.payment_date <= to_date('{end_date}'),
            'CURRENT',
            'PREVIOUS'
        ) as period,
        count(distinct r.invoice_no) as total_transaction_count_rolling_12_months_clicks_clubcard_service,
        count(distinct r.guest_code) as unique_guest_count_rolling_12_months_clicks_clubcard_service
    from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c on c.center_id = r.center_id
    where
        (
            (
                payment_date > dateadd(year, -1,to_date('{end_date}'))
                and payment_date <= to_date('{end_date}')
            )
            or (
                payment_date > dateadd(year, -2,to_date('{end_date}'))
                and payment_date <= dateadd(year, -1,to_date('{end_date}'))
            )
        )
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
        and r.is_service = true
        and (CLICKS_CLUBCARD IS NOT NULL
            and LTRIM(RTRIM(CLICKS_CLUBCARD)) <> ''
            and LTRIM(RTRIM(CLICKS_CLUBCARD)) <> '-')
    group by
        period
),
rolling_12_months_clicks_clubcard_retail as
(
    select
        iff(
            r.payment_date > dateadd(year, -1,to_date('{end_date}'))
            and r.payment_date <= to_date('{end_date}'),
            'CURRENT',
            'PREVIOUS'
        ) as period,
        count(distinct r.invoice_no) as total_transaction_count_rolling_12_months_clicks_clubcard_retail,
        count(distinct r.guest_code) as unique_guest_count_rolling_12_months_clicks_clubcard_retail
    from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c on c.center_id = r.center_id
    where
        (
            (
                payment_date > dateadd(year, -1,to_date('{end_date}'))
                and payment_date <= to_date('{end_date}')
            )
            or (
                payment_date > dateadd(year, -2,to_date('{end_date}'))
                and payment_date <= dateadd(year, -1,to_date('{end_date}'))
            )
        )
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
        and r.is_retail = true
        and (CLICKS_CLUBCARD IS NOT NULL
            and LTRIM(RTRIM(CLICKS_CLUBCARD)) <> ''
            and LTRIM(RTRIM(CLICKS_CLUBCARD)) <> '-')
    group by
        period
)
select
    bl.period,
    clicks_revenue as clicks_loyalty_sales,
    non_clicks_revenue as non_clicks_sales,
    revenue as sales,
    clicks_revenue/revenue as clicks_loyalty_sales_over_total,

    clicks_transaction_count as clicks_loyalty_transaction_count,
    non_clicks_transaction_count,
    total_transaction_count,
    clicks_transaction_count/total_transaction_count as clicks_loyalty_transactions_over_total,

    clicks_revenue/clicks_transaction_count as clicks_loyalty_basket_size,
    non_clicks_revenue/non_clicks_transaction_count as non_clicks_basket_size,
    revenue/total_transaction_count as basket_size_total,
    clicks_loyalty_basket_size/basket_size_total as click_loyalty_basket_size_over_total,

    clicks_new_guest_count as clicks_loyalty_new_guest_count,
    new_guest_count,
    clicks_new_guest_count/new_guest_count as new_clicks_loyalty_guest_over_new_guests,

    unique_guest_count,
    clicks_new_guest_count/unique_guest_count as clicks_loyalty_new_guests_over_total_unique_guests,

    round(r12.total_transaction_count_rolling_12_months/r12.unique_guest_count_rolling_12_months,4) as frequency_of_spend_rolling_12_months,
    round(r12cc.total_transaction_count_rolling_12_months_clicks_clubcard/r12cc.unique_guest_count_rolling_12_months_clicks_clubcard,4) as frequency_of_spend_rolling_12_months_clicks_clubcard,
    
    round(r12s.total_transaction_count_rolling_12_months_service/r12s.unique_guest_count_rolling_12_months_service,4) as frequency_of_spend_rolling_12_months_service,
    round(r12r.total_transaction_count_rolling_12_months_retail/r12r.unique_guest_count_rolling_12_months_retail,4) as frequency_of_spend_rolling_12_months_retail,
    round(r12ccs.total_transaction_count_rolling_12_months_clicks_clubcard_service/r12ccs.unique_guest_count_rolling_12_months_clicks_clubcard_service,4) as frequency_of_spend_rolling_12_months_clicks_clubcard_service,
    round(r12ccr.total_transaction_count_rolling_12_months_clicks_clubcard_retail/r12ccr.unique_guest_count_rolling_12_months_clicks_clubcard_retail,4) as frequency_of_spend_rolling_12_months_clicks_clubcard_retail
    
from
    base_lines bl
left join rolling_12_months r12
    on bl.period = r12.period
left join rolling_12_months_clicks_clubcard r12cc
    on bl.period = r12cc.period
left join rolling_12_months_service r12s
    on bl.period = r12s.period
left join rolling_12_months_retail r12r
    on bl.period = r12r.period
left join rolling_12_months_clicks_clubcard_service r12ccs
    on bl.period = r12ccs.period
left join rolling_12_months_clicks_clubcard_retail r12ccr
    on bl.period = r12ccr.period