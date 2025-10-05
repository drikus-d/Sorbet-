import os
import pandas as pd
import config
import utils as ut
# import export_to_excel as exx
import database_utils as dut
# from data_processing import create_sales_df, add_subtotals_and_grand_total
# from display_utils import format_dataframe
from database_utils import execute_query, read_sql_query
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import logging
from datetime import datetime, timedelta
import pymsteams
import excel_format as ef

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

pd.set_option("display.float_format", lambda x: f"{x:,.0f}")

SMTP_SERVER = 'smtp.office365.com'  # Replace with your SMTP server
SMTP_PORT = 587
SMTP_USERNAME = os.getenv('SMTP_USERNAME')  # Your SMTP username
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')  # Your SMTP password

def send_teams_notification(message):
    try:
        myTeamsMessage = pymsteams.connectorcard("https://astutetechcoza.webhook.office.com/webhookb2/58a376bc-68b2-47e1-ab4c-5ea9fbfbc656@14ef98a8-28ff-445f-b7f5-1c071cb9fc86/IncomingWebhook/5a38d65502484ffdb51f6a9d002095c8/d9fe9924-71df-4be7-b5ab-1cb5cc5e0931/V2wAbm3RVi1ULOPCyNAOAffmh1WWnO9PNwjzus4WYOYls1")
        myTeamsMessage.text(message)
        myTeamsMessage.send()
    except Exception as e:
        # logging.error(f"Failed to send teams notification: {e}")
        # st.write(f":red[Failed to send teams notification: {e}]")
        return False, str(e)

def generate_df(session,
                table_name: str,
                end_date,
                wtd_start_date,
                mtd_start_date,
                ytd_start_date):
    
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
        return None  # Or raise an error if that’s your desired behavior
    
    return results_df

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

        # logging.info(f"Email sent to {recipient_email}")
        # st.write(f":green[Email sent to {recipient_email}]")
        return True, None
    except Exception as e:
        # logging.error(f"Failed to send email to {recipient_email}: {e}")
        # st.write(f":red[Failed to send email to {recipient_email}: {e}]")
        return False, str(e)

