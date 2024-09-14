from typing import Any

from .abstract_table_fetcher import AbstractTableFetcher
from .table_type import TableType


class CastTableFetcher(AbstractTableFetcher):
    def get_table_type(self) -> TableType:
        return TableType.Casts

    def extract(self, dur_ms: int, raw_data: dict) -> dict[str, Any]:
        dur_m = dur_ms / 1000 / 60
        return {
            'dur': dur_ms,
            'job': raw_data['type'],
            'cast_n': raw_data['total'],
            'cpm': raw_data['total'] / dur_m
        }

    def get_statistic_keys(self) -> list[str]:
        return ['cpm']

