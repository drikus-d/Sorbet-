"""
This is the ops kpi module.
"""

import config
import pandas as pd
import utils as ut
import streamlit as st
from typing import List, Tuple

def ops_kpi_base_df(session, start_date: str, end_date: str, group: str):
    """
    This function is used to get the ops kpi.
    """
    query = ut.read_sql_query(config.OPS_KPI_PATH)
    # Format the query with start and end dates
    modified_query = query.format(start_date=start_date, end_date=end_date, group=group)

    # Load the data from the session
    df = ut.load_data(session, modified_query)

    return df


def ops_kpi_format_numeric_df(df: pd.DataFrame):
    """
    This function is used to format the ops kpi dataframe.
    """
    ops_numeric_columns = [
        "AVG_TOTAL_SALES_PER_STORE",
        "AVERAGE_TRADING_DENSITY",
        "AVG_SERVICE_SALES_PER_STORE",
        "AVG_SERVICE_UNITS_SOLD",
        "AVG_RETAIL_SALES_PER_STORE",
        "AVG_RETAIL_UNITS_SOLD",
        "TOTAL_TRANSACTION_COUNT",
        "TOTAL_TRANSACTION_COUNT_PREVIOUS",
        "AVG_TOTAL_TRANSACTIONS_PER_STORE",
        "TOTAL_BASKET_SIZE_AVERAGE",
        "SERVICE_BASKET_SIZE",
        "RETAIL_BASKET_SIZE",
        "UNIQUE_GUEST_COUNT",
        "NEW_GUEST_COUNT",
        "NEW_GUEST_PER_STORE",
        "ROLLING_UNIQUE_GUEST",
    ]
    # Ensure numeric columns are treated as numeric
    df[ops_numeric_columns] = df[ops_numeric_columns].apply(
        pd.to_numeric, errors="coerce"
    )

    # Apply the comma formatting for integers
    df[ops_numeric_columns] = df[ops_numeric_columns].applymap(
        lambda x: f"{x:,.0f}" if pd.notnull(x) else ""
    )
    return df


