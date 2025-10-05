with base as (
    select
        iff(
            r.payment_date >= to_date('{start_date}')
            and r.payment_date <= to_date('{end_date}'),
            'CURRENT',
            'PREVIOUS'
        ) as period,
        r.guest_code,
        t.tier_name,
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
                payment_date >= to_date('{start_date}') and payment_date <= to_date('{end_date}')
            )
            or
            (
                payment_date >= dateadd(year, -1, to_date('{start_date}'))
                and payment_date <= dateadd(year, -1, to_date('{end_date}'))
            )
        )
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and c.REPORTING_BRAND_NAME != 'No Zone' and c.is_reporting_branch = true 
        and c.REPORTING_BRAND_NAME is not null
        
),
split_tiers as (
    select 
        period,
        tier_name,
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
grouped_loyalty as (
    select
        period,
        'Total Loyalty' as tier_name,
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
    where tier_name in ('Green', 'Gold', 'Blue', 'Silver')
    group by all
),
grouped_all as (
    select
        period,
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

rolling_12_month_spend as (
    select
        t.tier_name,
        count(distinct r.guest_code) as rolling_unique_guest,
        count(distinct r.invoice_no) as rolling_transactions,
        round(rolling_transactions::DECIMAL(18,6)/ NULLIF(rolling_unique_guest, 0), 4) as frequency_spend_rolling_12,
        
        -- Service frequency
        count(distinct iff(r.is_service = true, r.guest_code, null)) as rolling_unique_guest_service,
        count(distinct iff(r.is_service = true, r.invoice_no, null)) as rolling_transactions_service,
        (rolling_transactions_service::DECIMAL(18,6)/ NULLIF(rolling_unique_guest_service, 0))::DECIMAL(18,6) as frequency_spend_rolling_12_service,
        
        -- Retail frequency
        count(distinct iff(r.is_retail = true, r.guest_code, null)) as rolling_unique_guest_retail,
        count(distinct iff(r.is_retail = true, r.invoice_no, null)) as rolling_transactions_retail,
        (rolling_transactions_retail::DECIMAL(18,6)/ NULLIF(rolling_unique_guest_retail, 0))::DECIMAL(18,6) as frequency_spend_rolling_12_retail
        
    from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c
            on c.center_id = r.center_id
        left join marts.finance.dim_tier as t
            on t.tier_id = r.tier_id
    where   
        payment_date > dateadd(year, -1, to_date('{end_date}')) and payment_date <= to_date('{end_date}')
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
        group by all
),
rolling_12_month_spend_grouped_loyalty as (
    select
        'Total Loyalty' as tier_name,
        count(distinct r.guest_code) as rolling_unique_guest,
        count(distinct r.invoice_no) as rolling_transactions,
        round(rolling_transactions::DECIMAL(18,6)/ NULLIF(rolling_unique_guest, 0), 4) as frequency_spend_rolling_12,
        
        -- Service frequency
        count(distinct iff(r.is_service = true, r.guest_code, null)) as rolling_unique_guest_service,
        count(distinct iff(r.is_service = true, r.invoice_no, null)) as rolling_transactions_service,
        (rolling_transactions_service::DECIMAL(18,6)/ NULLIF(rolling_unique_guest_service, 0))::DECIMAL(18,6) as frequency_spend_rolling_12_service,
        
        -- Retail frequency
        count(distinct iff(r.is_retail = true, r.guest_code, null)) as rolling_unique_guest_retail,
        count(distinct iff(r.is_retail = true, r.invoice_no, null)) as rolling_transactions_retail,
        (rolling_transactions_retail::DECIMAL(18,6)/ NULLIF(rolling_unique_guest_retail, 0))::DECIMAL(18,6) as frequency_spend_rolling_12_retail
        
    from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c
            on c.center_id = r.center_id
        left join marts.finance.dim_tier as t
            on t.tier_id = r.tier_id
    where   
        payment_date > dateadd(year, -1, to_date('{end_date}')) and payment_date <= to_date('{end_date}')
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
        and tier_name in ('Green', 'Gold', 'Blue', 'Silver')
        group by all
),
rolling_12_month_spend_grouped as (
    select
        'Total' as tier_name,
        count(distinct r.guest_code) as rolling_unique_guest,
        count(distinct r.invoice_no) as rolling_transactions,
        round(rolling_transactions::DECIMAL(18,6)/ NULLIF(rolling_unique_guest, 0), 4) as frequency_spend_rolling_12,
        
        -- Service frequency
        count(distinct iff(r.is_service = true, r.guest_code, null)) as rolling_unique_guest_service,
        count(distinct iff(r.is_service = true, r.invoice_no, null)) as rolling_transactions_service,
        (rolling_transactions_service::DECIMAL(18,6)/ NULLIF(rolling_unique_guest_service, 0))::DECIMAL(18,6) as frequency_spend_rolling_12_service,
        
        -- Retail frequency
        count(distinct iff(r.is_retail = true, r.guest_code, null)) as rolling_unique_guest_retail,
        count(distinct iff(r.is_retail = true, r.invoice_no, null)) as rolling_transactions_retail,
        (rolling_transactions_retail::DECIMAL(18,6)/ NULLIF(rolling_unique_guest_retail, 0))::DECIMAL(18,6) as frequency_spend_rolling_12_retail
        
    from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c
            on c.center_id = r.center_id
        left join marts.finance.dim_tier as t
            on t.tier_id = r.tier_id
    where   
        payment_date > dateadd(year, -1, to_date('{end_date}')) and payment_date <= to_date('{end_date}')
        and c.is_reporting_branch = true
	and (c.closing_date < '2022-03-01' or c.closing_date is null)
        and r.is_loyalty_payment = false
        group by all
    ),
base_union_tables as (
    select * from split_tiers
    union all
    select * from grouped_loyalty
    union all
    select * from grouped_all
),-- PRIOR YEAR rolling 12 months
rolling_12_month_spend_prior as (
    select
        t.tier_name,
        count(distinct r.guest_code) as rolling_unique_guest_prior,
        count(distinct r.invoice_no) as rolling_transactions_prior,
        round(rolling_transactions_prior::DECIMAL(18,6)/ NULLIF(rolling_unique_guest_prior, 0), 4) as frequency_spend_rolling_12_prior
    from marts.finance.fact_revenue as r
    left join marts.common.dim_center as c on c.center_id = r.center_id
    left join marts.finance.dim_tier as t on t.tier_id = r.tier_id
    where payment_date > dateadd(year, -2, to_date('{end_date}')) 
      and payment_date <= dateadd(year, -1, to_date('{end_date}'))
      and c.is_reporting_branch = true
      and (c.closing_date < '2022-03-01' or c.closing_date is null)
      and r.is_loyalty_payment = false
    group by all
),
rolling_12_month_spend_prior_grouped_loyalty as (
    select
        'Total Loyalty' as tier_name,
        count(distinct r.guest_code) as rolling_unique_guest_prior,
        count(distinct r.invoice_no) as rolling_transactions_prior,
        round(rolling_transactions_prior::DECIMAL(18,6)/ NULLIF(rolling_unique_guest_prior, 0), 4) as frequency_spend_rolling_12_prior
    from marts.finance.fact_revenue as r
    left join marts.common.dim_center as c on c.center_id = r.center_id
    left join marts.finance.dim_tier as t on t.tier_id = r.tier_id
    where payment_date > dateadd(year, -2, to_date('{end_date}')) 
      and payment_date <= dateadd(year, -1, to_date('{end_date}'))
      and c.is_reporting_branch = true
      and (c.closing_date < '2022-03-01' or c.closing_date is null)
      and r.is_loyalty_payment = false
      and tier_name in ('Green', 'Gold', 'Blue', 'Silver')
    group by all
),
rolling_12_month_spend_prior_grouped as (
    select
        'Total' as tier_name,
        count(distinct r.guest_code) as rolling_unique_guest_prior,
        count(distinct r.invoice_no) as rolling_transactions_prior,
        round(rolling_transactions_prior::DECIMAL(18,6)/ NULLIF(rolling_unique_guest_prior, 0), 4) as frequency_spend_rolling_12_prior
    from marts.finance.fact_revenue as r
    left join marts.common.dim_center as c on c.center_id = r.center_id
    left join marts.finance.dim_tier as t on t.tier_id = r.tier_id
    where payment_date > dateadd(year, -2, to_date('{end_date}')) 
      and payment_date <= dateadd(year, -1, to_date('{end_date}'))
      and c.is_reporting_branch = true
      and (c.closing_date < '2022-03-01' or c.closing_date is null)
      and r.is_loyalty_payment = false
    group by all
),

base_union_tables as (
    select * from split_tiers
    union all
    select * from grouped_loyalty
    union all
    select * from grouped_all
),

union_rolling as (
    select tier_name, frequency_spend_rolling_12, null as frequency_spend_rolling_12_prior, 
           frequency_spend_rolling_12_service, null as frequency_spend_rolling_12_service_prior,
           frequency_spend_rolling_12_retail, null as frequency_spend_rolling_12_retail_prior
    from rolling_12_month_spend
    union all
    select tier_name, frequency_spend_rolling_12, null, 
           frequency_spend_rolling_12_service, null,
           frequency_spend_rolling_12_retail, null
    from rolling_12_month_spend_grouped_loyalty
    union all
    select tier_name, frequency_spend_rolling_12, null,
           frequency_spend_rolling_12_service, null,
           frequency_spend_rolling_12_retail, null
    from rolling_12_month_spend_grouped
    union all
    select tier_name, null, frequency_spend_rolling_12_prior,
           null, null,
           null, null
    from rolling_12_month_spend_prior
    union all
    select tier_name, null, frequency_spend_rolling_12_prior,
           null, null,
           null, null
    from rolling_12_month_spend_prior_grouped_loyalty
    union all
    select tier_name, null, frequency_spend_rolling_12_prior,
           null, null,
           null, null
    from rolling_12_month_spend_prior_grouped
)

select 
    c.tier_name,
    c.sales as current_sales,
    c.transaction as current_transactions,
    current_sales/nullif(current_transactions,0) as current_basket_size,
    c.service_sales / nullif(c.service_transactions, 0) as CURRENT_SERVICE_BASKET_SIZE,
    c.retail_sales / nullif(c.retail_transactions, 0) as CURRENT_RETAIL_BASKET_SIZE,
    ur.frequency_spend_rolling_12,
    ur.frequency_spend_rolling_12_prior,
    ur.frequency_spend_rolling_12_service,
    ur.frequency_spend_rolling_12_service_prior,
    ur.frequency_spend_rolling_12_retail,
    ur.frequency_spend_rolling_12_retail_prior,
    c.unique_guest_count as current_unique_guest_count,
    c.redemption_value as current_redemption_value,
    c.birthday_discount as current_birthday_discount,
    p.sales as previous_sales,
    p.transaction as previous_transactions,
    previous_sales/nullif(previous_transactions,0) as previous_basket_size,
    p.service_sales / nullif(p.service_transactions, 0) as previous_service_basket_size,
    p.retail_sales  / nullif(p.retail_transactions, 0)  as previous_retail_basket_size,
    p.unique_guest_count as previous_unique_guest_count,
    p.redemption_value as previous_redemption_value,
    p.birthday_discount as previous_birthday_discount
from (select * from base_union_tables where period = 'CURRENT') as c
inner join (select * from base_union_tables where period = 'PREVIOUS') as p
    on c.tier_name = p.tier_name
inner join union_rolling as ur
    on ur.tier_name = c.tier_name
    