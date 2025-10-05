"""
This module contains functions for creating and
manipulating dataframes for the loyalty KPI section
in Streamlit.
"""
import pandas as pd
import config
import utils as ut
import streamlit as st


def rename_columns(df, sections: dict):
    """
    This function is used to rename the columns of the dataframe.
    """
    # Step 1: Create a new list of columns
    new_columns = ["TIER_NAME"]  # Start with 'TIER_NAME'

    for section, columns in sections.items():
        # Step 3: Rename each column in the section by prefixing with the section name
        for col in columns:
            new_columns.append(f"{section}-{col}")

    if len(new_columns) != len(df.columns):
        raise ValueError(
            f"Length mismatch: DataFrame has {len(df.columns)} columns, "
            f"but {len(new_columns)} new columns provided."
        )

    # Step 5: Rename the DataFrame's columns
    df.columns = new_columns

    return df


def loyalty_kpi_pivot(session, start_date: str, end_date: str):
    """
    This function is used to get the loyalty KPI pivot.
    """
    loyalty_kpi_query = ut.read_sql_query(config.LOYALTY_KPI_PATH)
    # Format the query with start and end dates
    modified_query = loyalty_kpi_query.format(start_date=start_date, end_date=end_date)

    # Load the data from the session
    loyalty_kpi_df = ut.load_data(session, modified_query)

    return loyalty_kpi_df


def add_loyalty_cost_and_birthday_discount_percent(df):
    """
    This function is used to add the loyalty cost % and birthday discount % to the dataframe.
    """
    # Simple approach: Calculate percentages as decimals (0.015 for 1.5%)
    df["LOYALTY_COST_PERCENT_CURRENT"] = (
        df["CURRENT_REDEMPTION_VALUE"] / df["CURRENT_SALES"]
    )
    df["LOYALTY_COST_PERCENT_PREVIOUS"] = (
        df["PREVIOUS_REDEMPTION_VALUE"] / df["PREVIOUS_SALES"]
    )
    
    df["BIRTHDAY_DISCOUNT_PERCENT_CURRENT"] = (
        df["CURRENT_BIRTHDAY_DISCOUNT"] / df["CURRENT_SALES"]
    )
    df["BIRTHDAY_DISCOUNT_PERCENT_PREVIOUS"] = (
        df["PREVIOUS_BIRTHDAY_DISCOUNT"] / df["PREVIOUS_SALES"]
    )
    
    # Handle division by zero
    df["LOYALTY_COST_PERCENT_CURRENT"] = df["LOYALTY_COST_PERCENT_CURRENT"].fillna(0)
    df["LOYALTY_COST_PERCENT_PREVIOUS"] = df["LOYALTY_COST_PERCENT_PREVIOUS"].fillna(0)
    df["BIRTHDAY_DISCOUNT_PERCENT_CURRENT"] = df["BIRTHDAY_DISCOUNT_PERCENT_CURRENT"].fillna(0)
    df["BIRTHDAY_DISCOUNT_PERCENT_PREVIOUS"] = df["BIRTHDAY_DISCOUNT_PERCENT_PREVIOUS"].fillna(0)
    
    return df


def loyalty_get_growth_rate(df, growth_col, current_col, previous_col):
    """
    This function is used to get the growth rate of a column.
    """
    # Replace zeros in previous_col with NaN to avoid division by zero
    df[previous_col] = df[previous_col].replace({0: pd.NA})

    df[growth_col] = (df[current_col] / df[previous_col]) - 1
    return df


def loyalty_contribution_to_total(df, col, new_col_name):
    """
    This function is used to get the contribution of a record
    to its total.
    """
    # Calculate the column total
    total = df[df["TIER_NAME"] == "Total"][col].sum()

    # Calculate the percentage of each row to the column total
    df[new_col_name] = df[col] / total
    return df


