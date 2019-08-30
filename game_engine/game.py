import asyncio
from .config import TICK_TIME, ADMIN_PASSWORD
from .player import Player
from .state import GameState
from .action import Action

import uuid


class Game:
    def __init__(self, sio):
        self.sio = sio

        self.sio.on("register", self.handle_player_register)
        self.sio.on("disconnect", self.handle_player_disconnect)
        self.sio.on("action", self.handle_action)

        self.players = {}
        self.state = GameState()

    async def handle_player_register(self, sid, data):
        print("register", sid, data)

        if "name" not in data:
            return

        if sid in self.players:
            return

        self.players[sid] = Player(sid, data["name"])
        self.state.place_new_blob(self.players[sid])

    async def handle_player_disconnect(self, sid):
        print("disconnect", sid)

        if sid in self.players:
            self.state.remove_player(self.players[sid].uuid)
            self.players.pop(sid)

    async def handle_action(self, sid, data):
        if "state_id" not in data:
            await self.sio.emit(
                "error", {"message": 'You must have "state_id" in your action'}, to=sid
            )
            return

        if data["state_id"] != self.current_state_id:
            await self.sio.emit(
                "error",
                {
                    "message": 'Your "state_id" is invalid. Maybe your program is too slow.'
                },
                to=sid,
            )
            return

        if "actions" not in data:
            await self.sio.emit(
                "error", {"message": 'You must have "actions" in your action'}, to=sid
            )
            return

        if sid in self.responded_to_request:
            await self.sio.emit(
                "error", {"message": "You can only emit actions once per tick"}, to=sid
            )
            return

        self.responded_to_request.add(sid)

        for action in data["actions"]:
            try:
                action_object = Action(action, self.players[sid])
            except AssertionError:
                await self.sio.emit(
                    "error",
                    {"message": "Invalid action structure: " + repr(action)},
                    to=sid,
                )
                return

            self.actions.append(action_object)

    async def broadcast_state(self):
        state_dump = self.state.get_state()
        coros = []
        coros.append(self.sio.emit("state", state_dump))

        for sid in self.players:
            player = self.players[sid]
            request = self.state.construct_request_for_player(player.uuid)
            request["state_id"] = self.current_state_id
            coros.append(self.sio.emit("action_request", request, to=player.sid))

        await asyncio.gather(*coros)

    async def game_loop(self):
        while True:
            self.current_state_id = str(uuid.uuid1())
            self.actions = []
            self.responded_to_request = set()
            await self.broadcast_state()

            await asyncio.sleep(TICK_TIME / 1000)

            self.state.advance(self.actions)
