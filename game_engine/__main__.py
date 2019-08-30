import asyncio

import socketio
from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS

from .game import Game

sio = socketio.AsyncServer(async_mode="sanic", cors_allowed_origins=[])

app = Sanic()
app.config['CORS_AUTOMATIC_OPTIONS'] = True
app.config['CORS_SUPPORTS_CREDENTIALS'] = True

sio.attach(app)
game = Game(sio)
cors = CORS(app, resources={r"/*": {"origins": "*"}}, automatic_options=True)


@app.route("/")
async def test(request):
    return json({"hello": "world"})


@app.listener("before_server_start")
def before_server_start(sanic, loop):
    sio.start_background_task(game.game_loop)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
