import os
from ..config import settings
import pandas as pd
from .log_config import get_data_logger
from threading import Lock


log = get_data_logger()
csv_mutex = Lock()

def get_detected_plates() -> list:
    """
    Retrieve all detected license plates from CSV file.
    Returns a list of dictionaries containing plate data.
    """
    try:
        with csv_mutex:
            if os.path.exists(settings.csv_file):
                df = pd.read_csv(settings.csv_file)
                return df.to_dict(orient='records')
            else:
                return []
    except Exception as e:
        log.exception(f"Failed to read CSV file: {e}")
        return []

def get_filtered_plates(start_date=None, end_date=None, plate_number=None) -> list:
    """
    Retrieve filtered license plate data from CSV file based on date range and/or plate number.
    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
        plate_number (str, optional): License plate number to filter
    Returns:
        list: Filtered list of dictionaries containing plate data
    """
    try:
        with csv_mutex:
            if not os.path.exists(settings.csv_file):
                return []
            
            df = pd.read_csv(settings.csv_file)
            
            if start_date:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df[df['timestamp'] >= start_date]
            
            if end_date:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df[df['timestamp'] <= end_date]
            
            if plate_number:
                df = df[df['plate_number'].str.contains(plate_number, case=False, na=False)]
            
            return df.to_dict(orient='records')
            
    except Exception as e:
        log.exception(f"Failed to read and filter CSV file: {e}")
        return []
    


def search_plate(plate_number: str) -> dict:
    """
    Search for a specific license plate in the CSV file.
    Args:
        plate_number (str): License plate number to search
    Returns:
        dict: Dictionary containing plate data
    """
    try:
        with csv_mutex:
            if not os.path.exists(settings.csv_file):
                return {}
            
            df = pd.read_csv(settings.csv_file)
            df = df[df['plate_number'].str.contains(plate_number, case=False, na=False)]
            
            if df.empty:
                return {}
            
            return df.to_dict(orient='records')[0]
            
    except Exception as e:
        log.exception(f"Failed to search for plate: {e}")
        return {}