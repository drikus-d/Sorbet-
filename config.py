"""
configuration file for the clicks scorecard app
"""

import os

# config.py
# SNOWFLAKE_ACCOUNT = "ecduzcj-tkb56505"
# SNOWFLAKE_USER = "CWOLMARANS"
# SNOWFLAKE_PASSWORD = "SorbetChristo123!"
# SNOWFLAKE_ROLE = "ACCOUNTADMIN"
# SNOWFLAKE_WAREHOUSE = "compute_wh"
# SNOWFLAKE_DATABASE = "CWOLMARANS"
# SNOWFLAKE_SCHEMA = "public"

SNOWFLAKE_ACCOUNT = "ecduzcj-tkb56505"
SNOWFLAKE_USER = "svc_integration"
SNOWFLAKE_PRIVATE_KEY="""-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAoZ0oZ14CQb+9zJzuSJCq3pBJEUu/XfzSY+Fq1kNglKLFRsUy
xnQNAfkZThjO2LGmX3q31QNOgpZRMy/MzZpKmptHD1hZ42PzBT328O6lkpEhVbkP
bixXvOkz8cbYEIZZ29cb9Ts3aF6oa9ebyqRTlKjpRn3y9MWHS0jzjPW51/ZcphDX
OpG+IhPvcAMr+5a37aWLdujO3jRKaMIwXQEgqiBsJkjlnCyYi97OaWn0MxTjq5ve
Dg9sYLtISYXVxOKt7etGb/ZZlQKNJusJrYUvzhvSWi2QX3LSCDfWtuBaVRigUFv8
7Q53PQi8iEN7/g6bUe0trZTMwwB1YbX6YVxlqQIDAQABAoIBAA9vCVjev88s2xiv
W2ujYif9RjcQQWsdve9TK39hAZgMN9P/eM7+LfBUbDPat2U3CO0JFIVzioO6zHAb
ll7Dp3B+l/GJldL6/G4xmdOuLLJzqOftc4FpW2sjZ6YlH8TrOalekHFRyYOud33O
AjcezIsPuvBUDpfMxdP9GGIrpMbwfZQqAGF43tE16kuC14pjgNlL6KvAw9Ft3iVQ
pcEauVZ9qnuljkXyjcJHcfVwcYxBfh9CBrOxlMMsWVCCHTek0r/MGj1nh+s0q/cM
ru70Ed7AsG6ocxOxEXQtB1CqrSu+rLWtv06VmqEnXBzECSkfsivc6wYQo0pVtYyt
FXt0F4ECgYEAzasa2ypIEfusX6yJMCQyNcA4kGWcih4VJglDSUrJn4KGK7J6GN1l
FcMYmLR6Yl9g2E6DKNdf6a6PLEC2Bug9alD/wiGYizdf35KLrmTlC+HwGEHfgEZD
9qs1eNqFwuprKGTuk5MGh6ZBnBSrbyyaHx+RTANGFXZU07MRWLMMi4ECgYEAySoW
tfNuJtY/58VFSaK3nrNVWZwJAT8enMUwvkpNNMoJF1tpkRemPiO9kxQ4MxTA7cuk
fLeBPsvAv5fWzGb5f8b0VxowH8OuVrt3EOUeBznJuYSwWDIBbCRFiSd/yNjFTo07
vrbMfTo5SGYhcBmUNtei47yYUVFdOBWKbnU5DikCgYAPFD161iXEk8Q2m4rPacf4
ouhCxgBtK/l2+XTiecZAmKxHpeVHz2uq5cv23jye28lY8qCxLOFOW8sJfpEZ/osK
MXge/qGVi3DPDoqJNcKJVX5p+OJvIDe5bSIVg0gNW2yR4JyRW1U+OtVSoT1UgFuo
boMTpKXNywg7IUTjUPVZgQKBgCSc3HVRUQMQi6ELbojwbKsdyLL+i0UGz/OIkE6S
B2tMOktd/+DAhSlaJ+7VB0WEyXh+T/nDDGr5eqNkZ1vcghyXgXE4+vlNDDYM+KbC
jKyT//scA1yJ/WhJUb6cyc0sZvzdB7q2WpGQP0zGCd/1R9yTcrowYSirvmOux/tC
qpfBAoGAZdQ7xujePdQcO2RKkbENT8u9Sn9XxjNLDX8Gnx4mZMrBicrdU8JKYH6q
nx8B8DH6VkFxF9hdXuu18OkcqW+7oQaEJdumycbLyDChpapsfC8bE4zlTF0SncSq
cyLgqfbrlptaXRjChSQEr3BKiIYoK27uZ2DIXUDHJbKq1z8MJDA=
-----END RSA PRIVATE KEY-----"""
SNOWFLAKE_ROLE = "ACCOUNTADMIN"
SNOWFLAKE_WAREHOUSE = "compute_wh"
SNOWFLAKE_DATABASE = "CWOLMARANS"
SNOWFLAKE_SCHEMA = "public"

