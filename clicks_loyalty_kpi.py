"""
This is the ops kpi module.
"""

import config
import pandas as pd
import utils as ut


def loyalty_kpi_main_measures(session, start_date: str, end_date: str):
    """
    This function is used to get the ops kpi.
    """
    query = ut.read_sql_query(config.CLICKS_ALL_MEASURES_PATH)
    # Format the query with start and end dates
    modified_query = query.format(start_date=start_date, end_date=end_date)

    # Load the data from the session
    df = ut.load_data(session, modified_query)

    return df


def loyalty_kpi_growth_column(df: pd.DataFrame):
    """
    This function is used to add the growth column to the ops kpi dataframe.
    """
    df = df.T
    # Promote the first row to a header
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    
    # Define percentage columns that should have growth calculated (they're percentages but still need growth)
    percentage_columns = [
        "CLICKS_LOYALTY_SALES_OVER_TOTAL",
        "CLICKS_LOYALTY_TRANSACTIONS_OVER_TOTAL", 
        "CLICK_LOYALTY_BASKET_SIZE_OVER_TOTAL",
        "NEW_CLICKS_LOYALTY_GUEST_OVER_NEW_GUESTS",
        "CLICKS_LOYALTY_NEW_GUESTS_OVER_TOTAL_UNIQUE_GUESTS"
    ]
    
    # The columns should be 'CURRENT' and 'PREVIOUS' at this point
    # Add the growth column for all metrics
    if "CURRENT" in df.columns and "PREVIOUS" in df.columns:
        # Initialize GROWTH column as float
        df["GROWTH"] = 0.0
        
        # Convert CURRENT and PREVIOUS to numeric
        df["CURRENT"] = pd.to_numeric(df["CURRENT"], errors="coerce")
        df["PREVIOUS"] = pd.to_numeric(df["PREVIOUS"], errors="coerce")
        
        # Calculate growth for all rows (including percentage columns)
        for idx in df.index:
            current_val = df.loc[idx, "CURRENT"]
            previous_val = df.loc[idx, "PREVIOUS"]
            
            if pd.notna(current_val) and pd.notna(previous_val) and previous_val != 0:
                growth = (current_val / previous_val) - 1
                df.loc[idx, "GROWTH"] = growth
            else:
                df.loc[idx, "GROWTH"] = 0.0
    else:
        # If columns don't exist, create empty GROWTH column
        df["GROWTH"] = 0.0
    
    df = df.T
    return df


def clicks_loyalty_kpi_format_numeric_df(df: pd.DataFrame):
    """
    Formats the clicks loyalty KPI DataFrame:
    - Applies comma formatting to numeric columns in 'CURRENT' and 'PREVIOUS' rows.
    - Applies percentage formatting to 'GROWTH' row.
    """
    clicks_loyalty_numeric_columns = [
        "CLICKS_LOYALTY_SALES",
        "NON_CLICKS_SALES",
        "SALES",
        "CLICKS_LOYALTY_TRANSACTION_COUNT",
        "NON_CLICKS_TRANSACTION_COUNT",
        "TOTAL_TRANSACTION_COUNT",
        "CLICKS_LOYALTY_BASKET_SIZE",
        "NON_CLICKS_BASKET_SIZE",
        "BASKET_SIZE_TOTAL",
        "CLICKS_LOYALTY_NEW_GUEST_COUNT",
        "NEW_GUEST_COUNT",
        "UNIQUE_GUEST_COUNT",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_CLICKS_CLUBCARD",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_SERVICE",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_RETAIL",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_CLICKS_CLUBCARD_SERVICE",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_CLICKS_CLUBCARD_RETAIL"
    ]

    # Ensure 'Period' is a column, not an index
    if "PERIOD" in df.index.names:
        df = df.reset_index()

    # Convert all columns to object type to avoid dtype conflicts
    for col in clicks_loyalty_numeric_columns:
        if col in df.columns:
            df[col] = df[col].astype(str)

    # Define frequency columns that should show decimal places
    frequency_columns = [
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_CLICKS_CLUBCARD",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_SERVICE",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_RETAIL",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_CLICKS_CLUBCARD_SERVICE",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_CLICKS_CLUBCARD_RETAIL"
    ]
    
    # Apply comma formatting for 'CURRENT' and 'PREVIOUS' rows
    for col in clicks_loyalty_numeric_columns:
        if col in df.columns:
            if col in frequency_columns:
                # Format frequency columns with 2 decimal places
                df.loc[df["PERIOD"].isin(["CURRENT", "PREVIOUS"]), col] = df.loc[
                    df["PERIOD"].isin(["CURRENT", "PREVIOUS"]), col
                ].apply(
                    lambda x: f"{float(x):.2f}" if pd.notnull(x) and x != "" and x != "nan" and x != "None" else ""
                )
            else:
                # Format other numeric columns as whole numbers
                df.loc[df["PERIOD"].isin(["CURRENT", "PREVIOUS"]), col] = df.loc[
                    df["PERIOD"].isin(["CURRENT", "PREVIOUS"]), col
                ].apply(
                    lambda x: f"{float(x):,.0f}" if pd.notnull(x) and x != "" and x != "nan" and x != "None" else ""
                )

    # Apply percentage formatting for 'GROWTH' row
    for col in clicks_loyalty_numeric_columns:
        if col in df.columns:
            df.loc[df["PERIOD"] == "GROWTH", col] = df.loc[
                df["PERIOD"] == "GROWTH", col
            ].apply(lambda x: f"{float(x) * 100:.1f}%" if pd.notnull(x) and x != "" and x != "nan" and x != "None" else "")

    return df


def clicks_loyalty_kpi_format_percentage_df(df: pd.DataFrame):
    """
    This function is used to format the ops kpi dataframe.
    """
    clicks_loyalty_percentage_columns = [
        "CLICKS_LOYALTY_SALES_OVER_TOTAL",
        "CLICKS_LOYALTY_TRANSACTIONS_OVER_TOTAL",
        "CLICK_LOYALTY_BASKET_SIZE_OVER_TOTAL",
        "NEW_CLICKS_LOYALTY_GUEST_OVER_NEW_GUESTS",
        "CLICKS_LOYALTY_NEW_GUESTS_OVER_TOTAL_UNIQUE_GUESTS",
    ]

    # Multiply by 100
    df[clicks_loyalty_percentage_columns] = df[clicks_loyalty_percentage_columns] * 100
    # Ensure numeric columns are treated as numeric
    df[clicks_loyalty_percentage_columns] = df[clicks_loyalty_percentage_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    # Apply percentage formatting for percentage columns
    for col in clicks_loyalty_percentage_columns:
        df[col] = df[col].astype(str)
        df[col] = df[col].apply(lambda x: f"{float(x):.1f}%" if pd.notnull(x) and x != "" and x != "nan" and x != "None" else "")
    return df


def clicks_loyalty_kpi_apply_color_formatting(df: pd.DataFrame):
    """
    Apply background color formatting to percentage values in the Clicks Loyalty KPI DataFrame.
    This function is kept for compatibility but no longer applies HTML formatting.
    Background colors are now handled in the Excel export function.
    """
    # No longer applying HTML color formatting - background colors are handled in Excel export
    return df


def clicks_loyalty_kpi_make_first_row_header(df: pd.DataFrame):
    """
    Makes the first row of the DataFrame the header without removing it from the data.
    """
    # Create a copy of the first row to use as the new header
    new_header = df.iloc[0]
    df.columns = new_header  # Set new header
    df = df[1:].reset_index(
        drop=True
    )  # Keep the first row in data but drop original index
    df.index.name = new_header.name  # Preserve original index name
    return df


def clicks_loyalty_kpi_restructure_df_with_sections_and_metrics(df):
    """
    This function is used to restructure the ops kpi dataframe with sections and metrics.
    """
    # Define the metric section map
    metric_section_map = {
        "CLICKS_LOYALTY_SALES": "SALES",
        "NON_CLICKS_SALES": "SALES",
        "SALES": "SALES",
        "CLICKS_LOYALTY_SALES_OVER_TOTAL": "SALES",
        "CLICKS_LOYALTY_TRANSACTION_COUNT": "TRANSACTIONS",
        "NON_CLICKS_TRANSACTION_COUNT": "TRANSACTIONS",
        "TOTAL_TRANSACTION_COUNT": "TRANSACTIONS",
        "CLICKS_LOYALTY_TRANSACTIONS_OVER_TOTAL": "TRANSACTIONS",
        "CLICKS_LOYALTY_BASKET_SIZE": "BASKET_SIZE",
        "NON_CLICKS_BASKET_SIZE": "BASKET_SIZE",
        "BASKET_SIZE_TOTAL": "BASKET_SIZE",
        "CLICK_LOYALTY_BASKET_SIZE_OVER_TOTAL": "BASKET_SIZE",
        "CLICKS_LOYALTY_NEW_GUEST_COUNT": "GUESTS",
        "NEW_GUEST_COUNT": "GUESTS",
        "NEW_CLICKS_LOYALTY_GUEST_OVER_NEW_GUESTS": "GUESTS",
        "UNIQUE_GUEST_COUNT": "GUESTS",
        "CLICKS_LOYALTY_NEW_GUESTS_OVER_TOTAL_UNIQUE_GUESTS": "GUESTS",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS": "GUESTS",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_CLICKS_CLUBCARD": "GUESTS",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_SERVICE": "GUESTS",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_RETAIL": "GUESTS",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_CLICKS_CLUBCARD_SERVICE": "GUESTS",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_CLICKS_CLUBCARD_RETAIL": "GUESTS",
    }

    # Extract first column as 'Metric' and map it to 'Section'
    df["Metric"] = df.iloc[:, 0]
    df["Section"] = df["Metric"].map(metric_section_map)

    # Reorder columns to place 'Section' and 'Metric' at the beginning
    column_order = ["Section", "Metric"] + [
        col for col in df.columns if col not in ["Section", "Metric"]
    ]
    df = df[column_order]

    return df


def clicks_loyalty_kpi_set_multiindex_section_metric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sets 'Section' and 'Metric' columns as a MultiIndex for the dataframe.
    """
    # Reset the index in case there’s an existing one
    df = df.reset_index(drop=True)

    # Ensure 'Section' and 'Metric' are treated as index columns
    if "Section" in df.columns and "Metric" in df.columns:
        df = df.set_index(["Section", "Metric"])
    else:
        raise KeyError("The columns 'Section' and 'Metric' must exist in the DataFrame")

    return df


def clicks_loyalty_kpi_add_section_headers(df: pd.DataFrame) -> pd.DataFrame:
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
    formatted_df.fillna(
        "", inplace=True
    )  # Fill NaNs with empty strings for consistency

    return formatted_df


def clicks_loyalty_kpi_format_indent_df(df):
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
        df_display["Metric_Type"].str.startswith("    ")
        == False  # pylint: disable=C0121
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


def rename_index(df):

    # Create a more readable mapping 
    rename_dict = {
        "CLICKS_LOYALTY_SALES": "Clicks loyalty sales",
        "NON_CLICKS_SALES": "Non clicks sales",
        "SALES": "Total sales",
        "CLICKS_LOYALTY_SALES_OVER_TOTAL": "Clicks loyalty sales over total",
        "CLICKS_LOYALTY_TRANSACTION_COUNT": "Clicks loyalty transactions count",
        "NON_CLICKS_TRANSACTION_COUNT": "Non clicks transactions count",
        "TOTAL_TRANSACTION_COUNT": "Total transactions count",
        "CLICKS_LOYALTY_TRANSACTIONS_OVER_TOTAL": "Clicks loyalty transactions over total",
        "CLICKS_LOYALTY_BASKET_SIZE": "Clicks loyalty basket size",
        "NON_CLICKS_BASKET_SIZE": "Non Clicks basket size",
        "BASKET_SIZE_TOTAL": "Basket size total",
        "CLICK_LOYALTY_BASKET_SIZE_OVER_TOTAL": "Clicks loyalty basket size over total",
        "CLICKS_LOYALTY_NEW_GUEST_COUNT": "Clicks loyalty new guest count",
        "NEW_GUEST_COUNT": "New guest count",
        "NEW_CLICKS_LOYALTY_GUEST_OVER_NEW_GUESTS": "New clicks loyalty guest over new guests",
        "UNIQUE_GUEST_COUNT": "Unique guest count",
        "CLICKS_LOYALTY_NEW_GUESTS_OVER_TOTAL_UNIQUE_GUESTS": "Clicks loyalty new guests over total unique guests",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS": "All Transactions Frequency of Spend (Rolling 12 months)",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_CLICKS_CLUBCARD": "Clicks Clubcard Frequency of Spend (Rolling 12 months)",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_SERVICE": "All Transactions Frequency of Spend (Rolling 12 months) - Service",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_RETAIL": "All Transactions Frequency of Spend (Rolling 12 months) - Retail",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_CLICKS_CLUBCARD_SERVICE": "Clicks Clubcard Frequency of Spend (Rolling 12 months) - Service",
        "FREQUENCY_OF_SPEND_ROLLING_12_MONTHS_CLICKS_CLUBCARD_RETAIL": "Clicks Clubcard Frequency of Spend (Rolling 12 months) - Retail",
    } 

    rename_section = {
        "SALES": "Sales",
        "TRANSACTIONS": "Transactions",
        "BASKET_SIZE": "Basket size",
        "GUESTS": "Guests",
    }

    # Rename the level
    df = df.rename(index=rename_dict, level='Metric')
    df = df.rename(index=rename_section, level='Section')
    return df

def loyalty_kpi_main_measures_table(session, start_date: str, end_date: str):
    """
    This function is used to add the growth column to the ops kpi dataframe.
    """
    df = loyalty_kpi_main_measures(session, start_date, end_date)
    df = loyalty_kpi_growth_column(df)  # Calculate growth FIRST with raw numeric data
    df = clicks_loyalty_kpi_format_percentage_df(df)  # Format percentages AFTER growth calculation
    df = clicks_loyalty_kpi_format_numeric_df(df)
    df = df.T
    df.reset_index(inplace=True)
    df = clicks_loyalty_kpi_make_first_row_header(df)
    df = clicks_loyalty_kpi_restructure_df_with_sections_and_metrics(df)
    df = clicks_loyalty_kpi_set_multiindex_section_metric(df)
    # Remove the first column
    df = df.iloc[:, 1:]
    df = clicks_loyalty_kpi_add_section_headers(df)
    df = rename_index(df)
    df = clicks_loyalty_kpi_format_indent_df(df)
    df = clicks_loyalty_kpi_apply_color_formatting(df)
    return df


def loyalty_kpi_centers(session, start_date: str, end_date: str):
    """
    This function is used to get the loyalty kpi centers.
    """
    query = ut.read_sql_query(config.CLICKS_CENTERS_PATH)
    modified_query = query.format(start_date=start_date, end_date=end_date)
    df = ut.load_data(session, modified_query)
    return df


def total_row_centers(df: pd.DataFrame):
    """
    This function is used to get the total row for the centers.
    """
    total_row = df.sum(numeric_only=True)
    total_row = total_row.to_frame().T
    total_row["CENTER"] = "TOTAL"
    return total_row


def make_numeric_columns(df: pd.DataFrame):
    """
    This function is used to make the columns numeric.
    """
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col].astype(str).str.strip(), errors="coerce")
    return df


def get_final_ratio_column(df: pd.DataFrame):
    """
    This function is used to get the final ratio column.
    """
    df["CLICKS_TO_TOTAL_SALES"] = df["CLICKS_REVENUE"] / df["REVENUE"]
    df["TOTAL_BASKET_SIZE"] = df["REVENUE"] / df["TOTAL_TRANSACTION_COUNT"]
    df["CLICKS_BASKET_SIZE"] = df["CLICKS_REVENUE"] / df["CLICKS_TRANSACTION_COUNT"]
    df["NON_CLICKS_BASKET_SIZE"] = df["NON_CLICKS_REVENUE"] / df["NON_CLICKS_TRANSACTION_COUNT"]
    df["CLICKS_BASKET_SIZE_TO_NON_CLICKS_BASKET_SIZE"] = (
        df["CLICKS_BASKET_SIZE"] / df["NON_CLICKS_BASKET_SIZE"]
    )
    df["NEW_GUEST_TO_UNIQUE_GUEST"] = df["NEW_GUEST_COUNT"] / df["UNIQUE_GUEST_COUNT"]
    df["NEW_CLICKS_LOYALTY_GUEST_TO_UNIQUE_GUESTS"] = (
        df["CLICKS_NEW_GUEST_COUNT"] / df["UNIQUE_GUEST_COUNT"]
    )
    return df


def select_columns(df: pd.DataFrame):
    """
    This function is used to select the columns.
    """
    df = df[
        [
            "CENTER",
            "CLICKS_TO_TOTAL_SALES",
            "CLICKS_BASKET_SIZE_TO_NON_CLICKS_BASKET_SIZE",
            "NEW_GUEST_TO_UNIQUE_GUEST",
            "NEW_CLICKS_LOYALTY_GUEST_TO_UNIQUE_GUESTS",
        ]
    ]
    return df

def convert_to_percentage(df: pd.DataFrame):
    """
    This function is used to convert the columns to percentage.
    """
    # Multiply by 100
    df.iloc[:, 1:] = df.iloc[:, 1:] * 100
    # Convert all columns except the first one to percentage
    df.iloc[:, 1:] = df.iloc[:, 1:].applymap(lambda x: f"{x:.1f}%" if pd.notnull(x) else "")
    return df


def loyalty_kpi_centers_main_table(
    session, start_date: str, end_date: str, head_or_tail: str = "head", limit: int = 20
):
    """
    This function is used to get the loyalty kpi centers.
    """
    df = loyalty_kpi_centers(session, start_date, end_date)
    # Convert columns to numeric
    df = make_numeric_columns(df)
    # Calculate ORDERING_COLUMN and confirm numeric type
    df["ORDERING_COLUMN"] = pd.to_numeric(
        df["CLICKS_REVENUE"] / df["REVENUE"], errors="coerce"
    )
    # Sort and select the desired number of rows
    df = df.sort_values(by="ORDERING_COLUMN", ascending=False)
    # Apply limit based on head_or_tail
    if head_or_tail == "head":
        df = df.head(limit)
    else:
        df = df.tail(limit)
    # Get totals and add to the dataframe
    total = total_row_centers(df)
    df = pd.concat([df, total])
    df = get_final_ratio_column(df)
    df = select_columns(df)
    df = convert_to_percentage(df)
    return df
