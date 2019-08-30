import uuid


class Player:
    uuid: str
    sid: str
    display_name: str
    score: int

    def __init__(self, sid, display_name):
        self.sid = sid
        self.display_name = display_name
        self.uuid = str(uuid.uuid4())

    def __eq__(self, other):
        return self.uuid == other.uuid
