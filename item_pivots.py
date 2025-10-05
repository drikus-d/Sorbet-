"""
This module contains functions for creating and
manipulating dataframes for the items. This is the top 20
retail and service items by revenue and the bottom 10 and
group totals.
"""

from typing import Literal
import pandas as pd
import config
import utils as ut


def base_items_with_loyalty(
    session,
    start_date: str,
    end_date: str,
    item_type: Literal["retail", "service"],
    day_package_filter_out: bool = None,
):
    """
    This function dynamically includes the 'is_day_package' and 'is_service' filters
    based on the 'item_type' and 'day_package_filter' parameters.
    """
    if item_type not in ["retail", "service"]:
        raise ValueError("item_type must be either 'retail' or 'service'")

    # Read the base query template
    items_base_query = ut.read_sql_query(config.ITEMS_WITH_LOYALTY_PATH)

    # Construct parameters based on item_type
    params_brand = {
        "start_date": start_date,
        "end_date": end_date,
        "item_group": "item_category" if item_type == "retail" else "item_sub_category",
    }

    # Determine the is_service_filter
    is_service_filter = (
        "r.is_service = true" if item_type == "service" else "r.is_service = false"
    )

    # Conditionally add the is_day_package filter
    if day_package_filter_out:
        day_package_condition = "is_day_package = false"
    else:
        day_package_condition = "1=1"  # No filtering if not provided

    # Replace placeholders in SQL query with actual values
    modified_query = items_base_query.format(
        start_date=params_brand["start_date"],
        end_date=params_brand["end_date"],
        item_group=params_brand["item_group"],
        is_service_filter=is_service_filter,  # Include the dynamic is_service filter
        day_package_condition=day_package_condition,  # Include the dynamic day_package condition
    )

    # Load data
    df = ut.load_data(session, modified_query)
    # Convert relevant columns to numeric

    list_to_convert_to_numric = [
        "CURRENT_TOTAL_REVENUE",
        "PREVIOUS_TOTAL_REVENUE",
        "CURRENT_TOTAL_UNITS",
        "PREVIOUS_TOTAL_UNITS",
    ]

    for col in list_to_convert_to_numric:
        if col in df.columns:  # Check if the column exists in the DataFrame
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            )  # Converts to float64 or NaN if conversion fails

    # Sort by total current revenue
    return df


def groupings_items_with_loyalty(
    df: pd.DataFrame, order_by: str = "CURRENT_TOTAL_REVENUE"
):
    """
    This function groups the dataframe by category and center and calculates the totals.
    """
    df_grouped = (
        df.groupby("CATEGORY")
        .agg(
            {
                "CURRENT_TOTAL_REVENUE": "sum",
                "PREVIOUS_TOTAL_REVENUE": "sum",
                "CURRENT_TOTAL_UNITS": "sum",
                "PREVIOUS_TOTAL_UNITS": "sum",
                "CURRENT_CENTER": "nunique",
                "PREVIOUS_CENTER": "nunique",
            }
        )
        .reset_index()
    )
    df_grouped.sort_values(by=order_by, ascending=False, inplace=True)
    if order_by == "CURRENT_TOTAL_REVENUE":
        df_grouped_exclude_missing = df_grouped[df_grouped["CURRENT_TOTAL_UNITS"] > 0]
    else:
        df_grouped_exclude_missing = df_grouped[df_grouped[order_by] > 0]
    return df_grouped_exclude_missing


