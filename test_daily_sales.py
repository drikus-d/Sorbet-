# test_daily_sales.py - Minimal test for Daily Sales functionality

import streamlit as st
import pandas as pd
import config
import utils as ut
import daily_sales as ds

# Configure Streamlit page
st.set_page_config(
    page_title="Daily Sales Test",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    """
    Minimal test function for Daily Sales functionality.
    """
    st.title("📈 Daily Sales Test")
    
    # Simple date input
    run_date = st.date_input(
        "Run Date:",
        value=pd.Timestamp("2025-09-28").date(),
    )
    
    run_date = pd.Timestamp(run_date)
    
    # Calculate week dates
    end_date = run_date - pd.Timedelta(days=1)
    day_of_week = end_date.weekday()
    days_to_subtract = (day_of_week + 7 - 0) % 7 + 1
    wtd_start_date = end_date - pd.Timedelta(days=days_to_subtract)
    
    # Button to test Daily Sales
    if st.button("🔍 Test Daily Sales"):
        try:
            st.write("🔍 DEBUG: Starting Daily Sales test...")
            
            # Establish Snowflake session
            session = ut.get_snowflake_session()
            st.write("✅ DEBUG: Snowflake session established")
            
            # Use the calculated date range
            daily_start_date = wtd_start_date.strftime(config.DATE_FORMAT)
            daily_end_date = end_date.strftime(config.DATE_FORMAT)
            
            st.write(f"🔍 DEBUG: Using dates: {daily_start_date} to {daily_end_date}")
            
            # Call Daily Sales function
            df = ds.daily_sales_table(session, daily_start_date, daily_end_date)
            st.write(f"✅ DEBUG: Daily sales table completed, shape: {df.shape if df is not None else 'None'}")
            
            if df is not None and not df.empty:
                # Add summary rows
                df = ds.daily_sales_summary_rows(df)
                st.write("✅ DEBUG: Summary rows added")
                
                # Format for display
                df_display = ds.format_daily_sales_display(df)
                st.write("✅ DEBUG: Display formatting completed")
                
                # Show the table
                st.subheader("Daily Sales Last Week")
                st.dataframe(df_display, use_container_width=True)
                st.write("✅ Daily Sales table displayed successfully!")
                
            else:
                st.warning("No data available for Daily Sales.")
                
        except Exception as e:
            st.error(f"Error in Daily Sales test: {str(e)}")
            st.write(f"❌ DEBUG: Error details: {str(e)}")

if __name__ == "__main__":
    main()

