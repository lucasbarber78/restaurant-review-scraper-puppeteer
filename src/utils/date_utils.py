#!/usr/bin/env python3
"""
Date Utilities Module

This module provides helper functions for parsing and standardizing dates.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Optional, Union
from dateutil import parser

logger = logging.getLogger(__name__)


def parse_date(date_string: str, fuzzy: bool = True) -> Optional[datetime]:
    """Parse a date string into a datetime object.
    
    Args:
        date_string (str): Date string to parse.
        fuzzy (bool, optional): Whether to use fuzzy parsing. Defaults to True.
        
    Returns:
        Optional[datetime]: Parsed datetime object or None if parsing fails.
    """
    if not date_string:
        return None
        
    try:
        # Try using dateutil parser with fuzzy matching
        return parser.parse(date_string, fuzzy=fuzzy)
    except (ValueError, parser.ParserError):
        # Handle relative dates
        return _parse_relative_date(date_string)


def standardize_date_format(date_obj: Union[datetime, str], output_format: str = '%Y-%m-%d') -> str:
    """Convert a datetime object or string to a standardized date format.
    
    Args:
        date_obj (Union[datetime, str]): Datetime object or date string.
        output_format (str, optional): Output date format. Defaults to '%Y-%m-%d'.
        
    Returns:
        str: Formatted date string.
    """
    if isinstance(date_obj, str):
        date_obj = parse_date(date_obj)
        
    if not date_obj:
        return ''
        
    return date_obj.strftime(output_format)


def _parse_relative_date(date_string: str) -> Optional[datetime]:
    """Parse relative date strings like "yesterday", "2 days ago", etc.
    
    Args:
        date_string (str): Relative date string.
        
    Returns:
        Optional[datetime]: Datetime object or None if parsing fails.
    """
    date_string = date_string.lower().strip()
    current_date = datetime.now()
    
    # Handle "today", "yesterday", etc.
    if 'today' in date_string:
        return current_date
    elif 'yesterday' in date_string:
        return current_date - timedelta(days=1)
        
    # Handle "X days/weeks/months/years ago"
    days_ago_match = re.search(r'(\d+)\s+day', date_string)
    weeks_ago_match = re.search(r'(\d+)\s+week', date_string)
    months_ago_match = re.search(r'(\d+)\s+month', date_string)
    years_ago_match = re.search(r'(\d+)\s+year', date_string)
    
    if days_ago_match:
        days = int(days_ago_match.group(1))
        return current_date - timedelta(days=days)
    elif weeks_ago_match:
        weeks = int(weeks_ago_match.group(1))
        return current_date - timedelta(weeks=weeks)
    elif months_ago_match:
        months = int(months_ago_match.group(1))
        # Approximate month calculation
        new_month = current_date.month - months
        new_year = current_date.year
        
        while new_month <= 0:
            new_month += 12
            new_year -= 1
            
        # Handle day overflow (e.g., trying to create February 30)
        try:
            return current_date.replace(year=new_year, month=new_month)
        except ValueError:
            # Last day of month
            if new_month == 12:
                return current_date.replace(year=new_year, month=new_month, day=31)
            else:
                return current_date.replace(year=new_year, month=new_month + 1, day=1) - timedelta(days=1)
    elif years_ago_match:
        years = int(years_ago_match.group(1))
        try:
            return current_date.replace(year=current_date.year - years)
        except ValueError:
            # February 29 in leap year
            return current_date.replace(year=current_date.year - years, month=2, day=28)
            
    # Fallback for unrecognized formats
    return None
