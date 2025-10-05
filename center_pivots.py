"""
This module contains functions for creating and
manipulating dataframes for the center and 
center groupings section in streamlit.
"""

import pandas as pd
import config
import utils as ut


def base_group_by_results(session, start_date: str, end_date: str):
    """
    This function is used to get the base group by results for the center pivots.
    """
    base_list_to_convert = [
        "CURRENT_SERVICE_REVENUE",
        "CURRENT_RETAIL_REVENUE",
        "CURRENT_TOTAL_REVENUE",
        "PREVIOUS_SERVICE_REVENUE",
        "PREVIOUS_RETAIL_REVENUE",
        "PREVIOUS_TOTAL_REVENUE",
        "SERVICE_BUDGET",
        "RETAIL_BUDGET",
        "TOTAL_BUDGET",
        "CURRENT_STORE_COUNT",
        "PREVIOUS_STORE_COUNT",
    ]

    # Load the base query
    stores_base_query = ut.read_sql_query(config.STORE_PIVOTS_NO_LOYALTY_PATH)

    params_brand = {
        "start_date": start_date,
        "end_date": end_date,
    }

    # Format the query with start and end dates
    modified_query = stores_base_query.format(
        start_date=params_brand["start_date"], end_date=params_brand["end_date"]
    )

    # Load the data from the session
    df = ut.load_data(session, modified_query)

    # Convert specified columns to numeric
    for col in base_list_to_convert:
        if col in df.columns:  # Check if the column exists in the DataFrame
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            )  # Converts to float64 or NaN if conversion fails

    # Custom order for the 'CATEGORY' column
    df.sort_values(by=["CURRENT_TOTAL_REVENUE"], ascending=[False], inplace=True)

    return df


def filter_df(df: pd.DataFrame, filter_dict: dict) -> pd.DataFrame:
    """
    This function is used to filter the DataFrame based on the filter_dict.
    """
    for key, value in filter_dict.items():
        df = df[df[key] == value]
    return df


# Get the sum of numeric columns
def sum_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function sums all numeric columns in the DataFrame and
    returns the result as a single-row DataFrame.
    """
    # Sum all numeric columns
    total_row = df.select_dtypes(include=["number"]).sum(numeric_only=True)

    # Add a label for the 'group_by' column (assuming it's the first column)
    total_row[df.columns[0]] = "Total"

    # Convert the Series to a DataFrame
    total_row = pd.DataFrame([total_row], columns=df.columns)

    return total_row


def create_base_dataframes(df):
    """
    This function is used to create grouped dataframes by Brand, Region, and Category.
    """
    df_by_brand = (
        df.groupby("BRAND")
        .sum(numeric_only=True)
        .reset_index()
        .sort_values(by="CURRENT_TOTAL_REVENUE", ascending=False)
    )
    df_by_region = (
        df.groupby("REGION")
        .sum(numeric_only=True)
        .reset_index()
        .sort_values(by="CURRENT_TOTAL_REVENUE", ascending=False)
    )
    df_by_category = (
        df.groupby("CATEGORY")
        .sum(numeric_only=True)
        .reset_index()
        .sort_values(by="CURRENT_TOTAL_REVENUE", ascending=False)
    )
    df_top_10 = (
        df.head(10)
        .groupby("CENTER")
        .sum(numeric_only=True)
        .reset_index()
        .sort_values(by="CURRENT_TOTAL_REVENUE", ascending=False)
    )
    df_icu = (
        df[df["CURRENT_TOTAL_REVENUE"] > 0]
        .tail(10)
        .groupby("CENTER")
        .sum(numeric_only=True)
        .reset_index()
        .sort_values(by="CURRENT_TOTAL_REVENUE", ascending=False)
    )
    df_closed = (
        df[df["IS_CLOSED"].fillna(False)]
        .groupby("CENTER")
        .sum(numeric_only=True)
        .reset_index()
        .sort_values(by="CURRENT_TOTAL_REVENUE", ascending=False)
    )
    df_new = (
        df[df["IS_NEW"].fillna(False)]
        .groupby("CENTER")
        .sum(numeric_only=True)
        .reset_index()
        .sort_values(by="CURRENT_TOTAL_REVENUE", ascending=False)
    )
    # Return the three resulting DataFrames
    return (
        df_by_brand,
        df_by_region,
        df_by_category,
        df_top_10,
        df_icu,
        df_closed,
        df_new,
    )


def create_and_append_totals(df: pd.DataFrame) -> dict:
    """
    This function is used to create and append the totals to the DataFrame.
    """
    # Dictionary to store total DataFrames
    df_by_brand, df_by_region, df_by_category, df_top_10, df_icu, df_closed, df_new = (
        create_base_dataframes(df)
    )

    # Put the dataframes in a dictionary
    dataframes_center_and_groupings = {
        "df_base": df,
        "df_by_brand": df_by_brand,
        "df_by_region": df_by_region,
        "df_by_category": df_by_category,
        "df_top_10": df_top_10,
        "df_icu": df_icu,
        "df_closed": df_closed,
        "df_new": df_new,
    }

    # Loop through the dataframes and append the totals
    for key, value in dataframes_center_and_groupings.items():
        # Order category column
        category_order = ["A +", "A", "B", "C"]
        if "CATEGORY" in value.columns:
            value["CATEGORY"] = pd.Categorical(
                value["CATEGORY"], categories=category_order, ordered=True
            )
            value.sort_values(by=["CATEGORY"], ascending=[True], inplace=True)
        # Get the total row
        total_row = sum_numeric_columns(value)
        # Append the total row to the DataFrame
        dataframes_center_and_groupings[key] = pd.concat(
            [value, total_row], ignore_index=True
        )

    return dataframes_center_and_groupings


def contribution_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function calculates the contribution of each row in a group_by column
    (e.g., brand) to the total of the target column (e.g., total revenue).
    """
    list_of_columns = [
        ("% CURRENT REV CONTR", "CURRENT_TOTAL_REVENUE"),
        ("% PREVIOUS REV CONTR", "PREVIOUS_TOTAL_REVENUE"),
        ("% TOTAL BUDGET", "TOTAL_BUDGET"),
    ]
    
    # Calculate totals BEFORE calculating percentages
    totals = {}
    for column in list_of_columns:
        # Calculate total from all rows except the "Total" row
        non_total_rows = df[df.iloc[:, 0] != "Total"]
        totals[column[1]] = non_total_rows[column[1]].sum()
    
    # Calculate the contribution for each row as a percentage of the total revenue
    for column in list_of_columns:
        df[column[0]] = df[column[1]] / totals[column[1]] * 100
        # Keep as numeric values for proper summation - don't convert to string yet
    
    return df


