# query/utils/time_parser.py

import dateparser
from datetime import datetime

def parse_datetime_from_query(text: str) -> str:
    dt = dateparser.parse(
        text,
        settings={
            "TIMEZONE": "Asia/Kolkata",
            "TO_TIMEZONE": "Asia/Kolkata",
            "RETURN_AS_TIMEZONE_AWARE": True,
            "PREFER_DATES_FROM": "future",
        }
    )
    return dt.isoformat() if dt else None
