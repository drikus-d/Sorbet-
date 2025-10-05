# clicks_scorecard_weekly_clean.py - Clean version with Daily Sales

import streamlit as st
import database_utils as dut
import utils as ut
import pandas as pd
import excel_format as ef
import config
import os
import smtplib
import logging

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Configure Streamlit page
st.set_page_config(
    page_title="Clicks Weekly Scorecard - Summary",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Set pandas display options
pd.set_option("display.float_format", lambda x: f"{x:,.0f}")

def main():
    """
    Main function to run the Clicks Scorecard Streamlit app.
    """
    # Establish Snowflake session
    try:
        session = ut.get_snowflake_session()
    except Exception as e:
        st.error(f"Failed to establish Snowflake session: {e}")
        st.stop()

    # Title of the app
    st.title("📈 Clicks Weekly Scorecard - Summary")

    # Date range selection
    run_date = st.date_input(
        "Run Date:",
        value=datetime.today().date(),
        min_value=None,
        max_value=None
    )

    run_date = pd.Timestamp(run_date)

    # Initialize session state variables
    if "all_dataframes" not in st.session_state:
        st.session_state.all_dataframes = []
    if "subheaders" not in st.session_state:
        st.session_state.subheaders = []
    if "excel_data" not in st.session_state:
        st.session_state.excel_data = None

    # Button to generate and display the scorecard
    if st.button("🔍 Generate Scorecard"):
        with st.spinner("Generating scorecard..."):
            # Initialize lists to hold DataFrames and their corresponding subheaders
            all_dataframes = []
            subheaders = []

            # Set the date parameters used in the run
            today = run_date
            end_date = today - pd.Timedelta(days=1)

            # The week start is the previous monday
            day_of_week = end_date.weekday()  # Monday is 0, Sunday is 6
            days_to_subtract = (day_of_week + 7 - 0) % 7 + 1
            wtd_start_date = end_date - pd.Timedelta(days=days_to_subtract)

            # Determine the start date for the year-to-date report
            if end_date.month > 9 or (end_date.month == 9 and end_date.day > 1):
                ytd_start_date = pd.to_datetime(f"{end_date.year}-09-01")
            else:
                ytd_start_date = pd.to_datetime(f"{end_date.year - 1}-09-01")

            ytd_start_date = ytd_start_date - pd.Timedelta(days=ytd_start_date.weekday())
            fin_end_date = ytd_start_date + pd.Timedelta(weeks=52)

            # Work out the month start date based on a 454 trade calendar
            pattern = [4, 5, 4, 4, 5, 4, 4, 5, 4, 4, 5, 4]
            if (fin_end_date.weekday() == ytd_start_date.weekday()):
                pattern[-1] += 1

            month_starts = []
            current = ytd_start_date
            for weeks in pattern:
                month_starts.append(current)
                current += pd.Timedelta(weeks=weeks)

            for i, month in enumerate(month_starts):
                month_end = (
                    month_starts[i + 1]
                    if i + 1 < len(month_starts)
                    else month_starts[i] + pd.Timedelta(weeks=pattern[i])
                )
                if month <= end_date < month_end:
                    mtd_start_date = month
                    break

            # Total Business
            try:
                df = generate_df(session,"TOTAL_STORE_STATS_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
                subheader = "Total Business"
                if df is not None and not df.empty:
                    st.subheader(subheader)
                    st.dataframe(df)
                    all_dataframes.append(df)
                    subheaders.append(subheader)
                else:
                    st.warning(f"No data available for '{subheader}'.")
                    all_dataframes.append(pd.DataFrame())
                    subheaders.append(subheader)
            except Exception as e:
                st.error(f"Error in Total Business: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Total Business (Error)")

            # Corporate Stores Only
            try:
                df = generate_df(session,"CORPORATE_STORE_STATS_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
                subheader = "Corporate Stores Only"
                if df is not None and not df.empty:
                    st.subheader(subheader)
                    st.dataframe(df)
                    all_dataframes.append(df)
                    subheaders.append(subheader)
                else:
                    st.warning(f"No data available for '{subheader}'.")
                    all_dataframes.append(pd.DataFrame())
                    subheaders.append(subheader)
            except Exception as e:
                st.error(f"Error in Corporate Stores: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Corporate Stores Only (Error)")

            # Service Top 20 Items
            try:
                df = generate_df(session,"ITEM_SERVICE_TOP_20",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
                subheader = "Service Top 20 Items"
                if df is not None and not df.empty:
                    st.subheader(subheader)
                    st.dataframe(df)
                    all_dataframes.append(df)
                    subheaders.append(subheader)
                else:
                    st.warning(f"No data available for '{subheader}'.")
                    all_dataframes.append(pd.DataFrame())
                    subheaders.append(subheader)
            except Exception as e:
                st.error(f"Error in Service Top 20: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Service Top 20 Items (Error)")

            # Service Total
            try:
                df = generate_df(session,"ITEM_SERVICE_TOTAL",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
                subheader = "Total Service Items"
                if df is not None and not df.empty:
                    st.subheader(subheader)
                    st.dataframe(df)
                    all_dataframes.append(df)
                    subheaders.append(subheader)
                else:
                    st.warning(f"No data available for '{subheader}'.")
                    all_dataframes.append(pd.DataFrame())
                    subheaders.append(subheader)
            except Exception as e:
                st.error(f"Error in Service Total: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Total Service Items (Error)")

            # Retail Top 20 Items
            try:
                df = generate_df(session,"ITEM_RETAIL_TOP_20",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
                subheader = "Retail Top 20 Items"
                if df is not None and not df.empty:
                    st.subheader(subheader)
                    st.dataframe(df)
                    all_dataframes.append(df)
                    subheaders.append(subheader)
                else:
                    st.warning(f"No data available for '{subheader}'.")
                    all_dataframes.append(pd.DataFrame())
                    subheaders.append(subheader)
            except Exception as e:
                st.error(f"Error in Retail Top 20: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Retail Top 20 Items (Error)")

            # Daily Sales Last Week - The main focus!
            try:
                import daily_sales as ds
                
                # Use the same date range as the rest of the report
                daily_start_date = wtd_start_date.strftime(config.DATE_FORMAT)
                daily_end_date = end_date.strftime(config.DATE_FORMAT)
                
                st.write(f"🔍 DEBUG: Calling daily_sales_table with start_date={daily_start_date}, end_date={daily_end_date}")
                
                df = ds.daily_sales_table(session, daily_start_date, daily_end_date)
                
                # Add summary rows
                if not df.empty:
                    df = ds.daily_sales_summary_rows(df)
                    # Format the display for better presentation
                    df_display = ds.format_daily_sales_display(df)
                
                # Get week number for title (fiscal year starting Sept 1)
                fiscal_year_start = pd.to_datetime(f"{end_date.year}-09-01")
                
                # Calculate weeks since fiscal year start
                days_since_fiscal_start = (wtd_start_date - fiscal_year_start).days
                week_number = (days_since_fiscal_start // 7) + 1
                
                # Add header and values for excel export
                subheader = f"Daily Sales Last Week (Week {week_number})"
                
                st.write(f"🔍 DEBUG: Daily sales DataFrame shape: {df.shape if df is not None else 'None'}")
                
                if df is not None and not df.empty:
                    st.subheader(subheader)
                    # Display the formatted version for better readability
                    st.dataframe(df_display, width='stretch')
                    # Use the original df for Excel export (with numeric values)
                    all_dataframes.append(df)
                    subheaders.append(subheader)
                    st.write(f"✅ Daily Sales table added to Excel export")
                else:
                    st.warning(f"No data available for '{subheader}'.")
                    all_dataframes.append(pd.DataFrame())
                    subheaders.append(subheader)
                    st.write(f"❌ Daily Sales table is empty")
                    
            except Exception as e:
                st.error(f"Error in Daily Sales section: {str(e)}")
                st.write("Skipping Daily Sales due to error...")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Daily Sales Last Week (Error)")
                st.write(f"❌ DEBUG: Daily Sales failed with error: {str(e)}")

            # Update session state
            st.session_state.all_dataframes = all_dataframes
            st.session_state.subheaders = subheaders
            
            # Generate the Excel file using the template
            try:
                formatted_start_date = wtd_start_date.strftime(config.DATE_FORMAT)
                formatted_end_date = end_date.strftime(config.DATE_FORMAT)

                combined_excel_data = ef.export_combined_excel_from_template(
                    all_dataframes=all_dataframes,
                    subheaders=subheaders,
                    start_date=formatted_start_date,
                    end_date=formatted_end_date,
                    template_path="clicks_scorecard_template.xlsx",
                )
                
                if combined_excel_data:
                    st.session_state.excel_data = combined_excel_data
                    st.success("✅ Excel file generated successfully!")
                else:
                    st.error("❌ Excel file generation returned empty data.")
            except Exception as e:
                st.error(f"An error occurred while generating the Excel file: {e}")
                st.session_state.excel_data = None

    # After generating, show the download button if Excel data is available
    if "excel_data" in st.session_state and st.session_state.excel_data:
        st.subheader("📤 Export to Formatted Excel")
        st.download_button(
            label="📥 Download Formatted Excel",
            data=st.session_state.excel_data,
            file_name="clicks_scorecard_weekly_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.success("✅ Formatted Excel file is ready for download!")
    else:
        st.info("🔄 Please generate the scorecard to enable the download button.")

def generate_df(session, table_name: str, end_date, wtd_start_date, mtd_start_date, ytd_start_date):
    try:
        query = ut.read_sql_query(config.FILE_PATHS[table_name])
        params = {
            "end_date": end_date.strftime(config.DATE_FORMAT),
            "wtd_start_date": wtd_start_date.strftime(config.DATE_FORMAT),
            "mtd_start_date": mtd_start_date.strftime(config.DATE_FORMAT),
            "ytd_start_date": ytd_start_date.strftime(config.DATE_FORMAT)
        }
        results_df = dut.execute_query(session, query, params)
        if results_df.empty:
            return None
        return results_df
    except Exception as e:
        st.error(f"Error in generate_df for {table_name}: {str(e)}")
        return None

if __name__ == "__main__":
    main()
