import requests
import base64
import time


TOKEN_ENDPOINT = 'https://www.fflogs.com/oauth/token'
TOKEN_BODY = {'grant_type': 'client_credentials'}
GRAPH_QL_ENDPOINT = 'https://www.fflogs.com/api/v2/client'


class FFLogsApiClient:
    def __init__(self, client_id: str, client_key: str):
        self.client_id = client_id
        self.client_key = client_key
        self.token = ''
        self.token_expires_in = 0

    @staticmethod
    def token_required(method):
        def runner(self, *args, **kwargs):
            if self.token_expires_in <= time.time():
                self.refresh_token()

            return method(self, *args, **kwargs)

        return runner

    def refresh_token(self):
        auth_b64 = base64.b64encode(f'{self.client_id}:{self.client_key}'.encode())
        auth_str = f'Basic {auth_b64.decode()}'

        r = requests.post(TOKEN_ENDPOINT, data=TOKEN_BODY, headers={
            'Authorization': auth_str
        }).json()

        self.token = r['access_token']
        self.token_expires_in = time.time() + r['expires_in'] - 600

    @token_required
    def query(self, graph_ql_query: str) -> dict | list:
        return requests.post(GRAPH_QL_ENDPOINT, json={
            'query': graph_ql_query,
        }, headers={
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }).json()