def loyalty_select_columns(df):
    """
    This function is used to select the required columns.
    """
    selected_columns = [
        "TIER_NAME",
        "CURRENT_SALES",
        "SALES_GROWTH",
        "CURRENT_SALES_CONTRIBUTION",
        "CURRENT_TRANSACTIONS",
        "TRANSACTION_GROWTH",
        "CURRENT_TRANSACTIONS_CONTRIBUTION",
        "CURRENT_UNIQUE_GUEST_COUNT",
        "GUEST_COUNT_GROWTH",
        "CURRENT_UNIQUE_GUEST_COUNT_CONTRIBUTION",
        "CURRENT_BASKET_SIZE",
        "BASKET_SIZE_GROWTH",
        "FREQUENCY_SPEND_ROLLING_12",
        "FREQUENCY_SPEND_ROLLING_12_SERVICE",
        "FREQUENCY_SPEND_ROLLING_12_RETAIL",
        "CURRENT_REDEMPTION_VALUE",
        "REDEMPTION_VALUE_GROWTH",
        "CURRENT_REDEMPTION_VALUE_CONTRIBUTION",
        "LOYALTY_COST_PERCENT_CURRENT",
        "LOYALTY_COST_PERCENT_PREVIOUS",
        "LOYALTY_COST_PERCENT_GROWTH_RATE",
        "CURRENT_BIRTHDAY_DISCOUNT",
        "BIRTHDAY_DISCOUNT_GROWTH",
        "CURRENT_BIRTHDAY_DISCOUNT_CONTRIBUTION",
        "BIRTHDAY_DISCOUNT_PERCENT_CURRENT",
        "BIRTHDAY_DISCOUNT_PERCENT_PREVIOUS",
        "BIRTHDAY_DISCOUNT_PERCENT_GROWTH_RATE",
    ]
    df = df[selected_columns]
    return df


def loyalty_format_columns(df):
    """
    This function is used to format the columns of the dataframe.
    """
    # Numeric columns to convert to numeric data types
    numeric_cols = [
        "CURRENT_SALES",
        "CURRENT_TRANSACTIONS",
        "CURRENT_UNIQUE_GUEST_COUNT",
        "CURRENT_BASKET_SIZE",
        "FREQUENCY_SPEND_ROLLING_12",
        "CURRENT_REDEMPTION_VALUE",
        "CURRENT_BIRTHDAY_DISCOUNT",
        "LOYALTY_COST_PERCENT_CURRENT",
        "LOYALTY_COST_PERCENT_PREVIOUS",
        "BIRTHDAY_DISCOUNT_PERCENT_CURRENT",
        "BIRTHDAY_DISCOUNT_PERCENT_PREVIOUS",
    ]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # Percentage columns to convert to numeric data types
    percentage_cols = [
        "SALES_GROWTH",
        "TRANSACTION_GROWTH",
        "GUEST_COUNT_GROWTH",
        "BASKET_SIZE_GROWTH",
        "REDEMPTION_VALUE_GROWTH",
        "BIRTHDAY_DISCOUNT_GROWTH",
        "LOYALTY_COST_PERCENT_GROWTH_RATE",
        "BIRTHDAY_DISCOUNT_PERCENT_GROWTH_RATE",
        "CURRENT_SALES_CONTRIBUTION",
        "CURRENT_TRANSACTIONS_CONTRIBUTION",
        "CURRENT_UNIQUE_GUEST_COUNT_CONTRIBUTION",
        "CURRENT_REDEMPTION_VALUE_CONTRIBUTION",
        "CURRENT_BIRTHDAY_DISCOUNT_CONTRIBUTION",
        "LOYALTY_COST_PERCENT_CURRENT",
        "BIRTHDAY_DISCOUNT_PERCENT_CURRENT",
    ]
    df[percentage_cols] = df[percentage_cols].apply(pd.to_numeric, errors="coerce")

    # Ensure percentages are fractions between -1 and 1
    #df[percentage_cols] = df[percentage_cols].applymap(lambda x: x / 100 if abs(x) >= 1 else x)

    return df


def transpose_order_pivot(df):
    """
    This function is used to transpose the dataframe.
    """
    df = df.T
    # Set the first row as the new column names
    df.columns = df.iloc[0]
    # Remove the first row
    df = df[1:]
    return df.reset_index()