def ops_kpi_format_percentage_df(df: pd.DataFrame):
    """
    This function is used to format the ops kpi dataframe.
    """
    ops_percentage_columns = [
        "TOTAL_SALES_GROWTH",
        "TOTAL_SERVICE_SALES_GROWTH",
        "AVG_SERVICES_TO_AVG_TOTAL_CURRENT",
        "AVG_SERVICES_TO_AVG_TOTAL_PREVIOUS",
        "TOTAL_RETAIL_SALES_GROWTH",
        "AVG_RETAIL_TO_AVG_TOTAL_CURRENT",
        "AVG_RETAIL_TO_AVG_TOTAL_PREVIOUS",
        "TRANSACTIONS_GROWTH",
        "AVERAGE_BASKET_SIZE_GROWTH",
        "SERVICE_BASKET_SIZE_GROWTH",
        "RETAIL_BASKET_SIZE_GROWTH",
        "UNIQUE_GUEST_GROWTH",
        "NEW_GUEST_GROWTH",
        "AVG_FREQUENCY_SPEND_GROWTH",
    ]
    # Multiply by 100
    df[ops_percentage_columns] = df[ops_percentage_columns] * 100
    # Ensure numeric columns are treated as numeric
    df[ops_percentage_columns] = df[ops_percentage_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    # Apply percentage formatting for percentage columns
    df[ops_percentage_columns] = df[ops_percentage_columns].applymap(
        lambda x: f"{x:.1f}%" if pd.notnull(x) else ""
    )
    return df


def ops_kpi_format_frequency_spend_df(df: pd.DataFrame):
    """
    This function is used to format the ops kpi dataframe.
    """
    special_ops_format = ["AVG_GUEST_FREQUENCY_SPEND", "FREQUENCY_SPEND_ROLLING_12"]
    # Ensure numeric columns are treated as numeric
    df[special_ops_format] = df[special_ops_format].apply(
        pd.to_numeric, errors="coerce"
    )

    # Apply the comma formatting for integers
    df[special_ops_format] = df[special_ops_format].applymap(
        lambda x: f"{x:,.2f}" if pd.notnull(x) else ""
    )
    return df


def make_first_row_header(df: pd.DataFrame):
    """
    Makes the first row of the DataFrame the header without removing it from the data.
    """
    # Create a copy of the first row to use as the new header
    new_header = df.iloc[0]
    df.columns = new_header  # Set new header
    df = df[1:].reset_index(drop=True)  # Keep the first row in data but drop original index
    df.index.name = new_header.name  # Preserve original index name
    return df


def restructure_df_with_sections_and_metrics(df):
    """
    This function is used to restructure the ops kpi dataframe with sections and metrics.
    """
    metric_section_map = {
        "TOTAL_SALES": "Sales",
        "SALES_GROWTH": "Sales",
        "AVG_TOTAL_SALES_PER_STORE": "Sales",
        "TOTAL_SALES_GROWTH": "Sales",
        "AVERAGE_TRADING_DENSITY": "Sales",
        "AVG_SERVICE_SALES_PER_STORE": "Sales",
        "TOTAL_SERVICE_SALES_GROWTH": "Sales",
        "TOTAL_TRANSACTIONS": "Transactions and Basket Size",
        "TRANSACTION_GROWTH": "Transactions and Basket Size",
        "TOTAL_TRANSACTION_COUNT": "Transactions and Basket Size",
        "TOTAL_TRANSACTION_COUNT_PREVIOUS": "Transactions and Basket Size",
        "AVG_TOTAL_TRANSACTIONS_PER_STORE": "Transactions and Basket Size",
        "TRANSACTIONS_GROWTH": "Transactions and Basket Size",
        "TOTAL_BASKET_SIZE_AVERAGE": "Transactions and Basket Size",
        "AVERAGE_BASKET_SIZE_GROWTH": "Transactions and Basket Size",
        "SERVICE_BASKET_SIZE": "Transactions and Basket Size",
        "SERVICE_BASKET_SIZE_GROWTH": "Transactions and Basket Size",
        "RETAIL_BASKET_SIZE": "Transactions and Basket Size",
        "RETAIL_BASKET_SIZE_GROWTH": "Transactions and Basket Size",
        "UNIQUE_GUEST_COUNT": "Other KPIs",
        "UNIQUE_GUEST_GROWTH": "Other KPIs",
        "ROLLING_UNIQUE_GUEST": "Other KPIs",
        "NEW_GUEST_COUNT": "Other KPIs",
        "NEW_GUEST_GROWTH": "Other KPIs",
        "NEW_GUEST_PER_STORE": "Other KPIs",
        "AVG_GUEST_FREQUENCY_SPEND": "Other KPIs",
        "FREQUENCY_SPEND_ROLLING_12": "Other KPIs",
        "AVG_FREQUENCY_SPEND_GROWTH": "Other KPIs",
        "AVG_RETAIL_SALES_PER_STORE": "Sales",
        "AVG_RETAIL_TO_AVG_TOTAL_CURRENT": "Sales",
        "AVG_RETAIL_TO_AVG_TOTAL_PREVIOUS": "Sales",
        "AVG_RETAIL_UNITS_SOLD": "Sales",
        "AVG_SERVICES_TO_AVG_TOTAL_CURRENT": "Sales",
        "AVG_SERVICES_TO_AVG_TOTAL_PREVIOUS": "Sales",
        "AVG_SERVICE_UNITS_SOLD": "Sales",
        "TOTAL_RETAIL_SALES_GROWTH": "Sales",
    }

    # Extract first column as 'Metric' and map it to 'Section'
    df["Metric"] = df.iloc[:, 0]
    df["Section"] = df["Metric"].map(metric_section_map)

    # Reorder columns to place 'Section' and 'Metric' at the beginning
    column_order = ["Section", "Metric"] + [col for col in df.columns if col not in ["Section", "Metric"]]
    df = df[column_order]

    return df

def add_section_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a blank row with only the section name as a standalone header for each new section.
    Assumes 'Section' and 'Metric' are index levels in the DataFrame.
    """
    # Reset the index to work with 'Section' and 'Metric' as columns
    df_reset = df.reset_index()
    
    # Create an empty list to store rows with headers
    formatted_rows = []
    
    # Track the previous section to detect new sections
    previous_section = None
    
    # Iterate through each row in the DataFrame
    for i, row in df_reset.iterrows():
        current_section = row["Section"]
        
        # Check if this row starts a new section
        if current_section != previous_section:
            # Create a blank row with only the section name populated
            section_header = {col: "" for col in df_reset.columns}
            section_header["Section"] = current_section
            formatted_rows.append(section_header)
            previous_section = current_section
        
        # Append the actual row data
        formatted_rows.append(row.to_dict())
    
    # Convert the list of dictionaries back into a DataFrame
    formatted_df = pd.DataFrame(formatted_rows)
    
    # Set 'Section' and 'Metric' back as the MultiIndex
    formatted_df = formatted_df.set_index(["Section", "Metric"])
    formatted_df.fillna("", inplace=True)  # Fill NaNs with empty strings for consistency
    
    return formatted_df



def column_ordering(df: pd.DataFrame, group: str) -> pd.DataFrame:
    """
    Orders the columns of the dataframe, preserving the index.
    """
    # Remove the first column
    df = df.iloc[:, 1:]
    if group == "CATEGORY":
        columns_sorted = ['A +', 'A', 'B', 'C', 'TOTAL']
    else:
        # Step 2: Sort columns alphabetically
        columns_sorted = sorted(df.columns)
        
        # Step 3: Move 'TOTAL' to the end if it exists
        if "TOTAL" in columns_sorted:
            columns_sorted.remove("TOTAL")
            columns_sorted.append("TOTAL")
    
    # Reorder the DataFrame columns
    ordered_columns = columns_sorted  # Add the first column back to the ordered list
    df = df[ordered_columns]
    
    return df

def set_multiindex_section_metric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sets 'Section' and 'Metric' columns as a MultiIndex for the dataframe.
    """
    # Reset the index in case there’s an existing one
    df = df.reset_index(drop=True)
    
    # Ensure 'Section' and 'Metric' are treated as index columns
    if 'Section' in df.columns and 'Metric' in df.columns:
        df = df.set_index(['Section', 'Metric'])
    else:
        raise KeyError("The columns 'Section' and 'Metric' must exist in the DataFrame")

    return df

def rename_index(df):

    # Create a more readable mapping 
    rename_dict = {
        'AVG_TOTAL_SALES_PER_STORE': 'Avg Total Sales per Store',
        'TOTAL_SALES_GROWTH': 'Total Sales Growth',
        'AVERAGE_TRADING_DENSITY': 'Average Trading Density',
        'AVG_SERVICE_SALES_PER_STORE': 'Avg Service Sales per Store',
        'TOTAL_SERVICE_SALES_GROWTH': 'Total Service Sales Growth',
        'AVG_SERVICES_TO_AVG_TOTAL_CURRENT': 'Services to Total Ratio (Current)',
        'AVG_SERVICES_TO_AVG_TOTAL_PREVIOUS': 'Services to Total Ratio (Previous)',
        'AVG_SERVICE_UNITS_SOLD': 'Avg Service Units Sold',
        'AVG_RETAIL_SALES_PER_STORE': 'Avg Retail Sales per Store',
        'TOTAL_RETAIL_SALES_GROWTH': 'Total Retail Sales Growth',
        'AVG_RETAIL_TO_AVG_TOTAL_CURRENT': 'Retail to Total Ratio (Current)',
        'AVG_RETAIL_TO_AVG_TOTAL_PREVIOUS': 'Retail to Total Ratio (Previous)',
        'AVG_RETAIL_UNITS_SOLD': 'Avg Retail Units Sold',
        'TOTAL_TRANSACTION_COUNT': 'Total Transaction Count',
        'TOTAL_TRANSACTION_COUNT_PREVIOUS': 'Total Transaction Count (Previous)',
        'AVG_TOTAL_TRANSACTIONS_PER_STORE': 'Avg Transactions per Store',
        'TRANSACTIONS_GROWTH': 'Transactions Growth',
        'TOTAL_BASKET_SIZE_AVERAGE': 'Average Basket Size',
        'AVERAGE_BASKET_SIZE_GROWTH': 'Basket Size Growth',
        'SERVICE_BASKET_SIZE': 'Service Basket Size',
        'SERVICE_BASKET_SIZE_GROWTH': 'Service Basket Size Growth',
        'RETAIL_BASKET_SIZE': 'Retail Basket Size',
        'RETAIL_BASKET_SIZE_GROWTH': 'Retail Basket Size Growth',
        'UNIQUE_GUEST_COUNT': 'Unique Guest Count',
        'UNIQUE_GUEST_GROWTH': 'Unique Guest Growth',
        'ROLLING_UNIQUE_GUEST': 'Rolling Unique Guests',
        'NEW_GUEST_COUNT': 'New Guest Count',
        'NEW_GUEST_GROWTH': 'New Guest Growth',
        'NEW_GUEST_PER_STORE': 'New Guests per Store',
        'AVG_GUEST_FREQUENCY_SPEND': 'Avg Guest Frequency Spend',
        'AVG_FREQUENCY_SPEND_GROWTH': 'Frequency Spend Growth',
        'FREQUENCY_SPEND_ROLLING_12': 'Frequency Spend (Rolling 12)'
    }

    # Rename the level
    df = df.rename(index=rename_dict, level='Metric')
    return df

def format_indent_ops_kpi(df):
    """
    Formats the loyalty KPI DataFrame by creating a compact index with indentation
    and inserting blank rows before each new section (except the first section).

    Parameters:
        df (pd.DataFrame): Input DataFrame with MultiIndex ['Metric', 'Type'].

    Returns:
        pd.DataFrame: Formatted DataFrame with indented grouping and blank rows.
    """

    # Step 1: Create a compact index with indentation
    compact_index = []
    previous_metric = None

    # Iterate over the MultiIndex levels to create the compact index
    for metric, type_ in df.index:
        if metric == previous_metric:
            # Indent the 'Type' to represent grouping
            compact_index.append(f"    {type_}")
        else:
            # Start a new group with the 'Metric' name
            compact_index.append(metric)
        previous_metric = metric

    # Step 2: Add the compact index as a new column in the DataFrame
    df_display = df.copy()
    df_display.insert(0, "Metric_Type", compact_index)

    # Step 3: Reset the index to remove the MultiIndex
    df_display = df_display.reset_index(drop=True)

    # Step 4: Insert blank rows before each new section, except the first section
    # Identify rows where a new 'Metric' begins (non-indented)
    new_metric_rows = df_display[
        df_display["Metric_Type"].str.startswith("    ") == False  # pylint: disable=C0121
    ].index

    # Create a single-row blank DataFrame to insert
    blank_row = pd.DataFrame(
        [[""] * len(df_display.columns)], columns=df_display.columns
    )

    # Insert a blank row before each new section (skip the first section)
    for idx in reversed(new_metric_rows[1:]):  # Start from the second section
        df_display = pd.concat(
            [df_display.iloc[:idx], blank_row, df_display.iloc[idx:]], ignore_index=True
        )

    return df_display





def main_ops_kpi(session, start_date: str, end_date: str, group: str):
    """
    This function is used to get the main ops kpi.
    """
    df = ops_kpi_base_df(session, start_date, end_date, group)
    df = ops_kpi_format_numeric_df(df)
    df = ops_kpi_format_percentage_df(df)
    df = ops_kpi_format_frequency_spend_df(df)

    # Transpose the dataframe
    df = df.T
    df.reset_index(inplace=True)
    df = make_first_row_header(df)
    # Group the dataframe by section
    df = restructure_df_with_sections_and_metrics(df)
    df = set_multiindex_section_metric(df)
    df = column_ordering(df, group)
    df = add_section_headers(df)
    df = rename_index(df)
    df = format_indent_ops_kpi(df)
    return df


def combine_ops_kpi_dataframes(all_dataframes: List[pd.DataFrame], subheaders: List[str]) -> Tuple[List[pd.DataFrame], List[str]]:
    """
    Pre-process Ops KPI dataframes to combine them side by side with blank separator columns.
    Returns modified lists of dataframes and subheaders.
    """
    ops_kpi_dfs = []
    ops_kpi_headers = []
    ops_kpi_indices = []
    
    # Collect Ops KPI indices and dataframes
    for idx, (df, subheader) in enumerate(zip(all_dataframes, subheaders)):
        if subheader.startswith("Ops KPI"):
            ops_kpi_dfs.append(df)
            ops_kpi_headers.append(subheader)
            ops_kpi_indices.append(idx)
            
    if not ops_kpi_dfs:
        return all_dataframes, subheaders

    # Find position of first Ops KPI section
    first_ops_position = min(ops_kpi_indices)

    # Reorder dataframes to Brand, Region, Category
    ordered_dfs = []
    ordered_headers = []
    for section in ['Brand', 'Region', 'Category']:
        for i, header in enumerate(ops_kpi_headers):
            if section in header:
                ordered_dfs.append(ops_kpi_dfs[i])
                ordered_headers.append(ops_kpi_headers[i])

    # Combine the dataframes side by side with separator columns
    combined_df = ordered_dfs[0].copy()  # Start with Brand
    
    # Add Region and Category, with separator columns
    for df in ordered_dfs[1:]:
        # Create a new empty DataFrame with just the separator column
        separator_df = pd.DataFrame(index=combined_df.index, columns=[f"separator_{len(combined_df.columns)}"])
        separator_df.fillna("", inplace=True)
        
        # Concatenate the separator and the new data horizontally
        combined_df = pd.concat([combined_df, separator_df, df.iloc[:, 1:]], axis=1)

    # Create new lists excluding original Ops KPI dataframes
    new_dataframes = [df for idx, df in enumerate(all_dataframes) 
                     if idx not in ops_kpi_indices]
    new_subheaders = [header for idx, header in enumerate(subheaders) 
                     if idx not in ops_kpi_indices]
    
    # Insert the combined Ops KPI dataframe at the original position
    new_dataframes.insert(first_ops_position, combined_df)
    new_subheaders.insert(first_ops_position, "Ops KPI")

    return new_dataframes, new_subheaders