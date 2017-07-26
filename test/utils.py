from datetime import datetime, timezone


def create_utc_date(*args, **kwargs):
    return datetime(*args, **kwargs, tzinfo=timezone.utc)