# File paths
STORE_PIVOTS_NO_LOYALTY_PATH = "sql/store_pivots_no_loyalty.sql"
ITEMS_WITH_LOYALTY_PATH = "sql/items_with_loyalty.sql"
LOYALTY_KPI_PATH = "sql/loyalty_kpi.sql"
OPS_KPI_PATH = "sql/ops_kpi.sql"
CLICKS_ALL_MEASURES_PATH = "sql/clicks_all_measures.sql"
CLICKS_CENTERS_PATH = "sql/clicks_centers.sql"

FILE_PATHS = {
    "TOTAL_STORE_STATS_PATH": "sql/total_store_stats.sql",
    "CORPORATE_STORE_STATS_PATH": "sql/corporate_store_stats.sql",
    "REGION_LAST_WEEK_PATH": "sql/region_last_week.sql",
    "REGION_MTD_PATH": "sql/region_mtd.sql",
    "REGION_YTD_PATH": "sql/region_ytd.sql",
    "ITEM_SERVICE_TOP_20": "sql/item_service.sql",
    "ITEM_SERVICE_TOTAL": "sql/item_service_total.sql",
    "ITEM_RETAIL_TOP_20": "sql/item_retail.sql",
    "ITEM_RETAIL_TOTAL": "sql/item_retail_total.sql",
    "TRANS_COUNT_TOTAL_PATH": "sql/trans_count_total.sql",
    "TRANS_COUNT_REGION_PATH": "sql/trans_count_region.sql",
    "BASKET_AVG_TOTAL_PATH": "sql/basket_avg_total.sql",
    "BASKET_AVG_REGION_PATH": "sql/basket_avg_region.sql",
    "DAILY_SALES_PATH": "sql/daily_sales.sql",
    "STORE_PIVOTS_NO_LOYALTY_PATH": "sql/store_pivots_no_loyalty.sql"
}

# Default settings
GROUP_BY_DEFAULT = "BRAND"
DATE_FORMAT = "%Y-%m-%d"

# Columns and other constants
BASE_VALUES = ["SERVICE_REVENUE", "RETAIL_REVENUE", "REVENUE"]
ITEM_VALUES = ["REVENUE", "QUANTITY"]
BUDGET_VALUES = ["SERVICE_BUDGET", "RETAIL_BUDGET", "TOTAL_BUDGET"]
NUMERIC_COLS = [
    "SERVICE - CURRENT",
    "RETAIL - CURRENT",
    "TOTAL - CURRENT",
    "% CURRENT CONTR",
    "STORE COUNT - CURRENT",
    "SERVICE - PREVIOUS",
    "RETAIL - PREVIOUS",
    "TOTAL - PREVIOUS",
    "STORE COUNT - PREVIOUS",
    "% PREVIOUS CONTR",
    "SERVICE BUDGET",
    "RETAIL BUDGET",
    "TOTAL - BUDGET",
    "% BUDGET CONTR",
]

NUMERIC_COLS_ITEMS = [
    "TOTAL - CURRENT",
    "TOTAL - PREVIOUS",
    "QUANTITY - CURRENT",
    "QUANTITY - PREVIOUS",
    "STORE COUNT - CURRENT",
    "STORE COUNT - PREVIOUS",
    "% CURRENT CONTR",
    "% PREVIOUS CONTR",
    "% CURRENT UNIT CONTR",
    "% PREVIOUS UNIT CONTR",
    "TOTAL CURRENT TO PREVIOUS %",
    "UNIT CURRENT TO PREVIOUS %",
    "AVERAGE REVENUE GROWTH PER STORE",
]


