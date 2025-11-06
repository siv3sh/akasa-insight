"""
Helper utilities for data cleaning, normalization, and validation.
"""

from datetime import datetime
from typing import Any, Optional
import re


class DataHelpers:
    """
    Helper class for data cleaning and normalization operations.
    """
    
    @staticmethod
    def normalize_date(date_value: Any) -> Optional[datetime]:
        """
        Normalize various date formats to datetime object.
        
        Args:
            date_value: Date value in various formats
            
        Returns:
            datetime: Normalized datetime object or None if parsing fails
        """
        if date_value is None or date_value == '':
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        # List of common date formats to try
        date_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%d-%m-%Y %H:%M:%S',
            '%d-%m-%Y',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d',
            '%Y%m%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
        ]
        
        date_str = str(date_value).strip()
        
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def normalize_mobile_number(mobile: Any) -> Optional[str]:
        """
        Normalize mobile number by removing special characters and spaces.
        
        Args:
            mobile: Mobile number in various formats
            
        Returns:
            str: Normalized mobile number or None if invalid
        """
        if mobile is None or mobile == '':
            return None
        
        # Convert to string and remove all non-digit characters
        mobile_str = str(mobile).strip()
        mobile_clean = re.sub(r'\D', '', mobile_str)
        
        # Validate length (assuming 10 digits for Indian mobile numbers)
        if len(mobile_clean) >= 10:
            return mobile_clean[-10:]  # Return last 10 digits
        
        return None if not mobile_clean else mobile_clean
    
    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """
        Safely convert value to float with default fallback.
        
        Args:
            value: Value to convert
            default: Default value if conversion fails
            
        Returns:
            float: Converted float value or default
        """
        if value is None or value == '':
            return default
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """
        Safely convert value to integer with default fallback.
        
        Args:
            value: Value to convert
            default: Default value if conversion fails
            
        Returns:
            int: Converted integer value or default
        """
        if value is None or value == '':
            return default
        
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def clean_string(value: Any) -> Optional[str]:
        """
        Clean and normalize string values.
        
        Args:
            value: String value to clean
            
        Returns:
            str: Cleaned string or None if empty
        """
        if value is None:
            return None
        
        cleaned = str(value).strip()
        return cleaned if cleaned else None
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> tuple[bool, list]:
        """
        Validate that all required fields are present and non-empty.
        
        Args:
            data: Dictionary with data to validate
            required_fields: List of required field names
            
        Returns:
            tuple: (is_valid, list of missing fields)
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None or str(data[field]).strip() == '':
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields
