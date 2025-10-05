"""
Dynamic Date Utilities for Weekly Scorecard Reports

This module provides functions to calculate dynamic dates for weekly reports
based on the current date and business rules.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple


def get_reporting_week_dates(current_date: datetime = None) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """
    Calculate the reporting week dates based on the current date.
    
    Business Rule:
    - If current date is within the current week (Monday to Sunday inclusive),
      then report on the PREVIOUS week (Monday to Sunday)
    - If current date is outside the current week, report on the most recent complete week
    
    Args:
        current_date: The current date (defaults to today if None)
        
    Returns:
        Tuple of (week_start_date, week_end_date) for the reporting period
    """
    if current_date is None:
        current_date = datetime.now()
    
    # Convert to pandas Timestamp for consistency
    current_date = pd.Timestamp(current_date)
    
    # Get the current week's Monday (start of current week)
    current_weekday = current_date.weekday()  # Monday = 0, Sunday = 6
    current_week_monday = current_date - pd.Timedelta(days=current_weekday)
    
    # Get the current week's Sunday (end of current week)
    current_week_sunday = current_week_monday + pd.Timedelta(days=6)
    
    # Business Rule: If we're within the current week (inclusive), report on previous week
    if current_date >= current_week_monday and current_date <= current_week_sunday:
        # Report on the previous week
        reporting_week_monday = current_week_monday - pd.Timedelta(days=7)
        reporting_week_sunday = current_week_sunday - pd.Timedelta(days=7)
    else:
        # Report on the most recent complete week
        reporting_week_monday = current_week_monday - pd.Timedelta(days=7)
        reporting_week_sunday = current_week_sunday - pd.Timedelta(days=7)
    
    return reporting_week_monday, reporting_week_sunday


def get_financial_year_dates(reporting_end_date: pd.Timestamp) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """
    Calculate the financial year start and end dates based on reporting end date.
    
    Financial year runs from September 1st to August 31st.
    
    Args:
        reporting_end_date: The end date of the reporting week
        
    Returns:
        Tuple of (financial_year_start, financial_year_end)
    """
    # Determine the financial year
    if reporting_end_date.month > 9 or (reporting_end_date.month == 9 and reporting_end_date.day > 1):
        # We're in the current financial year
        financial_year_start = pd.to_datetime(f"{reporting_end_date.year}-09-01")
        financial_year_end = pd.to_datetime(f"{reporting_end_date.year + 1}-08-31")
    else:
        # We're in the previous financial year
        financial_year_start = pd.to_datetime(f"{reporting_end_date.year - 1}-09-01")
        financial_year_end = pd.to_datetime(f"{reporting_end_date.year}-08-31")
    
    return financial_year_start, financial_year_end


def get_month_to_date_start(reporting_end_date: pd.Timestamp) -> pd.Timestamp:
    """
    Calculate the month-to-date start date based on a 4-5-4 retail calendar.
    
    Args:
        reporting_end_date: The end date of the reporting week
        
    Returns:
        Month-to-date start date
    """
    # Get financial year dates
    fy_start, fy_end = get_financial_year_dates(reporting_end_date)
    
    # Ensure financial year start is a Monday
    fy_start_monday = fy_start - pd.Timedelta(days=fy_start.weekday())
    
    # 4-5-4 retail calendar pattern (weeks per month)
    pattern = [4, 5, 4, 4, 5, 4, 4, 5, 4, 4, 5, 4]
    
    # Adjust pattern if needed for leap year
    if (fy_end.weekday() == fy_start_monday.weekday()):
        pattern[-1] += 1  # Add extra week to last month
    
    # Calculate month start dates
    month_starts = []
    current = fy_start_monday
    for weeks in pattern:
        month_starts.append(current)
        current += pd.Timedelta(weeks=weeks)
    
    # Find which month the reporting end date falls into
    for i, month_start in enumerate(month_starts):
        month_end = (
            month_starts[i + 1]
            if i + 1 < len(month_starts)
            else month_start + pd.Timedelta(weeks=pattern[i])
        )
        if month_start <= reporting_end_date < month_end:
            return month_start
    
    # Fallback to first month if not found
    return month_starts[0]


def get_year_to_date_start(reporting_end_date: pd.Timestamp) -> pd.Timestamp:
    """
    Calculate the year-to-date start date (financial year start).
    
    Args:
        reporting_end_date: The end date of the reporting week
        
    Returns:
        Year-to-date start date (financial year start as Monday)
    """
    fy_start, _ = get_financial_year_dates(reporting_end_date)
    
    # Ensure it's a Monday
    fy_start_monday = fy_start - pd.Timedelta(days=fy_start.weekday())
    
    return fy_start_monday


def format_report_banner(reporting_start_date: pd.Timestamp, reporting_end_date: pd.Timestamp, 
                        current_date: datetime = None) -> str:
    """
    Format the report banner with dynamic dates.
    
    Args:
        reporting_start_date: Start date of the reporting week
        reporting_end_date: End date of the reporting week
        current_date: Current date (defaults to now)
        
    Returns:
        Formatted banner string
    """
    if current_date is None:
        current_date = datetime.now()
    
    # Format dates
    report_generated = current_date.strftime("%A, %B %d, %Y at %I:%M %p")
    week_range = f"{reporting_start_date.strftime('%B %d')} - {reporting_end_date.strftime('%B %d, %Y')}"
    
    # Get month start and financial year start
    month_start = get_month_to_date_start(reporting_end_date)
    fy_start = get_year_to_date_start(reporting_end_date)
    
    month_start_str = month_start.strftime("%B %d, %Y")
    fy_start_str = fy_start.strftime("%B %d, %Y")
    
    return f"Week: {week_range}"


def get_all_report_dates(current_date: datetime = None) -> dict:
    """
    Get all report dates in one function call.
    
    Args:
        current_date: Current date (defaults to now)
        
    Returns:
        Dictionary with all calculated dates
    """
    if current_date is None:
        current_date = datetime.now()
    
    # Get reporting week dates
    wtd_start_date, end_date = get_reporting_week_dates(current_date)
    
    # Get other dates
    mtd_start_date = get_month_to_date_start(end_date)
    ytd_start_date = get_year_to_date_start(end_date)
    
    # Get financial year dates
    fy_start, fy_end = get_financial_year_dates(end_date)
    
    return {
        'current_date': pd.Timestamp(current_date),
        'wtd_start_date': wtd_start_date,
        'end_date': end_date,
        'mtd_start_date': mtd_start_date,
        'ytd_start_date': ytd_start_date,
        'financial_year_start': fy_start,
        'financial_year_end': fy_end,
        'report_banner': format_report_banner(wtd_start_date, end_date, current_date)
    }


# Example usage and testing
if __name__ == "__main__":
    # Test with today's date (Monday, September 29, 2025)
    test_date = datetime(2025, 9, 29)  # Monday
    
    print("=== Testing Dynamic Date System ===")
    print(f"Test Date: {test_date.strftime('%A, %B %d, %Y')}")
    print()
    
    # Get all dates
    dates = get_all_report_dates(test_date)
    
    print("Calculated Dates:")
    print(f"Week Start (Monday): {dates['wtd_start_date'].strftime('%A, %B %d, %Y')}")
    print(f"Week End (Sunday): {dates['end_date'].strftime('%A, %B %d, %Y')}")
    print(f"Month Start: {dates['mtd_start_date'].strftime('%A, %B %d, %Y')}")
    print(f"Year Start: {dates['ytd_start_date'].strftime('%A, %B %d, %Y')}")
    print()
    print("Report Banner:")
    print(dates['report_banner'])