NUMERIC_COLS_ITEMS_GROUP = [
    "TOTAL - CURRENT",
    "TOTAL - PREVIOUS",
    "QUANTITY - CURRENT",
    "QUANTITY - PREVIOUS",
]

PERCENTAGE_COLUMNS = [
    "% BUDGET CONTR",
    "% CURRENT CONTR",
    "% PREVIOUS CONTR",
    "SERVICE CURRENT TO PREVIOUS %",
    "RETAIL CURRENT TO PREVIOUS %",
    "TOTAL CURRENT TO PREVIOUS %",
    "SERVICE TO BUDGET %",
    "RETAIL TO BUDGET %",
    "TOTAL TO BUDGET %",
]

PERCENTAGE_COLUMNS_ITEMS = [
    "% CURRENT CONTR",
    "% PREVIOUS CONTR",
    "% CURRENT UNIT CONTR",
    "% PREVIOUS UNIT CONTR",
    "TOTAL CURRENT TO PREVIOUS %",
    "UNIT CURRENT TO PREVIOUS %",
    "AVERAGE REVENUE GROWTH PER STORE",
]


COLUMN_RENAME_MAPPING = {
    "SERVICE_REVENUE_CURRENT": "SERVICE - CURRENT",
    "RETAIL_REVENUE_CURRENT": "RETAIL - CURRENT",
    "REVENUE_CURRENT": "TOTAL - CURRENT",
    "CENTER_CURRENT": "STORE COUNT - CURRENT",
    "SERVICE_REVENUE_PREVIOUS": "SERVICE - PREVIOUS",
    "RETAIL_REVENUE_PREVIOUS": "RETAIL - PREVIOUS",
    "REVENUE_PREVIOUS": "TOTAL - PREVIOUS",
    "CENTER_PREVIOUS": "STORE COUNT - PREVIOUS",
    "SERVICE_BUDGET_CURRENT": "SERVICE BUDGET",
    "RETAIL_BUDGET_CURRENT": "RETAIL BUDGET",
    "TOTAL_BUDGET_CURRENT": "TOTAL - BUDGET",
    "QUANTITY_CURRENT": "QUANTITY - CURRENT",
    "QUANTITY_PREVIOUS": "QUANTITY - PREVIOUS",
}


PERCENTAGE_CALCULATION_MAPPING = {
    "SERVICE CURRENT TO PREVIOUS %": ("SERVICE - CURRENT", "SERVICE - PREVIOUS"),
    "RETAIL CURRENT TO PREVIOUS %": ("RETAIL - CURRENT", "RETAIL - PREVIOUS"),
    "TOTAL CURRENT TO PREVIOUS %": ("TOTAL - CURRENT", "TOTAL - PREVIOUS"),
    "SERVICE TO BUDGET %": ("SERVICE - CURRENT", "SERVICE BUDGET"),
    "RETAIL TO BUDGET %": ("RETAIL - CURRENT", "RETAIL BUDGET"),
    "TOTAL TO BUDGET %": ("TOTAL - CURRENT", "TOTAL - BUDGET"),
}


PERCENTAGE_CALCULATION_MAPPING_ITEMS = {
    "TOTAL CURRENT TO PREVIOUS %": ("TOTAL - CURRENT", "TOTAL - PREVIOUS"),
    "UNIT CURRENT TO PREVIOUS %": ("QUANTITY - CURRENT", "QUANTITY - PREVIOUS"),
}


DESIRED_COLUMN_ORDER_CENTERS = [
    "SERVICE - CURRENT",
    "RETAIL - CURRENT",
    "TOTAL - CURRENT",
    "% CURRENT CONTR",
    "STORE COUNT - CURRENT",
    "SERVICE - PREVIOUS",
    "RETAIL - PREVIOUS",
    "TOTAL - PREVIOUS",
    "% PREVIOUS CONTR",
    "STORE COUNT - PREVIOUS",
    "SERVICE BUDGET",
    "RETAIL BUDGET",
    "TOTAL - BUDGET",
    "% BUDGET CONTR",
]


