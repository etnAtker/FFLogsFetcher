from constants.bosses import *
from fetchers.cast_table_fetcher import CastTableFetcher
from fetchers.damage_table_fetcher import DamageTableFetcher
from fetchers.report_fetcher import ReportFetcher
from utils.api_client import FFLogsApiClient

CLIENT_ID = ''
CLIENT_KEY = ''

BOSS = TOP      # 参见constants.bosses，如需统计其他boss，请自行添加。
PHASE = 6       # 如果想统计整个战斗，或某boss不分P，则此项置为-1

client = FFLogsApiClient(CLIENT_ID, CLIENT_KEY)

report_fetcher = ReportFetcher(client, BOSS, PHASE, 1)
reports = report_fetcher.fetch()

damage_fetcher = DamageTableFetcher(client, reports)
damage_fetcher.fetch_and_export_stat()

cpm_fetcher = CastTableFetcher(client, reports)
cpm_fetcher.fetch_and_export_stat()
