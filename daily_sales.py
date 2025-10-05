"""
This is the daily sales module.
"""

import config
import pandas as pd
import utils as ut


def daily_sales_data(session, start_date: str, end_date: str):
    """
    This function is used to get the daily sales data.
    """
    try:
        import database_utils as dut
        query = ut.read_sql_query(config.FILE_PATHS["DAILY_SALES_PATH"])
        
        # Use the same parameter approach as other functions
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        # Execute the query with parameters
        df = dut.execute_query(session, query, params)
        
        return df
    except Exception as e:
        print(f"Error in daily_sales_data: {str(e)}")
        return pd.DataFrame()


def daily_sales_table(session, start_date: str, end_date: str):
    """
    This function is used to create the daily sales table.
    """
    try:
        df = daily_sales_data(session, start_date, end_date)
        
        if df.empty:
            print("DEBUG: DataFrame is empty!")
            return pd.DataFrame()
        
        # Debug: Print what we actually got
        print(f"DEBUG: DataFrame columns: {df.columns.tolist()}")
        print(f"DEBUG: DataFrame shape: {df.shape}")
        print(f"DEBUG: DataFrame head:\n{df.head()}")
        print(f"DEBUG: All dates in DataFrame: {df['DATES_CY'].tolist()}")
        print(f"DEBUG: All days in DataFrame: {df['DAY_NAME'].tolist()}")
        
        # CRITICAL FIX: Sort by date to ensure proper chronological order
        df['DATES_CY'] = pd.to_datetime(df['DATES_CY'])
        df = df.sort_values('DATES_CY').reset_index(drop=True)
        
        # CRITICAL FIX: Calculate correct day names using Python
        df['DAY_NAME'] = df['DATES_CY'].dt.day_name()
        
        # Create the formatted sales column with just day names (no day numbers)
        df['SALES'] = df['DAY_NAME']
        
        # Ensure numeric columns are numeric
        df['SALES_TY'] = df['SALES_TY'].astype(float)
        df['SALES_LY'] = df['SALES_LY'].astype(float)
        df['SALES_BUDGET'] = df['SALES_BUDGET'].astype(float)
        
        # Calculate growth percentage (Current vs Last Year) - store as decimal
        df['GROWTH_PCT'] = ((df['SALES_TY'] - df['SALES_LY']) / df['SALES_LY']).fillna(0)
        
        # Calculate budget variance percentage (Current vs Budget) - store as decimal
        # Positive = over budget, Negative = under budget
        df['BUDGET_PCT'] = ((df['SALES_TY'] - df['SALES_BUDGET']) / df['SALES_BUDGET']).fillna(0)
        
        # Format dates properly (already converted to datetime above)
        df['DATES_CY'] = df['DATES_CY'].dt.strftime('%Y-%m-%d')
        
        # Reorder columns to match expected format
        df = df[['SALES', 'DATES_CY', 'SALES_TY', 'SALES_LY', 'SALES_BUDGET', 'GROWTH_PCT', 'BUDGET_PCT']]
        
        return df
    except Exception as e:
        print(f"Error in daily_sales_table: {str(e)}")
        return pd.DataFrame()