DESIRED_COLUMN_ORDER_ITEMS = [
    "TOTAL - CURRENT",
    "TOTAL - PREVIOUS",
    "QUANTITY - CURRENT",
    "QUANTITY - PREVIOUS",
    "STORE COUNT - CURRENT",
    "STORE COUNT - PREVIOUS",
    "% CURRENT CONTR",
    "% PREVIOUS CONTR",
    "% CURRENT UNIT CONTR",
    "% PREVIOUS UNIT CONTR",
    "TOTAL CURRENT TO PREVIOUS %",
    "UNIT CURRENT TO PREVIOUS %",
    "AVERAGE REVENUE GROWTH PER STORE",
]


formatting_schema = [
    {
        "subheader": "Group by Brand",
        "formats": {
            "BRAND": "text",
            "SERVICE REVENUE CURRENT": "number",
            "RETAIL REVENUE CURRENT": "number",
            "TOTAL REVENUE CURRENT": "number",
            "% CURRENT REV CONTR": "percentage",
            "STORE COUNT CURRENT": "number",
            "SERVICE REVENUE PREVIOUS": "number",
            "RETAIL REVENUE PREVIOUS": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "% PREVIOUS REV CONTR": "percentage",
            "STORE COUNT PREVIOUS": "number",
            "SERVICE BUDGET": "number",
            "RETAIL BUDGET": "number",
            "TOTAL BUDGET": "number",
            "% TOTAL BUDGET": "percentage",
            "SERVICES CURRENT TO PREVIOUS %": "percentage",
            "RETAIL CURRENT TO PREVIOUS %": "percentage",
            "TOTAL CURRENT TO PREVIOUS %": "percentage",
            "SERVICES REVENUE TO BUDGET %": "percentage",
            "RETAIL REVENUE TO BUDGET %": "percentage",
            "TOTAL REVENUE TO BUDGET %": "percentage",
        }
    },
    {
        "subheader": "Group by Region",
        "formats": {
            "REGION": "text",
            "SERVICE REVENUE CURRENT": "number",
            "RETAIL REVENUE CURRENT": "number",
            "TOTAL REVENUE CURRENT": "number",
            "% CURRENT REV CONTR": "percentage",
            "STORE COUNT CURRENT": "number",
            "SERVICE REVENUE PREVIOUS": "number",
            "RETAIL REVENUE PREVIOUS": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "% PREVIOUS REV CONTR": "percentage",
            "STORE COUNT PREVIOUS": "number",
            "SERVICE BUDGET": "number",
            "RETAIL BUDGET": "number",
            "TOTAL BUDGET": "number",
            "% TOTAL BUDGET": "percentage",
            "SERVICES CURRENT TO PREVIOUS %": "percentage",
            "RETAIL CURRENT TO PREVIOUS %": "percentage",
            "TOTAL CURRENT TO PREVIOUS %": "percentage",
            "SERVICES REVENUE TO BUDGET %": "percentage",
            "RETAIL REVENUE TO BUDGET %": "percentage",
            "TOTAL REVENUE TO BUDGET %": "percentage",
        }
    },
    {
        "subheader": "Group by Category",
        "formats": {
            "CATEGORY": "text",
            "SERVICE REVENUE CURRENT": "number",
            "RETAIL REVENUE CURRENT": "number",
            "TOTAL REVENUE CURRENT": "number",
            "% CURRENT REV CONTR": "percentage",
            "STORE COUNT CURRENT": "number",
            "SERVICE REVENUE PREVIOUS": "number",
            "RETAIL REVENUE PREVIOUS": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "% PREVIOUS REV CONTR": "percentage",
            "STORE COUNT PREVIOUS": "number",
            "SERVICE BUDGET": "number",
            "RETAIL BUDGET": "number",
            "TOTAL BUDGET": "number",
            "% TOTAL BUDGET": "percentage",
            "SERVICES CURRENT TO PREVIOUS %": "percentage",
            "RETAIL CURRENT TO PREVIOUS %": "percentage",
            "TOTAL CURRENT TO PREVIOUS %": "percentage",
            "SERVICES REVENUE TO BUDGET %": "percentage",
            "RETAIL REVENUE TO BUDGET %": "percentage",
            "TOTAL REVENUE TO BUDGET %": "percentage",
        }
    },
    {
        "subheader": "Top 10 Stores - Current Sales",
        "formats": {
            "CENTER": "text",
            "SERVICE REVENUE CURRENT": "number",
            "RETAIL REVENUE CURRENT": "number",
            "TOTAL REVENUE CURRENT": "number",
            "% CURRENT REV CONTR": "percentage",
            "SERVICE REVENUE PREVIOUS": "number",
            "RETAIL REVENUE PREVIOUS": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "% PREVIOUS REV CONTR": "percentage",
            "SERVICE BUDGET": "number",
            "RETAIL BUDGET": "number",
            "TOTAL BUDGET": "number",
            "% TOTAL BUDGET": "percentage",
            "SERVICES CURRENT TO PREVIOUS %": "percentage",
            "RETAIL CURRENT TO PREVIOUS %": "percentage",
            "TOTAL CURRENT TO PREVIOUS %": "percentage",
            "SERVICES REVENUE TO BUDGET %": "percentage",
            "RETAIL REVENUE TO BUDGET %": "percentage",
            "TOTAL REVENUE TO BUDGET %": "percentage",
        }
    },
    {
        "subheader": "ICU Stores - Current Sales",
        "formats": {
            "CENTER": "text",
            "SERVICE REVENUE CURRENT": "number",
            "RETAIL REVENUE CURRENT": "number",
            "TOTAL REVENUE CURRENT": "number",
            "% CURRENT REV CONTR": "percentage",
            "SERVICE REVENUE PREVIOUS": "number",
            "RETAIL REVENUE PREVIOUS": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "% PREVIOUS REV CONTR": "percentage",
            "SERVICE BUDGET": "number",
            "RETAIL BUDGET": "number",
            "TOTAL BUDGET": "number",
            "% TOTAL BUDGET": "percentage",
            "SERVICES CURRENT TO PREVIOUS %": "percentage",
            "RETAIL CURRENT TO PREVIOUS %": "percentage",
            "TOTAL CURRENT TO PREVIOUS %": "percentage",
            "SERVICES REVENUE TO BUDGET %": "percentage",
            "RETAIL REVENUE TO BUDGET %": "percentage",
            "TOTAL REVENUE TO BUDGET %": "percentage",
        }
    },
    {
        "subheader": "New Stores - Current Sales",
        "formats": {
            "CENTER": "text",
            "SERVICE REVENUE CURRENT": "number",
            "RETAIL REVENUE CURRENT": "number",
            "TOTAL REVENUE CURRENT": "number",
            "% CURRENT REV CONTR": "percentage",
            "SERVICE REVENUE PREVIOUS": "number",
            "RETAIL REVENUE PREVIOUS": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "% PREVIOUS REV CONTR": "percentage",
            "SERVICE BUDGET": "number",
            "RETAIL BUDGET": "number",
            "TOTAL BUDGET": "number",
            "% TOTAL BUDGET": "percentage",
            "SERVICES CURRENT TO PREVIOUS %": "percentage",
            "RETAIL CURRENT TO PREVIOUS %": "percentage",
            "TOTAL CURRENT TO PREVIOUS %": "percentage",
            "SERVICES REVENUE TO BUDGET %": "percentage",
            "RETAIL REVENUE TO BUDGET %": "percentage",
            "TOTAL REVENUE TO BUDGET %": "percentage",
        }
    },
    {
        "subheader": "Closed Stores - Current Sales",
        "formats": {
            "CENTER": "text",
            "SERVICE REVENUE CURRENT": "number",
            "RETAIL REVENUE CURRENT": "number",
            "TOTAL REVENUE CURRENT": "number",
            "% CURRENT REV CONTR": "percentage",
            "SERVICE REVENUE PREVIOUS": "number",
            "RETAIL REVENUE PREVIOUS": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "% PREVIOUS REV CONTR": "percentage",
            "SERVICE BUDGET": "number",
            "RETAIL BUDGET": "number",
            "TOTAL BUDGET": "number",
            "% TOTAL BUDGET": "percentage",
            "SERVICES CURRENT TO PREVIOUS %": "percentage",
            "RETAIL CURRENT TO PREVIOUS %": "percentage",
            "TOTAL CURRENT TO PREVIOUS %": "percentage",
            "SERVICES REVENUE TO BUDGET %": "percentage",
            "RETAIL REVENUE TO BUDGET %": "percentage",
            "TOTAL REVENUE TO BUDGET %": "percentage",
        }
    },
    {
        "subheader": "Top 20 Service Items",
        "formats": {
            "CATEGORY": "text",
            "TOTAL REVENUE CURRENT": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "TOTAL UNITS CURRENT": "number",
            "TOTAL UNITS PREVIOUS": "number",
            "STORE COUNT CURRENT": "number",
            "STORE COUNT PREVIOUS": "number",
            "% CURRENT REV CONTR": "percentage",
            "% PREVIOUS REV CONTR": "percentage",
            "% CURRENT UNITS CONTR": "percentage",
            "% PREVIOUS UNITS CONTR": "percentage",
            "RAND CURRENT TO PREVIOUS %": "percentage",
            "UNITS CURRENT TO PREVIOUS%": "percentage",
            "AVERAGE REVENUE GROWTH PER STORE": "percentage",
        }
    },
    {
        "subheader": "Total Lines Service",
        "formats": {
            "TOTAL REVENUE CURRENT": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "TOTAL UNITS CURRENT": "number",
            "TOTAL UNITS PREVIOUS": "number",
            "TOP 20 CURRENT REVENUE OVER TOTAL": "percentage",
            "TOP 20 PREVIOUS REVENUE OVER TOTAL": "percentage",
            "TOP 20 CURRENT UNITS OVER TOTAL": "percentage",
            "TOP 20 PREVIOUS UNITS OVER TOTAL": "percentage",
        }
    },
    {
        "subheader": "Bottom 10 Service Items",
        "formats": {
            "CATEGORY": "text",
            "TOTAL REVENUE CURRENT": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "TOTAL UNITS CURRENT": "number",
            "TOTAL UNITS PREVIOUS": "number",
            "STORE COUNT CURRENT": "number",
            "STORE COUNT PREVIOUS": "number",
            "% CURRENT REV CONTR": "percentage",
            "% PREVIOUS REV CONTR": "percentage",
            "% CURRENT UNITS CONTR": "percentage",
            "% PREVIOUS UNITS CONTR": "percentage",
            "RAND CURRENT TO PREVIOUS %": "percentage",
            "UNITS CURRENT TO PREVIOUS%": "percentage",
            "AVERAGE REVENUE GROWTH PER STORE": "percentage",
        }
    },
    {
        "subheader": "Top 20 Retail Items",
        "formats": {
            "CATEGORY": "text",
            "TOTAL REVENUE CURRENT": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "TOTAL UNITS CURRENT": "number",
            "TOTAL UNITS PREVIOUS": "number",
            "STORE COUNT CURRENT": "number",
            "STORE COUNT PREVIOUS": "number",
            "% CURRENT REV CONTR": "percentage",
            "% PREVIOUS REV CONTR": "percentage",
            "% CURRENT UNITS CONTR": "percentage",
            "% PREVIOUS UNITS CONTR": "percentage",
            "RAND CURRENT TO PREVIOUS %": "percentage",
            "UNITS CURRENT TO PREVIOUS%": "percentage",
            "AVERAGE REVENUE GROWTH PER STORE": "percentage",
        }
    },
    {
        "subheader": "Total Lines Retail",
        "formats": {
            "TOTAL REVENUE CURRENT": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "TOTAL UNITS CURRENT": "number",
            "TOTAL UNITS PREVIOUS": "number",
            "TOP 20 CURRENT REVENUE OVER TOTAL": "percentage",
            "TOP 20 PREVIOUS REVENUE OVER TOTAL": "percentage",
            "TOP 20 CURRENT UNITS OVER TOTAL": "percentage",
            "TOP 20 PREVIOUS UNITS OVER TOTAL": "percentage",
        }
    },
    {
        "subheader": "Bottom 10 Retail Items",
        "formats": {
            "CATEGORY": "text",
            "TOTAL REVENUE CURRENT": "number",
            "TOTAL REVENUE PREVIOUS": "number",
            "TOTAL UNITS CURRENT": "number",
            "TOTAL UNITS PREVIOUS": "number",
            "STORE COUNT CURRENT": "number",
            "STORE COUNT PREVIOUS": "number",
            "% CURRENT REV CONTR": "percentage",
            "% PREVIOUS REV CONTR": "percentage",
            "% CURRENT UNITS CONTR": "percentage",
            "% PREVIOUS UNITS CONTR": "percentage",
            "RAND CURRENT TO PREVIOUS %": "percentage",
            "UNITS CURRENT TO PREVIOUS%": "percentage",
            "AVERAGE REVENUE GROWTH PER STORE": "percentage",
        }
    }
]


