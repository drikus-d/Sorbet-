# clicks_scorecard_weekly.py

import streamlit as st
import center_pivots as cp
# import item_pivots as ip
# import loyalty_kpi_main as lp  # This module doesn't exist, using clicks_loyalty_kpi instead
import loyalty_kpi_pivot as lp
import clicks_loyalty_kpi as clp
# import ops_kpi as op
import database_utils as dut
import utils as ut
import pandas as pd
import excel_format as ef
import config  # Importing the configuration file
import date_utils as du

# Display clean banner at the top
st.info("📅 **Weekly Performance (2025-09-22 to 2025-09-28)**")  # Dynamic date utilities
# import rename_columns as rc
# import io
import os  # Ensure os is imported
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
pd.set_option("display.float_format", lambda x: f"{x:,.0f}")  # Adjust as needed

def main():
    """
    Main function to run the Clicks Scorecard Streamlit app.
    """
    # Dynamic date system is now active
    
    # Establish Snowflake session (assuming utils.get_snowflake_session is defined and retrieves config internally)
    try:
        session = ut.get_snowflake_session()
        if session is None:
            st.error("Snowflake session is None - check your configuration and dependencies")
            st.stop()
        st.success("✅ Snowflake session established successfully!")
    except Exception as e:
        st.error(f"Failed to establish Snowflake session: {e}")
        st.stop()

    # Title of the app
    st.title("📈 Clicks Weekly Scorecard - Summary")

    # Date range selection (assuming utils.date_range_selection is defined)
    # start_date, end_date = ut.date_range_selection()
    run_date = st.date_input(
        "Run Date:",
        value=datetime.today().date(), # Default to the current date
        min_value=None,  # No minimum date restriction
        max_value=None   # Removed max_value to allow any date selection
    )

    run_date = pd.Timestamp(run_date)

    # Initialize session state variables
    if "all_dataframes" not in st.session_state:
        st.session_state.all_dataframes = []
    if "subheaders" not in st.session_state:
        st.session_state.subheaders = []
    if "excel_data" not in st.session_state:
        st.session_state.excel_data = None
    if "formatted_start_date" not in st.session_state:
        st.session_state.formatted_start_date = ""
    if "formatted_end_date" not in st.session_state:
        st.session_state.formatted_end_date = ""

    # Button to generate and display the scorecard
    if st.button("🔍 Generate Scorecard"):
        with st.spinner("Generating scorecard..."):
            # Initialize lists to hold DataFrames and their corresponding subheaders
            all_dataframes = []
            subheaders = []

            # DYNAMIC DATE CALCULATION: Get all report dates dynamically
            current_date = run_date.to_pydatetime() if hasattr(run_date, 'to_pydatetime') else run_date
            
            # Get all calculated dates using the dynamic date system
            dates = du.get_all_report_dates(current_date)
            
            # Extract the dates we need
            wtd_start_date = dates['wtd_start_date']
            end_date = dates['end_date']
            mtd_start_date = dates['mtd_start_date']
            ytd_start_date = dates['ytd_start_date']
            
            # Display the clean report banner (reporting week only)
            week_range = f"{wtd_start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            st.info(f"📅 **Weekly Performance ({week_range})**")
            
            # Verify we have exactly 7 days (Monday to Sunday inclusive)
            if (end_date - wtd_start_date).days != 6:
                st.warning(f"⚠️ Date range is not exactly 7 days: {(end_date - wtd_start_date).days + 1} days")
                # Auto-correct if needed
                end_date = wtd_start_date + pd.Timedelta(days=6)

            # Total Business
            df = generate_df(session,"TOTAL_STORE_STATS_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
            
            # Add header and values for excel export
            subheader = "Total Business"
            if df is not None and not df.empty:
                st.subheader(subheader)
                st.dataframe(df)
                all_dataframes.append(df)
                subheaders.append(subheader)
            else:
                st.warning(f"No data available for '{subheader}'.")
                all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
                subheaders.append(subheader)
            
            df = pd.DataFrame()

            # Corporate Stores Only
            df = generate_df(session,"CORPORATE_STORE_STATS_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
            
            # Add header and values for excel export
            subheader = "Corporate Stores Only"
            if df is not None and not df.empty:
                st.subheader(subheader)
                st.dataframe(df)
                all_dataframes.append(df)
                subheaders.append(subheader)
            else:
                st.warning(f"No data available for '{subheader}'.")
                all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
                subheaders.append(subheader)
            
            df = pd.DataFrame()

            # Last Week Sales by Region
            df = generate_df(session,"REGION_LAST_WEEK_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

            # Add header and values for excel export
            subheader = "Last Week Sales by Region"
            if df is not None and not df.empty:
                st.subheader(subheader)
                st.dataframe(df)
                all_dataframes.append(df)
                subheaders.append(subheader)
            else:
                st.warning(f"No data available for '{subheader}'.")
                all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
                subheaders.append(subheader)
            
            df = pd.DataFrame()

            # Month to Date by Region
            df = generate_df(session,"REGION_MTD_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

            # Add header and values for excel export
            subheader = "Month to Date by Region"
            if df is not None and not df.empty:
                st.subheader(subheader)
                st.dataframe(df)
                all_dataframes.append(df)
                subheaders.append(subheader)
            else:
                st.warning(f"No data available for '{subheader}'.")
                all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
                subheaders.append(subheader)
            
            df = pd.DataFrame()

            # Year to Date by Region - Enhanced Debugging
            try:
                st.write("🔍 DEBUG: Starting Year to Date by Region...")
                df = generate_df(session,"REGION_YTD_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
                st.write(f"✅ DEBUG: Year to Date query completed, shape: {df.shape if df is not None else 'None'}")

                # Add header and values for excel export
                subheader = "Year to Date by Region"
                if df is not None and not df.empty:
                    st.subheader(subheader)
                    st.dataframe(df)
                    all_dataframes.append(df)
                    subheaders.append(subheader)
                    st.write("✅ DEBUG: Year to Date displayed successfully")
                else:
                    st.warning(f"No data available for '{subheader}'.")
                    all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
                    subheaders.append(subheader)
                    st.write("⚠️ DEBUG: Year to Date returned empty data")
            except Exception as e:
                st.error(f"Error in Year to Date by Region: {str(e)}")
                st.write("Skipping Year to Date due to error...")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Year to Date by Region (Error)")
                st.write(f"❌ DEBUG: Year to Date failed: {str(e)}")
            
            df = pd.DataFrame()

            # Service Top 20 Items
            df = generate_df(session,"ITEM_SERVICE_TOP_20",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

            # Add header and values for excel export
            subheader = "Service Top 20 Items"
            if df is not None and not df.empty:
                st.subheader(subheader)
                st.dataframe(df)
                all_dataframes.append(df)
                subheaders.append(subheader)
            else:
                st.warning(f"No data available for '{subheader}'.")
                all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
                subheaders.append(subheader)
            
            df = pd.DataFrame()

            # Service Total
            df = generate_df(session,"ITEM_SERVICE_TOTAL",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

            # Add header and values for excel export
            subheader = "Total Service Items"
            if df is not None and not df.empty:
                st.subheader(subheader)
                st.dataframe(df)
                all_dataframes.append(df)
                subheaders.append(subheader)
            else:
                st.warning(f"No data available for '{subheader}'.")
                all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
                subheaders.append(subheader)
            
            df = pd.DataFrame()

            # Retail Top 20 Items - With Error Handling
            try:
                df = generate_df(session,"ITEM_RETAIL_TOP_20",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

                # Add header and values for excel export
                subheader = "Retail Top 20 Items"
                if df is not None and not df.empty:
                    st.subheader(subheader)
                    st.dataframe(df)
                    all_dataframes.append(df)
                    subheaders.append(subheader)
                else:
                    st.warning(f"No data available for '{subheader}'.")
                    all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
                    subheaders.append(subheader)
            except Exception as e:
                st.error(f"Error generating Retail Top 20 Items: {str(e)}")
                st.write("Skipping Retail Top 20 Items due to error...")
                # Add empty DataFrame to maintain list consistency
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Retail Top 20 Items (Error)")
            
            df = pd.DataFrame()

            # Load Total Retail Items
            st.write("🔍 Loading Total Retail Items...")
            df = generate_df(session,"ITEM_RETAIL_TOTAL",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
            if df is not None and not df.empty:
                st.subheader("Total Retail Items")
                st.dataframe(df, use_container_width=True)
                all_dataframes.append(df)
                subheaders.append("Total Retail Items")
            else:
                st.warning("No data available for 'Total Retail Items'.")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Total Retail Items (No Data)")

            # Load Transaction Count sections
            st.write("🔍 Loading Transaction Count sections...")
            df = generate_df(session,"TRANS_COUNT_TOTAL_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
            if df is not None and not df.empty:
                st.subheader("Transaction Count Total")
                st.dataframe(df, use_container_width=True)
                all_dataframes.append(df)
                subheaders.append("Transaction Count Total")
            else:
                st.warning("No data available for 'Transaction Count Total'.")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Transaction Count Total (No Data)")

            df = generate_df(session,"TRANS_COUNT_REGION_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
            if df is not None and not df.empty:
                st.subheader("Transaction Count by Region")
                st.dataframe(df, use_container_width=True)
                all_dataframes.append(df)
                subheaders.append("Transaction Count by Region")
            else:
                st.warning("No data available for 'Transaction Count by Region'.")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Transaction Count by Region (No Data)")
            
            # Load Basket Size sections
            st.write("🔍 Loading Basket Size sections...")
            df = generate_df(session,"BASKET_AVG_TOTAL_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
            if df is not None and not df.empty:
                st.subheader("Basket Size Total")
                st.dataframe(df, use_container_width=True)
                all_dataframes.append(df)
                subheaders.append("Basket Size Total")
            else:
                st.warning("No data available for 'Basket Size Total'.")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Basket Size Total (No Data)")

            df = generate_df(session,"BASKET_AVG_REGION_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
            if df is not None and not df.empty:
                st.subheader("Basket Size by Region")
                st.dataframe(df, use_container_width=True)
                all_dataframes.append(df)
                subheaders.append("Basket Size by Region")
            else:
                st.warning("No data available for 'Basket Size by Region'.")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Basket Size by Region (No Data)")
            
            df = pd.DataFrame()

            # ######## Assuming subheaders and all_dataframes are lists

            # section_dict = dict(zip(subheaders, all_dataframes))
            # for section, df in section_dict.items():
            #     # Get the corresponding rename mapping for this section
            #     rename_mapping = rc.rename_columns.get(section, {})
            
            #     # Rename the dataframe columns using the mapping
            #     df.rename(columns=rename_mapping, inplace=True)

            ############
            # Daily Sales Last Week - Enhanced Debugging and Error Handling
            try:
                st.write("🔍 DEBUG: Starting Daily Sales section...")
                import daily_sales as ds
                st.write("✅ DEBUG: daily_sales module imported successfully")
                
                # Use the same date range as the rest of the report
                daily_start_date = wtd_start_date.strftime(config.DATE_FORMAT)
                daily_end_date = end_date.strftime(config.DATE_FORMAT)
                
                st.write(f"🔍 DEBUG: Calling daily_sales_table with start_date={daily_start_date}, end_date={daily_end_date}")
                
                df = ds.daily_sales_table(session, daily_start_date, daily_end_date)
                st.write(f"✅ DEBUG: daily_sales_table completed, DataFrame shape: {df.shape if df is not None else 'None'}")
                
                # Add summary rows
                if not df.empty:
                    st.write("🔍 DEBUG: Adding summary rows...")
                    df = ds.daily_sales_summary_rows(df)
                    st.write("✅ DEBUG: Summary rows added successfully")
                
                # Get week number for title (fiscal year starting Sept 1)
                fiscal_year_start = pd.to_datetime("2025-09-01")
                
                # Calculate weeks since fiscal year start
                days_since_fiscal_start = (pd.to_datetime(daily_start_date) - fiscal_year_start).days
                week_number = (days_since_fiscal_start // 7) + 1
                
                # Add header and values for excel export
                subheader = f"Daily Sales Last Week (Week {week_number})"
                
                st.write(f"🔍 DEBUG: Daily sales DataFrame shape: {df.shape if df is not None else 'None'}")
                st.write(f"🔍 DEBUG: Daily sales DataFrame empty: {df.empty if df is not None else 'None'}")
                
                if df is not None and not df.empty:
                    st.subheader(subheader)
                    st.dataframe(df, width='stretch')
                    all_dataframes.append(df)
                    subheaders.append(subheader)
                    st.write(f"✅ Daily Sales table added to Excel export")
                else:
                    st.warning(f"No data available for '{subheader}'.")
                    all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
                    subheaders.append(subheader)
                    st.write(f"❌ Daily Sales table is empty")
                    
            except Exception as e:
                st.error(f"Error in Daily Sales section: {str(e)}")
                st.write("Skipping Daily Sales due to error...")
                # Add empty DataFrame to maintain list consistency
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Daily Sales Last Week (Error)")
                st.write(f"❌ DEBUG: Daily Sales failed with error: {str(e)}")
            
            # LOYALTY KPI TABLE - SINGLE CLEAN VERSION (Green, Blue, Silver, Gold format)
            try:
                loyalty_start_date = wtd_start_date.strftime(config.DATE_FORMAT)
                loyalty_end_date = end_date.strftime(config.DATE_FORMAT)
                
                st.write(f"🔍 DEBUG: Adding Loyalty KPI table with dates {loyalty_start_date} to {loyalty_end_date}")
                
                # Use the correct loyalty_kpi_pivot module for Green/Blue/Silver/Gold format
                df = lp.loyalty_kpi_main(session, loyalty_start_date, loyalty_end_date)
                
                subheader = "Loyalty KPI"
                
                if df is not None and not df.empty:
                    st.subheader(subheader)
                    st.dataframe(df, use_container_width=True)
                    all_dataframes.append(df)
                    subheaders.append(subheader)
                    st.write(f"✅ Loyalty KPI table added successfully!")
                else:
                    st.warning(f"No data for Loyalty KPI")
                    all_dataframes.append(pd.DataFrame())
                    subheaders.append(subheader)
                    
            except Exception as e:
                st.error(f"Error with Loyalty KPI: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Loyalty KPI (Error)")
            
            # Top 10 Stores and ICU Stores
            try:
                st.write("🔍 DEBUG: Starting Top 10/ICU Stores section...")
                
                # Get store data for Top 10 and ICU analysis
                st.write("🔍 DEBUG: Calling generate_df for STORE_PIVOTS_NO_LOYALTY_PATH...")
                df_stores = generate_df(session, "STORE_PIVOTS_NO_LOYALTY_PATH", end_date, wtd_start_date, mtd_start_date, ytd_start_date)
                
                st.write(f"🔍 DEBUG: df_stores is None: {df_stores is None}")
                if df_stores is not None:
                    st.write(f"🔍 DEBUG: df_stores empty: {df_stores.empty}")
                    st.write(f"🔍 DEBUG: df_stores shape: {df_stores.shape}")
                    st.write(f"🔍 DEBUG: df_stores columns: {list(df_stores.columns)}")
                
                if df_stores is not None and not df_stores.empty:
                    st.write("🔍 DEBUG: Creating store dataframes using center_pivots...")
                    # Create Top 10 and ICU dataframes using center_pivots
                    store_dataframes = cp.final_dataframes_dictionary(df_stores)
                    
                    st.write(f"🔍 DEBUG: store_dataframes keys: {list(store_dataframes.keys())}")
                    
                    # Display Top 10 Stores
                    if "df_top_10" in store_dataframes and not store_dataframes["df_top_10"].empty:
                        st.subheader("Top 10 Stores - Current Sales")
                        st.dataframe(store_dataframes["df_top_10"], use_container_width=True)
                        all_dataframes.append(store_dataframes["df_top_10"])
                        subheaders.append("Top 10 Stores - Current Sales")
                        st.write(f"✅ Top 10 Stores table added successfully!")
                    else:
                        st.write("🔍 DEBUG: Top 10 stores not available or empty")
                    
                    # Display ICU Stores
                    if "df_icu" in store_dataframes and not store_dataframes["df_icu"].empty:
                        st.subheader("ICU Stores - Current Sales")
                        st.dataframe(store_dataframes["df_icu"], use_container_width=True)
                        all_dataframes.append(store_dataframes["df_icu"])
                        subheaders.append("ICU Stores - Current Sales")
                        st.write(f"✅ ICU Stores table added successfully!")
                    else:
                        st.write("🔍 DEBUG: ICU stores not available or empty")
                else:
                    st.warning("No store data available for Top 10 and ICU analysis.")
                    
            except Exception as e:
                st.error(f"Error with Top 10/ICU Stores: {str(e)}")
                st.write(f"🔍 DEBUG: Exception details: {type(e).__name__}: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Top 10/ICU Stores (Error)")
            
            ############
            # Update session state
            st.session_state.all_dataframes = all_dataframes
            st.session_state.subheaders = subheaders
            # Generate the Excel file using the template
            try:
                # Format dates as per config.DATE_FORMAT
                formatted_start_date = wtd_start_date.strftime(config.DATE_FORMAT)
                formatted_end_date = end_date.strftime(config.DATE_FORMAT)

                # # Convert `section_dict` to lists for compatibility
                # all_dataframes = list(section_dict.values())  # List of dataframes
                # subheaders = list(section_dict.keys())  # List of section headers

                # columns_with_two_decimals = {
                #     'Loyalty KPI': ['Frequency Spend (Rolling 12 months)'],
                #     'Clicks Loyalty KPI': ['Frequency Spend (Rolling 12 months)'],
                # }

                # Use the lists in the export function
                combined_excel_data = ef.export_combined_excel_from_template(
                    all_dataframes=all_dataframes,
                    subheaders=subheaders,
                    start_date=formatted_start_date,
                    end_date=formatted_end_date,
                    template_path="clicks_scorecard_template.xlsx",
                   # columns_with_two_decimals=columns_with_two_decimals
                )
                # Debugging: Check if combined_excel_data is not empty
                if combined_excel_data:
                    st.session_state.excel_data = combined_excel_data

                    subject = "Test Scorecard Weekly"
                    body = (
                        f"Good day,\n\nAttached is the Group Sales Weekly report for "
                        f"{formatted_start_date} to {formatted_end_date}"
                    )

                    # send_email(
                    #         "christo@astutetech.co.za",
                    #         subject,
                    #         body,
                    #         st.session_state.excel_data,
                    #         "clicks_scorecard_weekly_report.xlsx"
                    #     )
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

    


def generate_df(session,
                table_name: str,
                end_date,
                wtd_start_date,
                mtd_start_date,
                ytd_start_date):
    
    try:
        results_df = []

        query = ut.read_sql_query(config.FILE_PATHS[table_name])

        params = {
            "end_date": end_date.strftime(config.DATE_FORMAT),
            "wtd_start_date": wtd_start_date.strftime(config.DATE_FORMAT),
            "mtd_start_date": mtd_start_date.strftime(config.DATE_FORMAT),
            "ytd_start_date": ytd_start_date.strftime(config.DATE_FORMAT)
        }

        results_df = dut.execute_query(session, query, params)

        if results_df.empty:
            return None  # Or raise an error if that's your desired behavior
        
        return results_df
    except Exception as e:
        st.error(f"Error in generate_df for {table_name}: {str(e)}")
        return None

def send_email(recipient_email, subject, body, attachment_data, filename):
    """
    Send an email with the specified details.
    """
    try:
        SMTP_SERVER = 'smtp.office365.com'  # Replace with your SMTP server
        SMTP_PORT = 587
        SMTP_USERNAME = os.getenv('SMTP_USERNAME')  # Your SMTP username
        SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')  # Your SMTP password

        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['Bcc'] = recipient_email
        msg['Subject'] = subject

        # Add the body
        msg.attach(MIMEText(body, 'plain'))

        # Add the first attachment
        if attachment_data:
            part = MIMEApplication(attachment_data)
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            msg.attach(part)

        # Connect to SMTP server and send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()

        logging.info(f"Email sent to {recipient_email}")
        st.write(f":green[Email sent to {recipient_email}]")
        return True, None
    except Exception as e:
        logging.error(f"Failed to send email to {recipient_email}: {e}")
        st.write(f":red[Failed to send email to {recipient_email}: {e}]")
        return False, str(e)
    
if __name__ == "__main__":
    main()