from typing import List

from . import Player


class ACTION_TYPES:
    MOVE = 0
    SPLIT = 1


class Action:
    player: Player
    vector: List[float]
    speed: float
    action_type: int
    blob_id: str

    def __init__(self, data, player):
        self._validate_data(data)

        self.player = player
        self.vector = data['vector']
        self.speed = data['speed']
        self.blob_id = data['blob_id']

        if data['type'] == 'move':
            self.action_type = ACTION_TYPES.MOVE
        elif data['type'] == 'split':
            self.action_type = ACTION_TYPES.SPLIT

    @classmethod
    def _validate_data(cls, data):
        assert (
            "blob_id" in data
            and "vector" in data
            and "speed" in data
            and "type" in data
        )

        assert isinstance(data["vector"], list)
        assert len(data["vector"]) == 2
        assert data["speed"] >= 0 and data["speed"] <= 100
        assert data["type"] in ("move", "split")

