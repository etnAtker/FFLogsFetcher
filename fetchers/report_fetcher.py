import pickle
import sys
from pathlib import Path

from tqdm import tqdm

from objects.boss import Boss
from objects.report import Report
from utils.api_client import FFLogsApiClient
from utils.utils import timestamp

QT_GET_REPORTS = '''
query {{
	reportData {{
		reports(startTime: {start_time}, zoneID: {zone_id}, page: {page}) {{
			data {{
				code,
				fights(encounterID: {encounter_id}, killType: Kills, difficulty: {difficulty}) {{
					endTime,
					phaseTransitions {{
						id,
						startTime
					}}
				}}
			}}
		}}
	}}
}}
'''

QT_GET_REPORTS_ENTIRE = '''
query {{
	reportData {{
		reports(startTime: {start_time}, zoneID: {zone_id}, page: {page}) {{
			data {{
				code,
				fights(encounterID: {encounter_id}, killType: Kills, difficulty: {difficulty}) {{
					startTime,
					endTime
				}}
			}}
		}}
	}}
}}
'''


def get_reports_query(
        start_time: int,
        boss: Boss,
        page: int,
        entire: bool = False
) -> str:
    template = QT_GET_REPORTS if not entire else QT_GET_REPORTS_ENTIRE
    return template.format(
        start_time=start_time,
        zone_id=boss.zone_id,
        encounter_id=boss.enc_id,
        difficulty=boss.difficulty,
        page=page
    )


class ReportFetcher:
    def __init__(
            self,
            client: FFLogsApiClient,
            boss: Boss, phase_id: int,
            page_num: int = 5,
            start_time: int = timestamp(-14),
            enable_sav: bool = True,
            re_fetch: bool = False,
            sav_dir: Path = Path('sav'),
    ):
        self.client = client
        self.boss = boss
        self.phase_id = phase_id
        self.page_num = page_num
        self.start_time = start_time

        self.enable_sav = enable_sav
        self.re_fetch = re_fetch
        self.sav_dir = sav_dir

        sav_dir.mkdir(parents=True, exist_ok=True)

    def fetch(self) -> list[Report]:
        sav_data = []

        do_fetch = self.re_fetch or not self.enable_sav
        if not do_fetch:
            sav_data = self._load_sav()
            tqdm.write(f'Loaded {len(sav_data)} reports')
            if len(sav_data) == 0:
                do_fetch = True

        if do_fetch:
            tqdm.write('Fetching reports...')
            sav_data = self._do_fetch()
            tqdm.write(f'Fetched {len(sav_data)} reports')

        if self.enable_sav:
            self._dump_sav(sav_data)

        return sav_data

    def _do_fetch(self) -> list[Report]:
        sav_data = []
        for p in tqdm(range(self.page_num), file=sys.stdout):
            get_report_query = get_reports_query(
                self.start_time, self.boss, p + 1, self.phase_id == -1
            )

            ori_reports = self.client.query(get_report_query)

            for ori_report in ori_reports['data']['reportData']['reports']['data']:
                report = Report(ori_report, self.phase_id, self.boss)
                if len(report.fights) != 0:
                    sav_data.append(report)

        return sav_data

    def _get_sav_prefix(self) -> str:
        phase_str = f'p{self.phase_id}' if self.phase_id != -1 else 'entire'
        return f'reports_{self.boss.zone_id}_{self.boss.enc_id}_{phase_str}'

    def _get_sav_path(self) -> Path:
        return self.sav_dir / f'{self._get_sav_prefix()}.pk'

    def _load_sav(self) -> list[Report]:
        sav_path = self._get_sav_path()
        if sav_path.exists():
            with open(sav_path, 'rb') as f:
                return pickle.load(f)
        else:
            return []

    def _dump_sav(self, sav_data: list[Report]):
        with open(self._get_sav_path(), 'wb') as f:
            pickle.dump(sav_data, f)