def daily_sales_summary_rows(df: pd.DataFrame):
    """
    This function adds summary rows to the daily sales table.
    """
    if df.empty:
        return df
    
    # Calculate totals
    total_ty = df['SALES_TY'].sum()
    total_ly = df['SALES_LY'].sum()
    total_budget = df['SALES_BUDGET'].sum()
    
    # Debug: Check data types and values
    print(f"DEBUG Data Types: TY={type(df['SALES_TY'].iloc[0])}, LY={type(df['SALES_LY'].iloc[0])}")
    print(f"DEBUG Sample Values: TY={df['SALES_TY'].iloc[0]}, LY={df['SALES_LY'].iloc[0]}")
    
    # Calculate weekend totals (Friday, Saturday, Sunday)
    weekend_df = df[df['SALES'].str.contains('Friday|Saturday|Sunday', na=False)]
    weekend_ty = weekend_df['SALES_TY'].sum()
    weekend_ly = weekend_df['SALES_LY'].sum()
    weekend_budget = weekend_df['SALES_BUDGET'].sum()
    
    # Calculate averages
    avg_ty = total_ty / len(df)
    avg_ly = total_ly / len(df)
    avg_budget = total_budget / len(df)
    
    # Calculate percentages as decimals (0.173 for 17.3%)
    total_growth = ((total_ty - total_ly) / total_ly) if total_ly > 0 else 0
    total_budget_pct = ((total_ty - total_budget) / total_budget) if total_budget > 0 else 0
    
    # Debug output for Total row calculations
    print(f"DEBUG Total Row: TY={total_ty}, LY={total_ly}, Budget={total_budget}")
    print(f"DEBUG Total Row: Growth={total_growth}, Budget_PCT={total_budget_pct}")
    
    weekend_growth = ((weekend_ty - weekend_ly) / weekend_ly) if weekend_ly > 0 else 0
    weekend_budget_pct = ((weekend_ty - weekend_budget) / weekend_budget) if weekend_budget > 0 else 0
    
    avg_growth = ((avg_ty - avg_ly) / avg_ly) if avg_ly > 0 else 0
    avg_budget_pct = ((avg_ty - avg_budget) / avg_budget) if avg_budget > 0 else 0
    
    # Store growth percentages in variables early (before any formatting)
    total_growth_decimal = total_growth
    weekend_growth_decimal = weekend_growth  
    avg_growth_decimal = avg_growth
    
    # Create summary rows with proper formatting (following Clicks Loyalty KPI pattern)
    summary_rows = [
        {
            'SALES': 'Total',
            'DATES_CY': pd.NaT,
            'SALES_TY': total_ty,  # Store as number for proper formatting
            'SALES_LY': total_ly,  # Store as number for proper formatting
            'SALES_BUDGET': total_budget,  # Store as number for proper formatting
            'GROWTH_PCT': total_growth_decimal,  # Store as decimal for proper formatting
            'BUDGET_PCT': total_budget_pct  # Store as decimal for proper formatting
        },
        {
            'SALES': 'Weekend trading (Fri/Sat/Sun)',
            'DATES_CY': pd.NaT,
            'SALES_TY': weekend_ty,  # Store as number for proper formatting
            'SALES_LY': weekend_ly,  # Store as number for proper formatting
            'SALES_BUDGET': weekend_budget,  # Store as number for proper formatting
            'GROWTH_PCT': weekend_growth_decimal,  # Store as decimal for proper formatting
            'BUDGET_PCT': weekend_budget_pct  # Store as decimal for proper formatting
        },
        {
            'SALES': 'AVG Sales',
            'DATES_CY': pd.NaT,
            'SALES_TY': avg_ty,  # Store as number for proper formatting
            'SALES_LY': avg_ly,  # Store as number for proper formatting
            'SALES_BUDGET': avg_budget,  # Store as number for proper formatting
            'GROWTH_PCT': avg_growth_decimal,  # Store as decimal for proper formatting
            'BUDGET_PCT': avg_budget_pct  # Store as decimal for proper formatting
        }
    ]
    
    # Convert to DataFrame and append
    summary_df = pd.DataFrame(summary_rows)
    
    result_df = pd.concat([df, summary_df], ignore_index=True)
    
    return result_df