rename_dictionary_loyalty_kpi = {
    'TIER_NAME': 'Tier Name',
    'SALES-CURRENT_SALES': 'Sales - Current',
    'SALES-SALES_GROWTH': 'Sales - Growth period on period',
    'SALES-CURRENT_SALES_CONTRIBUTION': 'Sales - Contribution to total',
    'TRANSACTIONS-CURRENT_TRANSACTIONS': 'Transactions - Current',
    'TRANSACTIONS-TRANSACTION_GROWTH': 'Transactions - Growth period on period',
    'TRANSACTIONS-CURRENT_TRANSACTIONS_CONTRIBUTION': 'Transactions - Contribution to total',
    'GUEST_COUNT-CURRENT_UNIQUE_GUEST_COUNT': 'Guest Count - Current',
    'GUEST_COUNT-GUEST_COUNT_GROWTH': 'Guest Count - Growth period on period',
    'GUEST_COUNT-CURRENT_UNIQUE_GUEST_COUNT_CONTRIBUTION': 'Guest Count - Contribution to total',
    'BASKET_SIZE-CURRENT_BASKET_SIZE': 'Basket Size - Current',
    'BASKET_SIZE-BASKET_SIZE_GROWTH': 'Basket Size - Growth period on period',
    'FREQUENCY_SPEND_ROLLING_12-FREQUENCY_SPEND_ROLLING_12': 'Frequency Spend (Rolling 12 months) - Current',
    'RETAIL_FREQ_OF_SPEND_ROLL_12_MONTHS-FREQUENCY_SPEND_ROLLING_12_RETAIL': 'Retail Freq. of Spend (Roll 12 months) - Current',
    'SERVICE_FREQ_OF_SPEND_ROLL_12_MONTHS-FREQUENCY_SPEND_ROLLING_12_SERVICE': 'Service Freq. of Spend (Roll 12 months) - Current',
    'REDEMPTION_VALUE-CURRENT_REDEMPTION_VALUE': 'Redemption Value - Current',
    'REDEMPTION_VALUE-REDEMPTION_VALUE_GROWTH': 'Redemption Value - Growth period on period',
    'REDEMPTION_VALUE-CURRENT_REDEMPTION_VALUE_CONTRIBUTION': 'Redemption Value - Contribution to total',
    'LOYALTY_COST_%-LOYALTY_COST_PERCENT_CURRENT': 'Loyalty Cost % of Sales - Current',
    'LOYALTY_COST_%-LOYALTY_COST_PERCENT_GROWTH_RATE': 'Loyalty Cost % of Sales- Growth period on period',
    'BIRTHDAY_DISCOUNT-CURRENT_BIRTHDAY_DISCOUNT': 'Birthday discount amount - Current',
    'BIRTHDAY_DISCOUNT-BIRTHDAY_DISCOUNT_GROWTH': 'Birthday discount amount - Growth period on period',
    'BIRTHDAY_DISCOUNT-CURRENT_BIRTHDAY_DISCOUNT_CONTRIBUTION': 'Birthday discount amount - Contribution to total',
    'BIRTHDAY_DISCOUNT_%-BIRTHDAY_DISCOUNT_PERCENT_CURRENT': 'Birthday discount cost % of sales - Current',
    'BIRTHDAY_DISCOUNT_%-BIRTHDAY_DISCOUNT_PERCENT_GROWTH_RATE': 'Birthday discount cost % of sales - Growth period on period'
}