def melt_and_pivot(df):
    """
    This function is used to melt and pivot the dataframe.
    """
    df.columns.name = None
    df_melted = df.melt(
        id_vars=["index"],
        var_name="TIER_NAME",
        value_name="Value",
    )

    # Split 'index' into 'Metric' and 'Type'
    df_melted[["Metric", "Type"]] = df_melted["index"].str.split("-", n=1, expand=True)
    df_melted["Metric"] = df_melted["Metric"].str.strip()
    df_melted["Type"] = df_melted["Type"].str.strip()

    # Pivot the DataFrame
    df_pivot = df_melted.pivot_table(
        values="Value",
        index=["Metric", "Type"],
        columns=["TIER_NAME"],
        aggfunc="first",
    )

    df_pivot = df_pivot.reset_index()
    return df_pivot


def format_loyalty_kpi_display(df):
    """
    This function formats the loyalty KPI DataFrame for display:
    - Formats growth percentages as percentages (multiplies by 100 and adds %)
    - Formats numeric values with thousand separators
    - Stores raw numeric values for Excel formatting
    """
    # Create a copy to avoid modifying the original
    formatted_df = df.copy()
    
    # Define the columns that contain growth percentages
    growth_columns = ['Green', 'Blue', 'Silver', 'Gold', 'Total Loyalty', 'Non-loyalty', 'Total']
    
    # Convert all columns to object type first to avoid dtype warnings
    for col in growth_columns:
        if col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].astype(object)
    
    # Format growth percentages for "Growth period on period" rows
    growth_mask = formatted_df['Type'] == 'Growth period on period'
    
    for col in growth_columns:
        if col in formatted_df.columns:
            # Convert to numeric first for calculations
            numeric_values = pd.to_numeric(formatted_df[col], errors='coerce')
            
            # Store raw decimal values for Excel formatting (before converting to percentages)
            formatted_df[f'{col}_RAW'] = numeric_values
            
            # Format growth percentages (multiply by 100 and add %)
            formatted_df.loc[growth_mask, col] = numeric_values.loc[growth_mask].apply(
                lambda x: f"{x*100:.1f}%" if pd.notna(x) and x != 0 else "0.0%"
            )
            
            # Format numeric values for "Current" rows (with thousand separators)
            current_mask = formatted_df['Type'] == 'Current'
            
            # Format numeric values for "Current" rows
            # Check if this row is a frequency metric (contains 'frequency' or 'freq' - case insensitive)
            frequency_mask = formatted_df['Metric'].str.contains('freq', case=False, na=False)
            current_frequency_mask = current_mask & frequency_mask
            
            if current_frequency_mask.any():
                # DEBUG: Print raw frequency values
                print(f"DEBUG FREQUENCY - Column: {col}")
                print(f"DEBUG FREQUENCY - Raw values: {numeric_values.loc[current_frequency_mask].tolist()}")
                print(f"DEBUG FREQUENCY - Data types: {numeric_values.loc[current_frequency_mask].dtype}")
                
                # For frequency metrics, format with 1 decimal place
                formatted_df.loc[current_frequency_mask, col] = numeric_values.loc[current_frequency_mask].apply(
                    lambda x: f"{float(x):.1f}" if pd.notna(x) and x != 0 else "0.0"
                )
            
            # Check if this row is a percentage metric (loyalty cost % or birthday discount %)
            percentage_mask = formatted_df['Metric'].str.contains('%', case=False, na=False)
            current_percentage_mask = current_mask & percentage_mask
            
            if current_percentage_mask.any():
                # For percentage metrics, format as percentages for Streamlit display
                formatted_df.loc[current_percentage_mask, col] = numeric_values.loc[current_percentage_mask].apply(
                    lambda x: f"{float(x)*100:.1f}%" if pd.notna(x) and x != 0 else "0.0%"
                )
            
            # Format non-frequency, non-percentage metrics with thousand separators and no decimals
            current_non_frequency_non_percentage_mask = current_mask & ~frequency_mask & ~percentage_mask
            formatted_df.loc[current_non_frequency_non_percentage_mask, col] = numeric_values.loc[current_non_frequency_non_percentage_mask].apply(
                lambda x: f"{x:,.0f}" if pd.notna(x) and x != 0 else "0"
            )
            
            # Format contribution percentages for "Contribution to total" rows
            contribution_mask = formatted_df['Type'] == 'Contribution to total'
            formatted_df.loc[contribution_mask, col] = numeric_values.loc[contribution_mask].apply(
                lambda x: f"{x*100:.1f}%" if pd.notna(x) and x != 0 else "0.0%"
            )
    
    return formatted_df


