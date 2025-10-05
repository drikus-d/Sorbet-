"""
Database Utilities Module
"""

import streamlit as st
import pandas as pd
from typing import Dict, Optional

def execute_query(session, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
    """
    Execute a query and return the result as a DataFrame.
    """
    try:
        if params:
            modified_query = query.format(**params)
            result = session.sql(modified_query).to_pandas()
        else:
            result = session.sql(query).to_pandas()
        return result
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return pd.DataFrame()

def read_sql_query(file_path: str) -> str:
    """
    Read an SQL query from a file and return it as a string.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"SQL file not found. Please ensure the file path is correct: {file_path}")
        return ""