OPS_METRIC_FORMAT_MAPPING = {
    'Avg Total Sales per Store': '#,##0',  # Numbers with thousand separator, no decimals
    'Total Sales Growth': '0.0%',  # Percentage with 1 decimal
    'Average Trading Density': '#,##0',
    'Avg Service Sales per Store': '#,##0',
    'Total Service Sales Growth': '0.0%',
    'Services to Total Ratio (Current)': '0.0%',
    'Services to Total Ratio (Previous)': '0.0%',
    'Avg Service Units Sold': '#,##0',
    'Avg Retail Sales per Store': '#,##0',
    'Total Retail Sales Growth': '0.0%',
    'Retail to Total Ratio (Current)': '0.0%',
    'Retail to Total Ratio (Previous)': '0.0%',
    'Avg Retail Units Sold': '#,##0',
    'Total Transaction Count': '#,##0',
    'Avg Transactions per Store': '#,##0',
    'Transactions Growth': '0.0%',
    'Average Basket Size': '#,##0.00',  # Numbers with 2 decimals
    'Basket Size Growth': '0.0%',
    'Service Basket Size': '#,##0.00',
    'Service Basket Size Growth': '0.0%',
    'Retail Basket Size': '#,##0.00',
    'Retail Basket Size Growth': '0.0%',
    'Unique Guest Count': '#,##0',
    'Unique Guest Growth': '0.0%',
    'Rolling Unique Guests': '#,##0',
    'New Guest Count': '#,##0',
    'New Guest Growth': '0.0%',
    'New Guests per Store': '#,##0',
    'Avg Guest Frequency Spend': '#,##0.00',
    'Frequency Spend Growth': '0.0%',
    'Frequency Spend (Rolling 12)': '#,##0.00',
    'Birthday discount cost % of sales': '0.0%',  # Add birthday discount percentage formatting
    'Birthday discount cost % of sales - Current': '0.0%',  # Add birthday discount current percentage formatting
    'Birthday discount cost % of sales - Growth period on period': '0.0%',  # Add birthday discount growth percentage formatting
    'Loyalty Cost % of Sales': '0.0%',  # Add loyalty cost percentage formatting
    'Loyalty Cost % of Sales - Current': '0.0%',  # Add loyalty cost current percentage formatting
    'Loyalty Cost % of Sales- Growth period on period': '0.0%',  # Add loyalty cost growth percentage formatting
    'Last Year %': '0.0%',  # Add basket size percentage formatting
    'Retail Last Year %': '0.0%',  # Add retail basket size percentage formatting
    'Service Last Year %': '0.0%'  # Add service basket size percentage formatting
}