# Get the sum of numeric columns
def get_item_total_row(df_grouped: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """
    This function sums all numeric columns in the DataFrame and
    returns the result as a single-row DataFrame.
    """
    # Sum all numeric columns
    total_row = (
        df_grouped.select_dtypes(include=["number"]).sum(numeric_only=True).round(0)
    )

    # Add a label for the 'group_by' column (assuming it's the first column)
    total_row[df_grouped.columns[0]] = "Total"

    # Convert the Series to a DataFrame
    total_row = pd.DataFrame([total_row], columns=df_grouped.columns)
    category_list = df_grouped["CATEGORY"].unique().tolist()
    total_row["CURRENT_CENTER"] = df[df["CATEGORY"].isin(category_list)][
        "CURRENT_CENTER"
    ].nunique()
    total_row["PREVIOUS_CENTER"] = df[df["CATEGORY"].isin(category_list)][
        "PREVIOUS_CENTER"
    ].nunique()

    return total_row


def append_group_and_total(
    df: pd.DataFrame,
    head_or_tail: str,
    order_by: str = "CURRENT_TOTAL_REVENUE",
    limit: int = None,
) -> pd.DataFrame:
    """
    This function groups the dataframe by category and center and calculates the totals.
    """
    # Call the function and pass the arguments
    grouped_df = groupings_items_with_loyalty(df, order_by)

    # Apply the head or tail function based on the argument
    if limit:
        if head_or_tail == "head":
            grouped_df = grouped_df.head(limit)
        elif head_or_tail == "tail":
            grouped_df = grouped_df.tail(limit)

    # Create a total row and concatenate it with the dataframe
    total_row = get_item_total_row(grouped_df, df)
    final_df = pd.concat([grouped_df, total_row], ignore_index=True)

    return final_df


def item_contribution_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function calculates the contribution of each row in a group_by column
    (e.g., brand) to the total of the target column (e.g., total revenue).
    """
    list_of_columns = [
        ("% CURRENT REV CONTR", "CURRENT_TOTAL_REVENUE"),
        ("% PREVIOUS REV CONTR", "PREVIOUS_TOTAL_REVENUE"),
        ("% CURRENT UNITS CONTR", "CURRENT_TOTAL_UNITS"),
        ("% PREVIOUS UNITS CONTR", "PREVIOUS_TOTAL_UNITS"),
    ]
    # Calculate the contribution for each brand as a percentage of the total revenue
    for column in list_of_columns:
        # get first column of the datafram
        total = df.loc[df.iloc[:, 0] == "Total", column[1]].values[0]
        df[column[0]] = df[column[1]] / total * 100
        df[column[0]] = df[column[0]].apply(lambda x: f"{x:.1f}%")
    # Display the result
    return df


def item_growth_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function calculates the growth of each row
    in a group_by column (e.g., brand) to the previous period.
    """
    df["AVG REVENUE PER STORE"] = df["CURRENT_TOTAL_REVENUE"] / df["CURRENT_CENTER"]
    df["AVG REVENUE PER STORE PREVIOUS"] = (
        df["PREVIOUS_TOTAL_REVENUE"] / df["PREVIOUS_CENTER"]
    )
    # Tuple for growth rates
    growth_rates = [
        (
            "RAND CURRENT TO PREVIOUS %",
            "CURRENT_TOTAL_REVENUE",
            "PREVIOUS_TOTAL_REVENUE",
        ),
        ("UNITS CURRENT TO PREVIOUS%", "CURRENT_TOTAL_UNITS", "PREVIOUS_TOTAL_UNITS"),
        (
            "AVERAGE REVENUE GROWTH PER STORE %",
            "AVG REVENUE PER STORE",
            "AVG REVENUE PER STORE PREVIOUS",
        ),
    ]
    for column in growth_rates:
        df[column[0]] = (df[column[1]] / df[column[2]] - 1) * 100
        # Replace inf, -inf, and NaN values with 0,
        # before applying percentage formatting
        df[column[0]].replace([float("inf"), -float("inf")], None, inplace=True)
        df[column[0]].replace(
            [pd.NA, None], "", inplace=True
        )  # Replace None or pd.NA with an empty string
        df[column[0]] = df[column[0]].apply(lambda x: f"{x:.1f}%" if x != "" else "")
    df.drop(
        columns=["AVG REVENUE PER STORE", "AVG REVENUE PER STORE PREVIOUS"],
        inplace=True,
    )
    return df


def rename_items_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function is used to rename the columns of the DataFrame.
    """
    renamed_df = df.rename(
        columns={
            "CURRENT_TOTAL_REVENUE": "TOTAL REVENUE CURRENT",
            "PREVIOUS_TOTAL_REVENUE": "TOTAL REVENUE PREVIOUS",
            "CURRENT_TOTAL_UNITS": "TOTAL UNITS CURRENT",
            "PREVIOUS_TOTAL_UNITS": "TOTAL UNITS PREVIOUS",
            "CURRENT_CENTER": "STORE COUNT CURRENT",
            "PREVIOUS_CENTER": "STORE COUNT PREVIOUS",
        }
    )

    return renamed_df


def final_items_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function is used to create the final dataframe with the contribution and growth columns.
    """
    df = item_contribution_column(df)
    df = item_growth_column(df)
    df = rename_items_columns(df)
    return df


def final_item_df_dictionary(
    df_service: pd.DataFrame,
    df_retail: pd.DataFrame,
) -> dict:
    """
    This function is used to create the final dataframe with the contribution and growth columns,
    and cleans percentage columns from inf% and nan% values.
    """
    df_service_top_20 = append_group_and_total(
        df_service, head_or_tail="head", limit=20
    )
    df_service_bottom_10 = append_group_and_total(
        df_service, head_or_tail="tail", limit=10
    )
    df_retail_top_20 = append_group_and_total(df_retail, head_or_tail="head", limit=20)
    df_retail_bottom_10 = append_group_and_total(
        df_retail, head_or_tail="tail", limit=10
    )

    # Make a dictionary of the above dataframes
    final_items_dictionary = {
        "service_top_20": df_service_top_20,
        "service_bottom_10": df_service_bottom_10,
        "retail_top_20": df_retail_top_20,
        "retail_bottom_10": df_retail_bottom_10,
    }

    for key, value in final_items_dictionary.items():
        final_items_dictionary[key] = final_items_dataframe(value)
    return final_items_dictionary


def get_total_lines_dataframe(
    df: pd.DataFrame, df_with_day_package: pd.DataFrame = None
) -> pd.DataFrame:
    '''
    This function calculates the total lines for the top 20 items
    and the total revenue and units for the current and previous year.
    Output is a single line dataframe with the totals and percentage comparisions.
    '''
    if df_with_day_package is None:
        df_with_day_package = df

    total_revenue_current_year = df_with_day_package["CURRENT_TOTAL_REVENUE"].sum()
    total_revenue_previous_year = df_with_day_package["PREVIOUS_TOTAL_REVENUE"].sum()
    total_units_current_year = df_with_day_package["CURRENT_TOTAL_UNITS"].sum()
    total_units_previous_year = df_with_day_package["PREVIOUS_TOTAL_UNITS"].sum()

    top_20_current_revenue = append_group_and_total(df, head_or_tail="head", limit=20)
    top_20_current_revenue_sum = top_20_current_revenue[
        top_20_current_revenue.iloc[:, 0] == "Total"
    ]["CURRENT_TOTAL_REVENUE"].values[0]
    top_20_previous_revenue = append_group_and_total(
        df_with_day_package,
        head_or_tail="head",
        limit=20,
        order_by="PREVIOUS_TOTAL_REVENUE",
    )
    top_20_previous_revenue_sum = top_20_previous_revenue[
        top_20_previous_revenue.iloc[:, 0] == "Total"
    ]["PREVIOUS_TOTAL_REVENUE"].values[0]
    top_20_current_units = append_group_and_total(
        df, head_or_tail="head", limit=20, order_by="CURRENT_TOTAL_UNITS"
    )
    top_20_current_units_sum = top_20_current_units[
        top_20_current_units.iloc[:, 0] == "Total"
    ]["CURRENT_TOTAL_UNITS"].values[0]
    top_20_previous_units = append_group_and_total(
        df_with_day_package,
        head_or_tail="head",
        limit=20,
        order_by="PREVIOUS_TOTAL_UNITS",
    )
    top_20_previous_units_sum = top_20_previous_units[
        top_20_previous_units.iloc[:, 0] == "Total"
    ]["PREVIOUS_TOTAL_UNITS"].values[0]

    top_20_current_revenue_over_total = (
        top_20_current_revenue_sum / total_revenue_current_year
    )
    top_20_previous_revenue_over_total = (
        top_20_previous_revenue_sum / total_revenue_previous_year
    )
    top_20_current_units_over_total = (
        top_20_current_units_sum / total_units_current_year
    )
    top_20_previous_units_over_total = (
        top_20_previous_units_sum / total_units_previous_year
    )

    dataframe_totals = pd.DataFrame(
        [
            {
                "TOTAL REVENUE CURRENT": total_revenue_current_year.round(0),
                "TOTAL REVENUE PREVIOUS": total_revenue_previous_year.round(0),
                "TOTAL UNITS CURRENT": total_units_current_year.round(0),
                "TOTAL UNITS PREVIOUS": total_units_previous_year.round(0),
                "TOP 20 CURRENT REVENUE OVER TOTAL %": 
                    f"{top_20_current_revenue_over_total * 100:.1f}%",
                "TOP 20 PREVIOUS REVENUE OVER TOTAL %": 
                    f"{top_20_previous_revenue_over_total * 100:.1f}%",
                "TOP 20 CURRENT UNITS OVER TOTAL %": 
                    f"{top_20_current_units_over_total * 100:.1f}%",
                "TOP 20 PREVIOUS UNITS OVER TOTAL %": 
                    f"{top_20_previous_units_over_total * 100:.1f}%",
            }
        ]
    )

    return dataframe_totals


def get_item_base_dataframes(session, start_date: str, end_date: str) -> dict:
    """
    This function returns the service and retail dataframes with and without the day package.
    """
    df_service = base_items_with_loyalty(session, start_date, end_date, "service", True)
    df_service_include_day_package = base_items_with_loyalty(
        session, start_date, end_date, "service", False
    )
    df_retail = base_items_with_loyalty(session, start_date, end_date, "retail", True)
    return df_service, df_service_include_day_package, df_retail
