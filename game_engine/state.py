import math
import random
import uuid
from collections import defaultdict
from typing import List

from .action import ACTION_TYPES, Action
from .config import (
    AREA_SIZE,
    BIT_SPAWN_PROB,
    PLAYER_BLOB_INITIAL_RADIUS,
    FOOD_BLOB_INITIAL_RADIUS,
)
from .player import Player


class Blob:
    owner: Player
    radius: int
    coords: List[int]
    blob_id: str

    def __init__(self, owner, coords, radius):
        self.coords = coords
        self.owner = owner
        self.radius = radius
        self.blob_id = str(uuid.uuid4())
        self.clamp_coords()

    def move_to(self, coords):
        self.coords = coords
        self.clamp_coords()

    def move(self, vec, speed):
        mag = math.hypot(*vec)
        vec[0] /= mag
        vec[1] /= mag

        vec[0] *= speed
        vec[1] *= speed
        new_coords = [self.coords[0] + vec[0], self.coords[1] + vec[1]]
        self.coords = new_coords
        self.clamp_coords()

    def clamp_coords(self):
        minX = 0 + self.radius
        maxX = AREA_SIZE[0] - self.radius

        minY = 0 + self.radius
        maxY = AREA_SIZE[1] - self.radius

        if self.coords[0] > maxX:
            self.coords[0] = maxX
        elif self.coords[0] < minX:
            self.coords[0] = minX

        if self.coords[1] > maxY:
            self.coords[1] = maxY
        elif self.coords[1] < minY:
            self.coords[1] = minY

    def eat(self, amount):
        self.radius += amount

    def split(self):
        if self.radius < 10:
            return

        self.radius = int(self.radius * 0.4)

        # Create a copy of the current blob
        return Blob(self.owner, self.coords, self.radius)

    def distance(self, other: "Blob"):
        return math.hypot(
            self.coords[0] - other.coords[0], self.coords[1] - other.coords[1]
        )

    def can_eat(self, other: "Blob") -> bool:
        distance = self.distance(other)

        if self.radius <= other.radius:
            return False

        if self.radius - other.radius > distance:
            return True

        return False

    def to_dict(self):
        return {
            "owner_name": self.owner.display_name,
            "coords": self.coords,
            "radius": self.radius,
            "blob_id": self.blob_id,
            "is_food": True if self.owner.uuid == 0 else False,
        }


class STATE_CHANGES:
    DELETE = 0
    EAT_AMOUNT = 1


class GameState:
    def __init__(self):
        self.blobs = {}
        self.player_blobs = defaultdict(list)
        self.computer_player = Player(None, "Admin")
        self.computer_player.uuid = 0
        self.current_state_dump = []

    def place_new_blob(self, player: Player, radius=PLAYER_BLOB_INITIAL_RADIUS):
        # TODO: add collision check since we can place blob inside another blob
        blob = Blob(
            player,
            [random.randint(0, AREA_SIZE[0]), random.randint(0, AREA_SIZE[1])],
            radius=radius,
        )
        self.add_blob(blob)

    def add_blob(self, blob: Blob):
        self.blobs[blob.blob_id] = blob
        self.player_blobs[blob.owner.uuid].append(blob)

    def remove_blob(self, blob: Blob):
        self.blobs.pop(blob.blob_id)
        self.player_blobs[blob.owner.uuid].remove(blob)

    def remove_player(self, uuid):
        blobs = self.player_blobs[uuid]
        for blob in blobs:
            self.remove_blob(blob)

    def advance(self, actions: List[Action]):
        self._apply_actions(actions)
        self._collision_check()
        self._spawn_bits()
        self._update_state_dump()

    def _apply_actions(self, actions: List[Action]):
        for action in actions:
            blob: Blob = self.blobs[action.blob_id]

            if blob.owner != action.player:
                print(action.player.display_name, "is trying to cheat lol")
                continue

            if action.action_type == ACTION_TYPES.MOVE:
                blob.move(action.vector, action.speed)
            elif action.action_type == ACTION_TYPES.SPLIT:
                new_blob = blob.split()
                if new_blob:
                    self.add_blob(new_blob)

    def _spawn_bits(self):
        if random.random() < BIT_SPAWN_PROB:
            self.place_new_blob(self.computer_player, radius=FOOD_BLOB_INITIAL_RADIUS)

    def _collision_check(self):
        changes = []

        for blob_id in self.blobs:
            blob = self.blobs[blob_id]

            # TODO: This is slow. Rewrite using quadtrees
            for other_blob_id in self.blobs:
                other_blob = self.blobs[other_blob_id]

                if other_blob == blob:
                    continue

                can_eat = blob.can_eat(other_blob)

                if can_eat:
                    changes.append((STATE_CHANGES.DELETE, other_blob))
                    changes.append(
                        (STATE_CHANGES.EAT_AMOUNT, blob, int(other_blob.radius * 0.5))
                    )

        for change in changes:
            if change[0] == STATE_CHANGES.DELETE:
                self.remove_blob(change[1])
            elif change[0] == STATE_CHANGES.EAT_AMOUNT:
                change[1].eat(change[2])

    def _update_state_dump(self):
        self.current_state_dump = []
        for blob_id in self.blobs:
            self.current_state_dump.append(self.blobs[blob_id].to_dict())

    def get_state(self):
        return self.current_state_dump

    def construct_request_for_player(self, uuid):
        state = self.get_state()
        current_player_blobs = list(map(lambda x: x.to_dict(), self.player_blobs[uuid]))

        return {"state": state, "my_blobs": current_player_blobs}