CLICKS_LOYALTY_FORMAT_MAPPING = {
    "Clicks loyalty sales": '#,##0', 
    "Non clicks sales": '#,##0',
    "Total sales": '#,##0',
    "Clicks loyalty sales over total": '0.0%',
    "Clicks loyalty transactions count": '#,##0',
    "Non clicks transactions count": '#,##0',
    "Total transactions count": '#,##0',
    "Clicks loyalty transactions over total": '0.0%',
    "Clicks loyalty basket size": '#,##0.00',
    "Non Clicks basket size": '#,##0',
    "Basket size total": '#,##0',
    "Clicks loyalty basket size over total": '0.0%',
    "Clicks loyalty new guest count": '#,##0',
    "New guest count": '#,##0',
    "New clicks loyalty guest over new guests": '0.0%',
    "Unique guest count": '#,##0',
    "Clicks loyalty new guests over total unique guests": '0.0%',
    "All Transactions Frequency of Spend (Rolling 12 months)": '#,##0.00',
    "Clicks Clubcard Frequency of Spend (Rolling 12 months)": '#,##0.00',
    "All Transactions Frequency of Spend (Rolling 12 months) - Service": '#,##0.00',
    "All Transactions Frequency of Spend (Rolling 12 months) - Retail": '#,##0.00',
    "Clicks Clubcard Frequency of Spend (Rolling 12 months) - Service": '#,##0.00',
    "Clicks Clubcard Frequency of Spend (Rolling 12 months) - Retail": '#,##0.00'
}
