    with base_lines as (
    select
        iff(
            r.payment_date >= to_date('{start_date}')
            and r.payment_date <= to_date('{end_date}'),
            'CURRENT',
            'PREVIOUS'
        ) as period,
        c.{group},
        count(distinct c.reporting_center_name) as store_count,
        sum(r.revenue) as revenue,
        sum(iff(is_service = true, r.revenue, 0)) as service_revenue,
        sum(iff(is_retail = true, r.revenue, 0)) as retail_revenue,
        sum(r.quantity) as units_sold,
        sum(iff(is_service = true, r.quantity, 0)) as service_units_sold,
        sum(iff(is_retail = true, r.quantity, 0)) as retail_units_sold,
        count(distinct r.invoice_no) as total_transaction_count,
        count(distinct(iff(is_service = true, r.invoice_no, null))) as service_transaction_count,
        count(distinct(iff(is_retail = true, r.invoice_no, null))) as retail_transaction_count,
        count(distinct r.guest_code) as unique_guest_count,
        count(distinct(iff(r.is_first_visit = true, r.guest_code, null))) as new_guest_count
    from marts.finance.fact_revenue as r
    left join marts.common.dim_center as c
        on c.center_id = r.center_id
    left join marts.finance.dim_tier as t
        on t.tier_id = r.tier_id
    where
        (
            (payment_date >= to_date('{start_date}') and payment_date <= to_date('{end_date}'))
            or
            (payment_date >= dateadd(year, -1, to_date('{start_date}'))
            and payment_date <= dateadd(year, -1, to_date('{end_date}')))
        )
        and c.is_reporting_branch = true
        and is_loyalty_payment = false
    group by all
),
total_base as (
select
    iff(
        r.payment_date >= to_date('{start_date}')
        and r.payment_date <= to_date('{end_date}'),
        'CURRENT','PREVIOUS') as period,
        'TOTAL',
        count(distinct c.reporting_center_name) as total_store_count,
        sum(r.revenue) as revenue_total,
        sum(iff(is_service = true, r.revenue, 0)) as total_service_revenue,
        sum(iff(is_retail = true, r.revenue, 0)) as total_retail_revenue,
        sum(r.quantity) as units_sold,
        sum(iff(is_service = true, r.quantity, 0)) as total_service_units_sold,
        sum(iff(is_retail = true, r.quantity, 0)) as total_retail_units_sold,
        count(distinct r.invoice_no) as total_transaction_count,
        count(distinct(iff(is_service = true, r.invoice_no, null))) as service_transaction_count,
        count(distinct(iff(is_retail = true, r.invoice_no, null))) as retail_transaction_count,
        count(distinct r.guest_code) as total_unique_guest_count,
        count(distinct(iff(r.is_first_visit = true, r.guest_code, null))) as total_new_guest_count
    from marts.finance.fact_revenue as r
    left join marts.common.dim_center as c
        on c.center_id = r.center_id
    left join marts.finance.dim_tier as t
        on t.tier_id = r.tier_id
       where
        (
            (payment_date >= to_date('{start_date}') and payment_date <= to_date('{end_date}'))
            or
            (payment_date >= dateadd(year, -1, to_date('{start_date}'))
            and payment_date <= dateadd(year, -1, to_date('{end_date}')))
        )
        and c.is_reporting_branch = true
        and is_loyalty_payment = false
    group by all
),
base as (
select * from base_lines
union all
select * from total_base
),
unique_centers as (
   select
        {group},
        center_code,
        reporting_center_name as center,
        store_size 
    from marts.common.dim_center
    where coalesce(opening_date, '1900-01-01') <= to_date('{end_date}')
    and is_reporting_branch = true and {group} is not null
    group by all
),
-- Need to relook at this calc in power bi, its not looking at current stores
average_store_size as (
    select 
        {group},
        avg(store_size) as avg_store_size
    from unique_centers
group by all
union all
select 'TOTAL', avg(store_size) as avg_store_size
from unique_centers
),
current_main as (
    select 
        b.{group},
        b.revenue,
        --TOTAL SALES
        b.service_revenue,
        b.retail_revenue,
        b.revenue/b.store_count as avg_total_sales_per_store,
        b.revenue/ast.avg_store_size/store_count as average_trading_density,
        --SERVICE SALES
        b.service_revenue/b.store_count as avg_service_sales_per_store,
        b.service_units_sold/b.store_count as avg_service_units_sold,
        --RETAIL  SALES
        b.retail_revenue/b.store_count as avg_retail_sales_per_store,
        b.retail_units_sold/b.store_count as avg_retail_units_sold,
        --TRANSACTIONS AND BASKET SECTION
        b.total_transaction_count,
        b.total_transaction_count/b.store_count as avg_total_transactions_per_store,
        avg_total_sales_per_store/avg_total_transactions_per_store as total_basket_size_average,
        b.service_revenue/b.service_transaction_count as service_basket_size,
        b.retail_revenue/b.retail_transaction_count as retail_basket_size,
        -- OTHER KPIs
        b.unique_guest_count,
        b.new_guest_count,
        trunc(b.new_guest_count/b.store_count, 0) as new_guest_per_store,
        b.total_transaction_count/b.unique_guest_count as avg_guest_frequency_spend
    from base as b 
    inner join average_store_size as ast 
        on b.{group} = ast.{group}
    where period = 'CURRENT'
    group by all order by 1
),
previous_main as (
    select 
        {group},
        revenue as revenue_previous,
        revenue/store_count as avg_total_sales_per_store_previous,
        service_revenue as service_revenue_previous,
        service_revenue/store_count as avg_service_sales_per_store_previous,
        retail_revenue as retail_revenue_previous,
        retail_revenue/store_count as avg_retail_sales_per_store_previous,
        total_transaction_count as total_transaction_count_previous,
        total_transaction_count/store_count as avg_total_transactions_per_store_previous,
        service_transaction_count as service_transaction_count_previous,
        avg_total_sales_per_store_previous/avg_total_transactions_per_store_previous as total_basket_size_average_previous,
        service_revenue_previous/service_transaction_count as service_basket_size_previous,
        retail_revenue/retail_transaction_count as retail_basket_size_previous,
        -- OTHER KPIs
        unique_guest_count as unique_guest_count_previous,
        new_guest_count as new_guest_count_previous,
        total_transaction_count/unique_guest_count as avg_guest_frequency_spend_previous
    from base
    where period = 'PREVIOUS'
),
rolling_12_month_spend as (
    select
        c.{group},
        count(distinct r.guest_code) as rolling_unique_guest,
        count(distinct r.invoice_no) as rolling_transactions,
        rolling_transactions/ NULLIF(rolling_unique_guest, 0) as frequency_spend_rolling_12,       
    from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c
            on c.center_id = r.center_id
    where   
        payment_date > dateadd(year, -1, to_date('{end_date}')) and payment_date <= to_date('{end_date}')
         and c.is_reporting_branch = true
         and r.is_loyalty_payment = false
        group by all
    union all
    select
        'TOTAL',
        count(distinct r.guest_code) as rolling_unique_guest,
        count(distinct r.invoice_no) as rolling_transactions,
        rolling_transactions/ NULLIF(rolling_unique_guest, 0) as frequency_spend_rolling_12,       
    from
        marts.finance.fact_revenue as r
        left join marts.common.dim_center as c
            on c.center_id = r.center_id
    where   
        payment_date > dateadd(year, -1, to_date('{end_date}')) and payment_date <= to_date('{end_date}')
         and c.is_reporting_branch = true
         and r.is_loyalty_payment = false
        group by all
),
combined_main as (
    select 
        --TOTAL SALES SECTION
        cm.{group},
        cm.avg_total_sales_per_store,
        ((cm.revenue/nullif(pm.revenue_previous, 0)) - 1) as total_sales_growth,
        cm.average_trading_density,
        --SERVICE SALES SECTION
        cm.avg_service_sales_per_store,
        ((cm.service_revenue/nullif(pm.service_revenue_previous, 0)) - 1) as total_service_sales_growth,
        (cm.avg_service_sales_per_store/cm.avg_total_sales_per_store) as avg_services_to_avg_total_current,
        pm.avg_service_sales_per_store_previous/pm.avg_total_sales_per_store_previous as avg_services_to_avg_total_previous,
        cm.avg_service_units_sold,
        --RETAIL SALES SECTION
        cm.avg_retail_sales_per_store,
        ((cm.retail_revenue/nullif(pm.retail_revenue_previous, 0)) - 1) as total_retail_sales_growth,
        (cm.avg_retail_sales_per_store/cm.avg_total_sales_per_store) as avg_retail_to_avg_total_current,
        pm.avg_retail_sales_per_store_previous/pm.avg_total_sales_per_store_previous as avg_retail_to_avg_total_previous,
        avg_retail_units_sold,
        --TRANSACTIONS AND BASKET SIZE
        cm.total_transaction_count,
        pm.total_transaction_count_previous,
        cm.avg_total_transactions_per_store,
        ((cm.total_transaction_count/total_transaction_count_previous) - 1) as transactions_growth,
        total_basket_size_average,
        ((total_basket_size_average/total_basket_size_average_previous) - 1) as average_basket_size_growth,
        cm.service_basket_size,
        ((cm.service_basket_size/pm.service_basket_size_previous) -1) as service_basket_size_growth,
        cm.retail_basket_size,
        ((cm.retail_basket_size/pm.retail_basket_size_previous) -1) as retail_basket_size_growth,
        -- OTHER KPIs
        cm.unique_guest_count,
        ((cm.unique_guest_count/pm.unique_guest_count_previous) - 1) as unique_guest_growth,
        ---guest rollinf 12 to add
        rs.rolling_unique_guest,
        cm.new_guest_count,
        (cm.new_guest_count/cm.unique_guest_count) as new_guest_growth,
        cm.new_guest_per_store,
        cm.avg_guest_frequency_spend,
        ((cm.avg_guest_frequency_spend/pm.avg_guest_frequency_spend_previous) - 1) as avg_frequency_spend_growth,
        rs.frequency_spend_rolling_12
    from current_main as cm 
    left join previous_main as pm
        on cm.{group} = pm.{group}
    left join rolling_12_month_spend as rs
        on rs.{group} = pm.{group}
)
select * from combined_main