def generate_and_send_report(session, recipient_email):
    """
    Generate a report for the current month and send it via email.
    """
    
    # Title of the app
    # st.title("📈 Clicks Weekly Scorecard - Summary")

    # Date range selection (assuming utils.date_range_selection is defined)
    # start_date, end_date = ut.date_range_selection()
    # run_date = st.date_input(
    #     "Run Date:",
    #     value=datetime.today().date(), # Default to the current date
    #     min_value=None,  # No minimum date restriction
    #     max_value=None   # Removed max_value to allow any date selection
    # )

    run_date = datetime.today().date()

    run_date = pd.Timestamp(run_date)

    # Initialize session state variables
    # if "all_dataframes" not in st.session_state:
    #     st.session_state.all_dataframes = []
    # if "subheaders" not in st.session_state:
    #     st.session_state.subheaders = []
    # if "excel_data" not in st.session_state:
    #     st.session_state.excel_data = None
    # if "formatted_start_date" not in st.session_state:
    #     st.session_state.formatted_start_date = ""
    # if "formatted_end_date" not in st.session_state:
    #     st.session_state.formatted_end_date = ""

    # Button to generate and display the scorecard
    # if st.button("🔍 Generate Scorecard"):
    #     with st.spinner("Generating scorecard..."):
    # Initialize lists to hold DataFrames and their corresponding subheaders
    all_dataframes = []
    subheaders = []

    # Set the date parameters used in the run
    today = run_date # pd.to_datetime(run_date)
    
    end_date   = today - pd.Timedelta(days=1)

    # The week start is the previous monday
    day_of_week = end_date.weekday()  # Monday is 0, Sunday is 6
    days_to_subtract = (day_of_week + 7 - 0) % 7    
    wtd_start_date = end_date - pd.Timedelta(days=days_to_subtract)

    # Determine the start date for the year-to-date report.
    # — if it's after Sept 1 (month > 9, or month==9 & day>1), YTD starts this year's Sept 1
    # — otherwise (including Sept 1!), YTD starts last year's Sept 1
    if end_date.month > 9 or (end_date.month == 9 and end_date.day > 1):
        ytd_start_date = pd.to_datetime(f"{end_date.year}-09-01")
    else:
        ytd_start_date = pd.to_datetime(f"{end_date.year - 1}-09-01")

    ytd_start_date = ytd_start_date - pd.Timedelta(days=ytd_start_date.weekday())

    fin_end_date = ytd_start_date + pd.Timedelta(weeks=52)

    # Work out the month start date based on a 454 trade calender
    
    # Define retail calendar start
    pattern = [4, 5, 4, 4, 5, 4, 4, 5, 4, 4, 5, 4]
    if (fin_end_date.weekday() == ytd_start_date.weekday()):
        pattern[-1] += 1  # Add extra week to last month

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
    df = generate_df(session,"TOTAL_STORE_STATS_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
    
    # Add header and values for excel export
    subheader = "Total Business"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # Corporate Stores Only
    df = generate_df(session,"CORPORATE_STORE_STATS_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
    
    # Add header and values for excel export
    subheader = "Corporate Stores Only"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # Last Week Sales by Region
    df = generate_df(session,"REGION_LAST_WEEK_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

    # Add header and values for excel export
    subheader = "Last Week Sales by Region"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # Month to Date by Region
    df = generate_df(session,"REGION_MTD_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

    # Add header and values for excel export
    subheader = "Month to Date by Region"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # Year to Date by Region
    df = generate_df(session,"REGION_YTD_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

    # Add header and values for excel export
    subheader = "Year to Date by Region"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # Service Top 20 Items
    df = generate_df(session,"ITEM_SERVICE_TOP_20",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

    # Add header and values for excel export
    subheader = "Service Top 20 Items"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # Service Total
    df = generate_df(session,"ITEM_SERVICE_TOTAL",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

    # Add header and values for excel export
    subheader = "Total Service Items"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # Retail Top 20 Items
    df = generate_df(session,"ITEM_RETAIL_TOP_20",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

    # Add header and values for excel export
    subheader = "Retail Top 20 Items"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # Retail Total
    df = generate_df(session,"ITEM_RETAIL_TOTAL",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

    # Add header and values for excel export
    subheader = "Total Retail Items"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # Transaction Count
    df = generate_df(session,"TRANS_COUNT_TOTAL_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

    # Add header and values for excel export
    subheader = "Transaction Count"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # Transaction Count: Last Week by Region
    df = generate_df(session,"TRANS_COUNT_REGION_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)
    
    # Add header and values for excel export
    subheader = "Transaction Count: Last Week by Region"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # Basket Size
    df = generate_df(session,"BASKET_AVG_TOTAL_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

    # Add header and values for excel export
    subheader = "Basket Size"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # Basket size: Last Week by Region
    df = generate_df(session,"BASKET_AVG_REGION_PATH",end_date,wtd_start_date,mtd_start_date,ytd_start_date)

    # Add header and values for excel export
    subheader = "Basket size: Last Week by Region"
    if df is not None and not df.empty:
        # st.subheader(subheader)
        # st.dataframe(df)
        all_dataframes.append(df)
        subheaders.append(subheader)
    else:
        # st.warning(f"No data available for '{subheader}'.")
        all_dataframes.append(pd.DataFrame())  # Append empty DataFrame
        subheaders.append(subheader)
    
    df = pd.DataFrame()

    # ######## Assuming subheaders and all_dataframes are lists

    # section_dict = dict(zip(subheaders, all_dataframes))
    # for section, df in section_dict.items():
    #     # Get the corresponding rename mapping for this section
    #     rename_mapping = rc.rename_columns.get(section, {})
    
    #     # Rename the dataframe columns using the mapping
    #     df.rename(columns=rename_mapping, inplace=True)


    
    ############
    # Update session state
    # st.session_state.all_dataframes = all_dataframes
    # st.session_state.subheaders = subheaders

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
            # st.session_state.excel_data = combined_excel_data

            subject = "Clicks Scorecard Weekly"
            body = (
                f"Good day,\n\nAttached is the Group Sales Weekly report for "
                f"{formatted_start_date} to {formatted_end_date}"
            )

            send_email(
                    recipient_email,
                    subject,
                    body,
                    combined_excel_data, # st.session_state.excel_data,
                    "clicks_scorecard_weekly_report.xlsx"
                )
        # else:
            # st.error("❌ Excel file generation returned empty data.")
    except Exception as e:
        logging.error(f"Error in Lambda handler: {e}")
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
        # st.error(f"An error occurred while generating the Excel file: {e}")
        # st.session_state.excel_data = None

def main():
    """
    Main function to automate monthly reports and emails.
    """
    session = ut.get_snowflake_session()

    # Fetch recipient list from Snowflake
    recipients_query = "SELECT 'christo@astutetech.co.za' as RECIPIENT_EMAIL union SELECT 'philip.seimenis@sorbet.co.za' as RECIPIENT_EMAIL union SELECT 'Sibusiso@sorbet.co.za' as RECIPIENT_EMAIL" # "SELECT RECIPIENT_EMAIL FROM STREAMLIT.PUBLIC.RECIPIENT_LIST WHERE ACTIVE = TRUE"
    recipient_df = session.sql(recipients_query).to_pandas()
    recipients = recipient_df['RECIPIENT_EMAIL'].tolist()

    if not recipients:
        logging.warning("No active recipients found.")
        return

    # Generate and email reports for all recipients
    for recipient_email in recipients:
        generate_and_send_report(session, recipient_email)

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    """
    try:
        main()  # Call your main function here
        return {
            'statusCode': 200,
            'body': 'Reports generated and emails sent successfully.'
        }
    except Exception as e:
        logging.error(f"Error in Lambda handler: {e}")
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }