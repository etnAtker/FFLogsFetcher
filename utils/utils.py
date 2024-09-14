import datetime
from typing import Any, TypeVar

T = TypeVar('T')


def timestamp(days_offset: int) -> int:
    return int((datetime.datetime.utcnow() + datetime.timedelta(days=days_offset)).timestamp()) * 1000


def fmt(x) -> str:
    if x > 1_000_000:
        return f'{x / 1000000:.3f}M'

    if x > 100_000:
        return f'{x / 1000:.3f}k'

    return f'{x:.1f}'


def has_any_keywords(s: str, keywords: set) -> bool:
    for keyword in keywords:
        if keyword in s:
            return True

    return False


def flatten_list_in_dict(ori: dict[Any, list[T]]) -> T:
    return [item for lists_in_dict in ori.values() for item in lists_in_dict]