def growth_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function calculates the growth of each row
    in a group_by column (e.g., brand) to the previous period.
    """
    # Tuple for growth rates
    growth_rates = [
        (
            "SERVICES CURRENT TO PREVIOUS %",
            "CURRENT_SERVICE_REVENUE",
            "PREVIOUS_SERVICE_REVENUE",
        ),
        (
            "RETAIL CURRENT TO PREVIOUS %",
            "CURRENT_RETAIL_REVENUE",
            "PREVIOUS_RETAIL_REVENUE",
        ),
        (
            "TOTAL CURRENT TO PREVIOUS %",
            "CURRENT_TOTAL_REVENUE",
            "PREVIOUS_TOTAL_REVENUE",
        ),
        ("SERVICES REVENUE TO BUDGET %", "CURRENT_SERVICE_REVENUE", "SERVICE_BUDGET"),
        ("RETAIL REVENUE TO BUDGET %", "CURRENT_RETAIL_REVENUE", "RETAIL_BUDGET"),
        ("TOTAL REVENUE TO BUDGET %", "CURRENT_TOTAL_REVENUE", "TOTAL_BUDGET"),
    ]
    for column in growth_rates:
        df[column[0]] = df[column[1]] / df[column[2]] * 100
        df[column[0]] = df[column[0]].apply(lambda x: f"{x:.1f}%")
    return df


def select_and_reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selects and reorders columns in the DataFrame.

    Parameters:
    - df: The DataFrame to process.
    - first_col: The column name to place as the first column (unique for each DataFrame).
    - common_columns: A list of column names to follow the first column (common across DataFrames).

    Returns:
    - Reordered DataFrame.
    """
    first_col = df.columns[0]
    common_columns = [
        # Current period
        "CURRENT_SERVICE_REVENUE",
        "CURRENT_RETAIL_REVENUE",
        "CURRENT_TOTAL_REVENUE",
        "% CURRENT REV CONTR",
        "CURRENT_STORE_COUNT",
        # Previous period
        "PREVIOUS_SERVICE_REVENUE",
        "PREVIOUS_RETAIL_REVENUE",
        "PREVIOUS_TOTAL_REVENUE",
        "% PREVIOUS REV CONTR",
        "PREVIOUS_STORE_COUNT",
        # Budget
        "SERVICE_BUDGET",
        "RETAIL_BUDGET",
        "TOTAL_BUDGET",
        "% TOTAL BUDGET",
        # Growth
        "SERVICES CURRENT TO PREVIOUS %",
        "RETAIL CURRENT TO PREVIOUS %",
        "TOTAL CURRENT TO PREVIOUS %",
        "SERVICES REVENUE TO BUDGET %",
        "RETAIL REVENUE TO BUDGET %",
        "TOTAL REVENUE TO BUDGET %",
    ]

    # Create a list of columns, starting with the first column and followed by the common columns
    columns_to_select = [first_col] + common_columns

    # Reorder the DataFrame by selecting only the specified columns
    reordered_df = df[columns_to_select]

    return reordered_df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function is used to rename the columns of the DataFrame.
    """
    renamed_df = df.rename(
        columns={
            "CURRENT_SERVICE_REVENUE": "SERVICE REVENUE CURRENT",
            "CURRENT_RETAIL_REVENUE": "RETAIL REVENUE CURRENT",
            "CURRENT_TOTAL_REVENUE": "TOTAL REVENUE CURRENT",
            "CURRENT_STORE_COUNT": "STORE COUNT CURRENT",
            "PREVIOUS_SERVICE_REVENUE": "SERVICE REVENUE PREVIOUS",
            "PREVIOUS_RETAIL_REVENUE": "RETAIL REVENUE PREVIOUS",
            "PREVIOUS_TOTAL_REVENUE": "TOTAL REVENUE PREVIOUS",
            "PREVIOUS_STORE_COUNT": "STORE COUNT PREVIOUS",
            "SERVICE_BUDGET": "SERVICE BUDGET",
            "RETAIL_BUDGET": "RETAIL BUDGET",
            "TOTAL_BUDGET": "TOTAL BUDGET",
        }
    )

    return renamed_df


def final_dataframes_dictionary(df: pd.DataFrame) -> dict:
    """
    This function is used to create the final dataframe with the contribution and growth columns.
    """
    dataframes_center_and_groupings = create_and_append_totals(df)

    for key, value in dataframes_center_and_groupings.items():
        # Process the dataframes with contribution, growth, and selection
        dataframes_center_and_groupings[key] = contribution_column(value)
        dataframes_center_and_groupings[key] = growth_column(
            dataframes_center_and_groupings[key]
        )
        dataframes_center_and_groupings[key] = select_and_reorder_columns(
            dataframes_center_and_groupings[key]
        )

        # Drop certain columns for specific dataframes
        if key in ["df_top_10", "df_icu", "df_new", "df_closed"]:
            dataframes_center_and_groupings[key] = dataframes_center_and_groupings[
                key
            ].drop(columns=["CURRENT_STORE_COUNT", "PREVIOUS_STORE_COUNT"])

        # Rename columns
        dataframes_center_and_groupings[key] = rename_columns(
            dataframes_center_and_groupings[key]
        )

        # Replace 'nan%' and 'inf%' with blank and also NaN with empty string
        dataframes_center_and_groupings[key] = dataframes_center_and_groupings[
            key
        ].replace(["nan%", "inf%"], "", regex=True)
        dataframes_center_and_groupings[key] = dataframes_center_and_groupings[
            key
        ].fillna("")
        
        # Apply number formatting to numeric columns (thousands separator, 0 decimal places)
        # Commented out to prevent returning Styler objects
        # dataframes_center_and_groupings[key] = dataframes_center_and_groupings[key].style.format(
        #     {
        #         col: "{:,.0f}"
        #         for col in dataframes_center_and_groupings[key]
        #         .select_dtypes(include=["float64", "int64"])
        #         .columns
        #     }
        # )
        
        # Format percentage columns for display
        dataframes_center_and_groupings[key] = format_percentage_columns(
            dataframes_center_and_groupings[key]
        )

    return dataframes_center_and_groupings


def format_percentage_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function formats percentage columns for proper display.
    """
    percentage_columns = ["% CURRENT REV CONTR", "% PREVIOUS REV CONTR", "% TOTAL BUDGET"]
    
    for col in percentage_columns:
        if col in df.columns:
            # Format as percentage strings for display, handling both numeric and string values
            def format_percentage(x):
                if pd.isna(x) or x == "":
                    return "0.0%"
                elif isinstance(x, str) and x.endswith('%'):
                    return x  # Already formatted
                elif isinstance(x, (int, float)):
                    return f"{x:.1f}%"
                else:
                    try:
                        # Try to convert to float and format
                        return f"{float(x):.1f}%"
                    except (ValueError, TypeError):
                        return "0.0%"
            
            df[col] = df[col].apply(format_percentage)
    
    return df
