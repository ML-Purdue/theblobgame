import socketio
import asyncio
import random

sio = socketio.AsyncClient()


async def action_request(data):
    state = data["state"]
    my_blobs = data["my_blobs"]
    state_id = data["state_id"]

    await sio.emit(
        "action",
        {
            "state_id": state_id,
            "actions": [
                {
                    "blob_id": my_blobs[0]["blob_id"],
                    "vector": [random.uniform(-1, 1), random.uniform(-1, 1)],
                    "speed": 50,
                    "type": "move",
                }
            ],
        },
    )


async def error_handler(data):
    print("ERROR:", data["message"])


async def start(sio):
    await sio.connect("http://localhost:8000")
    await sio.emit("register", {"name": "elnardu" + str(random.randint(1, 100))})
    await sio.wait()


sio.on("action_request", action_request)
sio.on("error", error_handler)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(sio))