def loyalty_kpi_main(session, start_date: str, end_date: str):
    """
    This function is used to get the loyalty KPI main,
    that will be displayed in the Streamlit app.
    """
    df = loyalty_kpi_pivot(session, start_date, end_date)
    df = add_loyalty_cost_and_birthday_discount_percent(df)

    # Get the growth rate tuple
    growth_rate_cols = [
        ("SALES_GROWTH", "CURRENT_SALES", "PREVIOUS_SALES"),
        ("TRANSACTION_GROWTH", "CURRENT_TRANSACTIONS", "PREVIOUS_TRANSACTIONS"),
        ("GUEST_COUNT_GROWTH", "CURRENT_UNIQUE_GUEST_COUNT", "PREVIOUS_UNIQUE_GUEST_COUNT"),
        ("BASKET_SIZE_GROWTH", "CURRENT_BASKET_SIZE", "PREVIOUS_BASKET_SIZE"),
        ("REDEMPTION_VALUE_GROWTH", "CURRENT_REDEMPTION_VALUE", "PREVIOUS_REDEMPTION_VALUE"),
        ("LOYALTY_COST_PERCENT_GROWTH_RATE", "LOYALTY_COST_PERCENT_CURRENT", "LOYALTY_COST_PERCENT_PREVIOUS"),
        ("BIRTHDAY_DISCOUNT_GROWTH", "CURRENT_BIRTHDAY_DISCOUNT", "PREVIOUS_BIRTHDAY_DISCOUNT"),
        ("BIRTHDAY_DISCOUNT_PERCENT_GROWTH_RATE", "BIRTHDAY_DISCOUNT_PERCENT_CURRENT", "BIRTHDAY_DISCOUNT_PERCENT_PREVIOUS"),
    ]

    for growth_rate_col in growth_rate_cols:
        df = loyalty_get_growth_rate(
            df, growth_rate_col[0], growth_rate_col[1], growth_rate_col[2]
        )

    # Contribution to total columns
    contribution_to_total_cols = [
        ("CURRENT_SALES", "CURRENT_SALES_CONTRIBUTION"),
        ("CURRENT_TRANSACTIONS", "CURRENT_TRANSACTIONS_CONTRIBUTION"),
        ("CURRENT_UNIQUE_GUEST_COUNT", "CURRENT_UNIQUE_GUEST_COUNT_CONTRIBUTION"),
        ("CURRENT_REDEMPTION_VALUE", "CURRENT_REDEMPTION_VALUE_CONTRIBUTION"),
        ("CURRENT_BIRTHDAY_DISCOUNT", "CURRENT_BIRTHDAY_DISCOUNT_CONTRIBUTION"),
    ]
    for contribution_to_total_col in contribution_to_total_cols:
        df = loyalty_contribution_to_total(
            df, contribution_to_total_col[0], contribution_to_total_col[1]
        )

    df = loyalty_select_columns(df).copy()
    df = loyalty_format_columns(df)

    sections = {
        "SALES": ["CURRENT_SALES", "SALES_GROWTH", "CURRENT_SALES_CONTRIBUTION"],
        "TRANSACTIONS": [
            "CURRENT_TRANSACTIONS",
            "TRANSACTION_GROWTH",
            "CURRENT_TRANSACTIONS_CONTRIBUTION",
        ],
        "GUEST_COUNT": [
            "CURRENT_UNIQUE_GUEST_COUNT",
            "GUEST_COUNT_GROWTH",
            "CURRENT_UNIQUE_GUEST_COUNT_CONTRIBUTION",
        ],
        "BASKET_SIZE": ["CURRENT_BASKET_SIZE", "BASKET_SIZE_GROWTH"],
        "FREQUENCY_SPEND_ROLLING_12": ["FREQUENCY_SPEND_ROLLING_12"],
        "RETAIL_FREQ_OF_SPEND_ROLL_12_MONTHS": ["FREQUENCY_SPEND_ROLLING_12_RETAIL"],
        "SERVICE_FREQ_OF_SPEND_ROLL_12_MONTHS": ["FREQUENCY_SPEND_ROLLING_12_SERVICE"],
        "REDEMPTION_VALUE": [
            "CURRENT_REDEMPTION_VALUE",
            "REDEMPTION_VALUE_GROWTH",
            "CURRENT_REDEMPTION_VALUE_CONTRIBUTION",
        ],
        "LOYALTY_COST_%": [
            "LOYALTY_COST_PERCENT_CURRENT",
            "LOYALTY_COST_PERCENT_PREVIOUS",
            "LOYALTY_COST_PERCENT_GROWTH_RATE",
        ],
        "BIRTHDAY_DISCOUNT": [
            "CURRENT_BIRTHDAY_DISCOUNT",
            "BIRTHDAY_DISCOUNT_GROWTH",
            "CURRENT_BIRTHDAY_DISCOUNT_CONTRIBUTION",
        ],
        "BIRTHDAY_DISCOUNT_%": [
            "BIRTHDAY_DISCOUNT_PERCENT_CURRENT",
            "BIRTHDAY_DISCOUNT_PERCENT_PREVIOUS",
            "BIRTHDAY_DISCOUNT_PERCENT_GROWTH_RATE",
        ],
    }

    df = rename_columns(df, sections)
    # Rename columns using your configuration (ensure this dictionary is defined in your config)
    df = df.rename(columns=config.rename_dictionary_loyalty_kpi)
    df = transpose_order_pivot(df)
    df = melt_and_pivot(df)
    # Custom sort by metric and type
    metric_custom_order = [
        'Sales', 'Transactions', 'Guest Count', 'Basket Size',
        'Frequency Spend (Rolling 12 months)', 'Retail Freq. of Spend (Roll 12 months)', 'Service Freq. of Spend (Roll 12 months)', 'Redemption Value',
        'Loyalty Cost % of Sales', 'Birthday discount amount',
        'Birthday discount cost % of sales'
    ]

    type_custom_order = ["Current", "Growth period on period", "Contribution to total"]

    df['Metric'] = pd.Categorical(df['Metric'], categories=metric_custom_order, ordered=True)
    df['Type'] = pd.Categorical(df['Type'], categories=type_custom_order, ordered=True)
    df = df.sort_values(by=["Metric", "Type"])

    # Adjust the DataFrame as per your requirements
    # List of metrics where 'Non-loyalty' should be blank and 'Total' equals 'Total Loyalty'
    metrics_adjustments = [
        'Redemption Value',
        'Loyalty Cost % of Sales',
        'Birthday discount amount',
        'Birthday discount cost % of sales'
    ]

    # Set 'Non-loyalty' to blank and 'Total' equal to 'Total Loyalty' for specified metrics
    df.loc[df['Metric'].isin(metrics_adjustments), 'Non-loyalty'] = ''
    df.loc[df['Metric'].isin(metrics_adjustments), 'Total'] = df.loc[df['Metric'].isin(metrics_adjustments), 'Total Loyalty']

    # Filter out any rows with None or empty Metric values (helper rows)
    df = df[df['Metric'].notna() & (df['Metric'] != 'None') & (df['Metric'] != '')]
    
    # Ensure correct column order
    df = df[['Metric', 'Type', 'Green', 'Blue', 'Silver', 'Gold', 'Total Loyalty', 'Non-loyalty', 'Total']]

    # Format growth percentages for display
    df = format_loyalty_kpi_display(df)

    return df
