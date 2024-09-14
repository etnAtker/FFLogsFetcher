import abc
import json
import sys
from pathlib import Path
from typing import Callable

from pandas import DataFrame
from tqdm import tqdm

from .table_type import TableType
from objects.report import Report
from utils.api_client import FFLogsApiClient
from utils.statistics import default_analyser
from utils.utils import *

QT_GET_TABLE = '''
query {{
	reportData {{
		report(code: "{report_code}") {{
				code,
{fights_tables}
		}}
	}}
}}
'''

IQT_GET_TABLE = '''
				{fight_alias}: table(
					encounterID: {encounter_id}, 
					killType: Kills
					dataType: {table_type}, 
					startTime: {start_time}, 
					endTime: {end_time}
				),
'''

JOB_TYPE_EXCLUDE = {'Limit Break', 'LimitBreak', 'Unknown'}
RECOVERABLE_ERR_KEYWORDS = {'do not have permission'}


def get_table_query(enc_id: int | str, report: Report, table_type: TableType) -> str:
    table_queries = ''
    for fight in report.fights:
        table_queries += IQT_GET_TABLE.format(
            fight_alias=fight.alias,
            encounter_id=enc_id,
            table_type=table_type.name,
            start_time=fight.start_time,
            end_time=fight.end_time
        )
    return QT_GET_TABLE.format(report_code=report.code, fights_tables=table_queries)


class AbstractTableFetcher(abc.ABC):
    def __init__(
            self,
            client: FFLogsApiClient,
            reports: list[Report],
            enable_sav: bool = True,
            re_fetch: bool = False,
            sav_dir: Path = Path('sav'),
    ):
        self.client = client
        self.reports = reports

        self.enable_sav = enable_sav
        self.re_fetch = re_fetch
        self.sav_dir = sav_dir

        sav_dir.mkdir(parents=True, exist_ok=True)

        self.boss = reports[0].boss
        self.phase = reports[0].get_phase_str()

    @abc.abstractmethod
    def get_table_type(self) -> TableType:
        pass

    @abc.abstractmethod
    def extract(self, dur_ms: int, raw_data: dict) -> dict[str, Any]:
        pass

    @abc.abstractmethod
    def get_statistic_keys(self) -> list[str]:
        pass

    def fetch_and_export_stat(
            self,
            export_dir: Path = Path('statistics'),
            analyser: Callable[[dict[str, list[dict[str, Any]]], str], DataFrame] = default_analyser
    ):
        self._export_statistics(self._fetch(), export_dir, analyser)

    def _fetch(self) -> dict[str, list[dict[str, Any]]]:
        tqdm.write(f"Fetching {self.get_table_type().name}...")
        if len(self.reports) == 0:
            return {}

        sav_data = self._load_sav() if self.enable_sav and not self.re_fetch else {}
        self._do_fetch(sav_data)

        if self.enable_sav:
            self._dump_sav(sav_data)

        return sav_data

    def _export_statistics(
            self,
            result: dict[str, list[dict[str, Any]]],
            export_dir: Path,
            analyser: Callable[[dict[str, list[dict[str, Any]]], str], DataFrame]
    ):
        export_dir.mkdir(parents=True, exist_ok=True)
        for key in self.get_statistic_keys():
            analyser(result, key).to_csv(export_dir / f'{self._get_sav_prefix()}_{key}.csv')

    def _do_fetch(self, sav_data: dict[str, list[dict[str, Any]]]):
        for r in tqdm(self.reports, file=sys.stdout):
            if r.code in sav_data:
                tqdm.write(f'Skipping {r.code}')
                continue

            raw = self.client.query(get_table_query(r.boss.enc_id, r, self.get_table_type()))
            try:
                if (
                        'errors' in raw
                        and has_any_keywords(raw['errors'][0]['message'], RECOVERABLE_ERR_KEYWORDS)
                ):
                    tqdm.write(f'Skipping {r.code}, because of return: {raw}')
                    continue

                extracted_data = []
                for k, v in raw['data']['reportData']['report'].items():
                    if k == 'code':
                        continue

                    fight_data = v['data']
                    dur_ms = fight_data['combatTime']
                    if 'downtime' in fight_data:
                        dur_ms -= fight_data['downtime']

                    for player_data in fight_data['entries']:
                        if player_data['type'] in JOB_TYPE_EXCLUDE:
                            continue

                        extracted_data.append(self.extract(dur_ms, player_data))

                sav_data[r.code] = extracted_data
            except Exception as e:
                tqdm.write(f'Error: {e}')
                tqdm.write(f'Raw return: {raw}')
                return

    def _get_sav_prefix(self) -> str:
        return f'{self.get_table_type().name}_{self.boss.zone_id}_{self.boss.enc_id}_{self.phase}'

    def _get_sav_path(self) -> Path:
        return self.sav_dir / f'{self._get_sav_prefix()}.json'

    def _load_sav(self) -> dict[str, list[dict[str, Any]]]:
        sav_path = self._get_sav_path()
        if sav_path.exists():
            with open(sav_path, 'r') as f:
                return json.load(f)
        else:
            return {}

    def _dump_sav(self, sav_data: dict[str, list[dict[str, Any]]]):
        with open(self._get_sav_path(), 'w') as f:
            json.dump(sav_data, f)
