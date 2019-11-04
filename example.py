import socketio
import asyncio
import random
import math

sio = socketio.AsyncClient()

def dist_between_blobs(a,b):
    x1, y1 = a["coords"]
    x2, y2 = b["coords"]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) **2)

async def action_request(data):
    state = data["state"]
    my_blobs = data["my_blobs"]
    state_id = data["state_id"]
    food = [o for o in state if o["is_food"]]
    closest_food = min(food, key=lambda x: dist_between_blobs(x, my_blobs[0]))

    food_x = closest_food["coords"][0]-my_blobs[0]["coords"][0]
    food_y = closest_food["coords"][1]-my_blobs[0]["coords"][1]

    await sio.emit(
        "action",
        {
            "state_id": state_id,
            "actions": [
                {
                    "blob_id": my_blobs[0]["blob_id"],
                    "vector": [food_x, food_y],
                    "speed": 30,
                    "type": "move",
                }
            ],
        },
    )


async def error_handler(data):
    print("ERROR:", data["message"])


async def start(sio):
    await sio.connect("http://142.93.112.226:4000")
    await sio.emit("register", {"name": "elnardu" + str(random.randint(1, 100))})
    await sio.wait()


sio.on("action_request", action_request)
sio.on("error", error_handler)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(sio))

