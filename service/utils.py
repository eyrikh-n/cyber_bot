from datetime import timedelta, datetime

import pytz


async def get_timezone_by_utc_offset(utc_offset: timedelta) -> str:
    current_utc_time = datetime.now(pytz.utc)
    for tz in map(pytz.timezone, pytz.all_timezones_set):
        if current_utc_time.astimezone(tz).utcoffset() == utc_offset:
            return tz.zone
    return ""
