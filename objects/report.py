from objects.boss import Boss


class Fight:
    def __init__(self, report_code: str, ori_fight: dict, phase_id: int):
        self.code = report_code
        self.start_time = ori_fight['startTime'] if 'startTime' in ori_fight else -1
        self.end_time = ori_fight['endTime']
        self.phase_id = phase_id

        if 'phaseTransitions' in ori_fight and ori_fight['phaseTransitions'] is not None:
            for phase in ori_fight['phaseTransitions']:
                if phase['id'] == phase_id:
                    self.start_time = phase['startTime']

                if phase['id'] == phase_id + 1:
                    self.end_time = phase['startTime']

        if self.start_time == -1:
            raise ValueError(f'Fight in {report_code} does not has phase id {phase_id}')

        self.alias = f'f{self.start_time}'
        self.duration = self.end_time - self.start_time


class Report:
    def __init__(self, ori_report: dict, phase_id: int, boss: Boss):
        self.code = ori_report['code']
        self.fights = []
        self.flight_alias_map = {}
        self.phase_id = phase_id

        self.boss = boss

        for fight in ori_report['fights']:
            parsed_fight = Fight(self.code, fight, phase_id)
            self.fights.append(parsed_fight)
            self.flight_alias_map[parsed_fight.alias] = parsed_fight

    def get_phase_str(self) -> str:
        return f'p{self.phase_id}' if self.phase_id != -1 else 'entire'