def format_daily_sales_display(df: pd.DataFrame):
    """
    This function formats the daily sales table for better display.
    Following the same pattern as Clicks Loyalty KPI for consistency.
    """
    if df.empty:
        return df
    
    # Create a copy to avoid modifying the original
    formatted_df = df.copy()
    
    # Debug: Check Total row values before formatting
    total_row_before = formatted_df[formatted_df['SALES'] == 'Total']
    if not total_row_before.empty:
        print(f"DEBUG Before Formatting - Total row GROWTH_PCT: {total_row_before['GROWTH_PCT'].iloc[0]} (type: {type(total_row_before['GROWTH_PCT'].iloc[0])})")
        print(f"DEBUG Before Formatting - Total row BUDGET_PCT: {total_row_before['BUDGET_PCT'].iloc[0]} (type: {type(total_row_before['BUDGET_PCT'].iloc[0])})")
    
    # 1. CENTER ALIGN DATES: Format DATES_CY column (center alignment handled in Streamlit display)
    # Keep dates as strings for proper display
    
    # 2. FORMAT NUMBERS: Daily rows vs Summary rows (following Clicks Loyalty KPI pattern)
    daily_mask = ~formatted_df['SALES'].isin(['Total', 'Weekend trading (Fri/Sat/Sun)', 'AVG Sales'])
    summary_mask = formatted_df['SALES'].isin(['Total', 'Weekend trading (Fri/Sat/Sun)', 'AVG Sales'])
    
    # Convert numeric columns to object type to avoid dtype warnings
    numeric_columns = ['SALES_TY', 'SALES_LY', 'SALES_BUDGET']
    for col in numeric_columns:
        formatted_df[col] = formatted_df[col].astype(object)
    
    # Daily rows: format with spaces as thousand separators and 2 decimals
    formatted_df.loc[daily_mask, 'SALES_TY'] = formatted_df.loc[daily_mask, 'SALES_TY'].apply(lambda x: f"{x:,.2f}".replace(',', ' ') if pd.notna(x) else "0.00")
    formatted_df.loc[daily_mask, 'SALES_LY'] = formatted_df.loc[daily_mask, 'SALES_LY'].apply(lambda x: f"{x:,.2f}".replace(',', ' ') if pd.notna(x) else "0.00")
    formatted_df.loc[daily_mask, 'SALES_BUDGET'] = formatted_df.loc[daily_mask, 'SALES_BUDGET'].apply(lambda x: f"{x:,.2f}".replace(',', ' ') if pd.notna(x) else "0.00")
    
    # Summary rows: format with spaces as thousand separators and NO decimals (like everywhere else)
    formatted_df.loc[summary_mask, 'SALES_TY'] = formatted_df.loc[summary_mask, 'SALES_TY'].apply(lambda x: f"{x:,.0f}".replace(',', ' ') if pd.notna(x) else "0")
    formatted_df.loc[summary_mask, 'SALES_LY'] = formatted_df.loc[summary_mask, 'SALES_LY'].apply(lambda x: f"{x:,.0f}".replace(',', ' ') if pd.notna(x) else "0")
    formatted_df.loc[summary_mask, 'SALES_BUDGET'] = formatted_df.loc[summary_mask, 'SALES_BUDGET'].apply(lambda x: f"{x:,.0f}".replace(',', ' ') if pd.notna(x) else "0")
    
    # 3. FORMAT PERCENTAGES: Following Clicks Loyalty KPI pattern
    percentage_columns = ['GROWTH_PCT', 'BUDGET_PCT']
    
    # Convert to numeric first
    for col in percentage_columns:
        formatted_df[col] = pd.to_numeric(formatted_df[col], errors='coerce')
    
    # Convert percentage columns to object type to avoid dtype warnings
    for col in percentage_columns:
        formatted_df[col] = formatted_df[col].astype(object)
    
    # Store raw decimals for Excel (Excel will handle the formatting)
    for col in percentage_columns:
        formatted_df[f'{col}_RAW'] = formatted_df[col]
    
    # Format percentages for Streamlit display (following Clicks Loyalty KPI pattern)
    for col in percentage_columns:
        # Daily rows: format as percentages
        formatted_df.loc[daily_mask, col] = formatted_df.loc[daily_mask, col].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "0.0%")
        # Summary rows: format as percentages (same as daily rows)
        formatted_df.loc[summary_mask, col] = formatted_df.loc[summary_mask, col].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "0.0%")
    
    # Debug: Check Total row values after formatting
    total_row = formatted_df[formatted_df['SALES'] == 'Total']
    if not total_row.empty:
        print(f"DEBUG After Formatting - Total row GROWTH_PCT: {total_row['GROWTH_PCT'].iloc[0]}")
        print(f"DEBUG After Formatting - Total row BUDGET_PCT: {total_row['BUDGET_PCT'].iloc[0]}")
    
    # Handle NaT dates in summary rows
    formatted_df['DATES_CY'] = formatted_df['DATES_CY'].apply(
        lambda x: "" if pd.isna(x) or x == "" else str(x)
    )
    
    return formatted_df