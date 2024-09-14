class Boss:
    def __init__(self, zone_id: int, enc_id: int, difficulty: int = 0):
        self.zone_id = zone_id
        self.enc_id = enc_id
        self.difficulty = difficulty
