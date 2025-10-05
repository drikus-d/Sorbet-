# Sorbet Weekly Scorecard

import streamlit as st
import center_pivots as cp
import loyalty_kpi_pivot as lp
import clicks_loyalty_kpi as clp
import database_utils as dut
import utils as ut
import pandas as pd
import excel_format as ef
import config
import date_utils as du
import os
import smtplib
import logging
import daily_sales as ds

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Configure Streamlit page
st.set_page_config(
    page_title="Sorbet Weekly Scorecard - Summary",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Set pandas display options
pd.set_option("display.float_format", lambda x: f"{x:,.0f}")

def main():
    """
    Main function to run the Sorbet Scorecard Streamlit app.
    """
    # Establish Snowflake session
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
    st.title("📈 Sorbet Weekly Scorecard - Summary")

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

            # Get all calculated dates using the dynamic date system
            current_date = run_date.to_pydatetime() if hasattr(run_date, 'to_pydatetime') else run_date
            dates = du.get_all_report_dates(current_date)
            
            # Extract the dates we need
            wtd_start_date = dates['wtd_start_date']
            end_date = dates['end_date']
            mtd_start_date = dates['mtd_start_date']
            ytd_start_date = dates['ytd_start_date']
            
            # Display the clean report banner with fiscal year and execution info
            week_range = f"{wtd_start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            
            # Calculate fiscal year start
            fiscal_year_start = pd.to_datetime(f"{current_date.year}-09-01") if current_date.month >= 9 else pd.to_datetime(f"{current_date.year-1}-09-01")
            fiscal_year_start_str = fiscal_year_start.strftime('%Y-%m-%d')
            
            # Get current execution date and time
            execution_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            st.info(f"📅 **Weekly Performance ({week_range})**")
            st.info(f"📊 **Fiscal Year Start: {fiscal_year_start_str}**")
            st.info(f"⏰ **Execution Date & Time: {execution_datetime}**")
            
            # Verify we have exactly 7 days (Monday to Sunday inclusive)
            if (end_date - wtd_start_date).days != 6:
                st.warning(f"⚠️ Date range is not exactly 7 days: {(end_date - wtd_start_date).days + 1} days")
                end_date = wtd_start_date + pd.Timedelta(days=6)

            # Total Business
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

            # Corporate Stores Only
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

            # Weekly by Region
            try:
                df = generate_df(session,"REGION_LAST_WEEK_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
                subheader = "Week to Date by Region"
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
                st.error(f"Error in Weekly by Region: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Weekly by Region (Error)")

            # Service Top 20 Items
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

            # Service Total
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
                st.error(f"Error generating Retail Top 20 Items: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Retail Top 20 Items (Error)")

            # Total Retail Items
            df = generate_df(session,"ITEM_RETAIL_TOTAL",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
            if df is not None and not df.empty:
                st.subheader("Total Retail Items")
                st.dataframe(df, width='stretch')
                all_dataframes.append(df)
                subheaders.append("Total Retail Items")
            else:
                st.warning("No data available for 'Total Retail Items'.")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Total Retail Items (No Data)")

            # Transaction Count Total
            df = generate_df(session,"TRANS_COUNT_TOTAL_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
            if df is not None and not df.empty:
                st.subheader("Transaction Count Total")
                st.dataframe(df, width='stretch')
                all_dataframes.append(df)
                subheaders.append("Transaction Count Total")
            else:
                st.warning("No data available for 'Transaction Count Total'.")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Transaction Count Total (No Data)")

            # Transaction Count by Region
            df = generate_df(session,"TRANS_COUNT_REGION_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
            if df is not None and not df.empty:
                st.subheader("Transaction Count by Region")
                st.dataframe(df, width='stretch')
                all_dataframes.append(df)
                subheaders.append("Transaction Count by Region")
            else:
                st.warning("No data available for 'Transaction Count by Region'.")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Transaction Count by Region (No Data)")
            
            # Basket Size Total
            df = generate_df(session,"BASKET_AVG_TOTAL_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
            if df is not None and not df.empty:
                st.subheader("Basket Size Total")
                st.dataframe(df, width='stretch')
                all_dataframes.append(df)
                subheaders.append("Basket Size Total")
            else:
                st.warning("No data available for 'Basket Size Total'.")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Basket Size Total (No Data)")

            # Basket Size by Region
            df = generate_df(session,"BASKET_AVG_REGION_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
            if df is not None and not df.empty:
                st.subheader("Basket Size by Region")
                st.dataframe(df, width='stretch')
                all_dataframes.append(df)
                subheaders.append("Basket Size by Region")
            else:
                st.warning("No data available for 'Basket Size by Region'.")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Basket Size by Region (No Data)")

            # Daily Sales Last Week
            try:
                daily_start_date = wtd_start_date.strftime(config.DATE_FORMAT)
                daily_end_date = end_date.strftime(config.DATE_FORMAT)
                
                df = ds.daily_sales_table(session, daily_start_date, daily_end_date)
                
                # Add summary rows
                if not df.empty:
                    df = ds.daily_sales_summary_rows(df)
                
                # Calculate week number dynamically based on fiscal year
                fiscal_year_start = pd.to_datetime(f"{current_date.year}-09-01") if current_date.month >= 9 else pd.to_datetime(f"{current_date.year-1}-09-01")
                days_since_fiscal_start = (pd.to_datetime(daily_start_date) - fiscal_year_start).days
                week_number = (days_since_fiscal_start // 7) + 1
                
                subheader = f"Daily Sales Last Week (Week {week_number})"
                
                if df is not None and not df.empty:
                    st.subheader(subheader)
                    st.dataframe(df, width='stretch')
                    all_dataframes.append(df)
                    subheaders.append(subheader)
                else:
                    st.warning(f"No data available for '{subheader}'.")
                    all_dataframes.append(pd.DataFrame())
                    subheaders.append(subheader)
                    
            except Exception as e:
                st.error(f"Error in Daily Sales section: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Daily Sales Last Week (Error)")
            
            # Loyalty KPI Table
            try:
                loyalty_start_date = wtd_start_date.strftime(config.DATE_FORMAT)
                loyalty_end_date = end_date.strftime(config.DATE_FORMAT)
                
                df = lp.loyalty_kpi_main(session, loyalty_start_date, loyalty_end_date)
                subheader = "Loyalty KPI"
                
                if df is not None and not df.empty:
                    st.subheader(subheader)
                    st.dataframe(df, width='stretch')
                    all_dataframes.append(df)
                    subheaders.append(subheader)
                else:
                    st.warning(f"No data for Loyalty KPI")
                    all_dataframes.append(pd.DataFrame())
                    subheaders.append(subheader)
                    
            except Exception as e:
                st.error(f"Error with Loyalty KPI: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Loyalty KPI (Error)")
            
            # Clicks Loyalty KPI Table
            try:
                clicks_loyalty_start_date = wtd_start_date.strftime(config.DATE_FORMAT)
                clicks_loyalty_end_date = end_date.strftime(config.DATE_FORMAT)
                
                df_clicks_loyalty = clp.loyalty_kpi_main_measures_table(session, clicks_loyalty_start_date, clicks_loyalty_end_date)
                subheader_clicks_loyalty = "Clicks Loyalty KPI"
                
                if df_clicks_loyalty is not None and not df_clicks_loyalty.empty:
                    st.subheader(subheader_clicks_loyalty)
                    st.dataframe(df_clicks_loyalty, width='stretch')
                    all_dataframes.append(df_clicks_loyalty)
                    subheaders.append(subheader_clicks_loyalty)
                else:
                    st.warning(f"No data for Clicks Loyalty KPI")
                    all_dataframes.append(pd.DataFrame())
                    subheaders.append(subheader_clicks_loyalty)
                    
            except Exception as e:
                st.error(f"Error with Clicks Loyalty KPI: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Clicks Loyalty KPI (Error)")
            
            # Top 10 Stores and ICU Stores
            try:
                df_stores = generate_df(session, "STORE_PIVOTS_NO_LOYALTY_PATH", end_date, wtd_start_date, mtd_start_date, ytd_start_date)
                
                if df_stores is not None and not df_stores.empty:
                    store_dataframes = cp.final_dataframes_dictionary(df_stores)
                    
                    # Display Top 10 Stores
                    if "df_top_10" in store_dataframes and not store_dataframes["df_top_10"].empty:
                        # Remove unwanted columns from Top 10 Stores DataFrame
                        columns_to_remove = [
                            "% CURRENT REV CONTR", 
                            "% PREVIOUS REV CONTR",
                            "SERVICES CURRENT TO PREVIOUS %",
                            "RETAIL CURRENT TO PREVIOUS %", 
                            "TOTAL CURRENT TO PREVIOUS %",
                            "SERVICES REVENUE TO BUDGET %",
                            "RETAIL REVENUE TO BUDGET %",
                            "TOTAL REVENUE TO BUDGET %",
                            "% TOTAL BUDGET",
                            "SERVICES CURRENT TO PREVIOUS",
                            "RETAIL CURRENT TO PREVIOUS",
                            "TOTAL CURRENT TO PREVIOUS",
                            "SERVICES REVENUE TO BUDGET",
                            "RETAIL REVENUE TO BUDGET",
                            "TOTAL REVENUE TO BUDGET"
                        ]
                        existing_columns_to_remove = [col for col in columns_to_remove if col in store_dataframes["df_top_10"].columns]
                        store_dataframes["df_top_10"] = store_dataframes["df_top_10"].drop(columns=existing_columns_to_remove)
                        
                        st.subheader("Top 10 Stores - Current Sales")
                        st.dataframe(store_dataframes["df_top_10"], width='stretch')
                        all_dataframes.append(store_dataframes["df_top_10"])
                        subheaders.append("Top 10 Stores - Current Sales")
                    
                    # Display ICU Stores
                    if "df_icu" in store_dataframes and not store_dataframes["df_icu"].empty:
                        # Remove unwanted columns from ICU Stores DataFrame
                        columns_to_remove = [
                            "% CURRENT REV CONTR", 
                            "% PREVIOUS REV CONTR",
                            "SERVICES CURRENT TO PREVIOUS %",
                            "RETAIL CURRENT TO PREVIOUS %", 
                            "TOTAL CURRENT TO PREVIOUS %",
                            "SERVICES REVENUE TO BUDGET %",
                            "RETAIL REVENUE TO BUDGET %",
                            "TOTAL REVENUE TO BUDGET %",
                            "% TOTAL BUDGET",
                            "SERVICES CURRENT TO PREVIOUS",
                            "RETAIL CURRENT TO PREVIOUS",
                            "TOTAL CURRENT TO PREVIOUS",
                            "SERVICES REVENUE TO BUDGET",
                            "RETAIL REVENUE TO BUDGET",
                            "TOTAL REVENUE TO BUDGET"
                        ]
                        existing_columns_to_remove = [col for col in columns_to_remove if col in store_dataframes["df_icu"].columns]
                        store_dataframes["df_icu"] = store_dataframes["df_icu"].drop(columns=existing_columns_to_remove)
                        
                        st.subheader("ICU Stores - Current Sales")
                        st.dataframe(store_dataframes["df_icu"], width='stretch')
                        all_dataframes.append(store_dataframes["df_icu"])
                        subheaders.append("ICU Stores - Current Sales")
                else:
                    st.warning("No store data available for Top 10 and ICU analysis.")
                    
            except Exception as e:
                st.error(f"Error with Top 10/ICU Stores: {str(e)}")
                all_dataframes.append(pd.DataFrame())
                subheaders.append("Top 10/ICU Stores (Error)")
            
            # Store fiscal year and execution info for Excel banner
            fiscal_year_start_str = fiscal_year_start.strftime('%Y-%m-%d')
            execution_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
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
                    fiscal_year_start=fiscal_year_start_str,
                    execution_datetime=execution_datetime
                )
                
                if combined_excel_data:
                    st.session_state.excel_data = combined_excel_data
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
            file_name="sorbet_scorecard_weekly_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.success("✅ Formatted Excel file is ready for download!")
    else:
        st.info("🔄 Please generate the scorecard to enable the download button.")

def generate_df(session, table_name: str, end_date, wtd_start_date, mtd_start_date, ytd_start_date):
    """
    Generate DataFrame from SQL query with dynamic parameters
    """
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

def send_email(recipient_email, subject, body, attachment_data, filename):
    """
    Send an email with the specified details.
    """
    try:
        SMTP_SERVER = 'smtp.office365.com'
        SMTP_PORT = 587
        SMTP_USERNAME = os.getenv('SMTP_USERNAME')
        SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['Bcc'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        if attachment_data:
            part = MIMEApplication(attachment_data)
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            msg.attach(part)

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