from typing import Any

from .abstract_table_fetcher import AbstractTableFetcher
from .table_type import TableType


class DamageTableFetcher(AbstractTableFetcher):
    def get_table_type(self) -> TableType:
        return TableType.DamageDone

    def extract(self, dur_ms: int, raw_data: dict) -> dict[str, Any]:
        dur_s = dur_ms / 1000
        return {
            'dur': dur_ms,
            'job': raw_data['type'],
            'ad': raw_data['totalADPS'],
            'adps': raw_data['totalADPS'] / dur_s,
            'rd': raw_data['totalRDPS'],
            'rdps': raw_data['totalRDPS'] / dur_s
        }

    def get_statistic_keys(self) -> list[str]:
        return ['ad', 'adps', 'rd', 'rdps']
