# Sorbet Weekly Scorecard

A comprehensive Streamlit application for generating weekly performance scorecards for Sorbet salons and nailbars, with integrated Excel export functionality.

## Features

- **Weekly Performance Dashboard**: Real-time metrics for current, previous, and budget periods
- **Regional Analysis**: Performance breakdown by geographic regions
- **Store Performance**: Top 10 performing stores and ICU (In-Crisis Unit) stores analysis
- **Loyalty KPI Tracking**: Customer loyalty metrics and basket size analysis
- **Excel Export**: Professional Excel reports with custom formatting
- **Dynamic Date Calculations**: Automatic fiscal year and period calculations

## Key Components

### Main Application
- `Sorbet_Weekly_Scorecard.py` - Main Streamlit application
- `clicks_scorecard_weekly.py` - Original base application

### Data Processing
- `loyalty_kpi_pivot.py` - Loyalty KPI data processing and formatting
- `center_pivots.py` - Store pivot data manipulation
- `excel_format.py` - Excel export and formatting logic

### Configuration
- `config.py` - Database connections and formatting configurations

### SQL Queries
- `sql/` directory contains all database queries for different metrics
- Optimized for Snowflake database with proper schema references

## Installation

1. Clone the repository:
```bash
git clone https://github.com/drikus-d/Sorbet-.git
cd Sorbet-
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure database settings in `config.py`

4. Run the application:
```bash
streamlit run Sorbet_Weekly_Scorecard.py
```

## Database Requirements

- Snowflake database connection
- Access to `marts.common.dim_center` and related schemas
- Proper permissions for revenue and transaction data

## Excel Export Features

- Custom formatting for different metric types
- Merged headers and professional styling
- Percentage calculations with proper formatting
- Regional data pivoting
- Store performance summaries

## Recent Updates

- ✅ Fixed percentage formatting for loyalty metrics
- ✅ Aligned basket size calculations across tables
- ✅ Improved Excel export formatting
- ✅ Added fiscal year and execution date tracking
- ✅ Enhanced regional data display
- ✅ Optimized store performance tables

## Contributing

This project is designed for Sorbet's internal reporting needs. For modifications or enhancements, please follow the existing code structure and maintain compatibility with the Snowflake database schema.

## License

Internal use only - Sorbet Proprietary
