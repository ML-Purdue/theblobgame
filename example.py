import queue
import socketio
import asyncio
import random
import math
import numpy as np

sio = socketio.AsyncClient()

DIRECTIONS = [(-1, 0), (-1, -1), (0, 1), (1, 1), (1,  0), (1, -1), (0, -1), (-1, 1)]

def euc_dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def a_star(graph, start, end):
    #print(start)
    #print(end)
    #print("Begin")
    graph = np.copy(graph)
    cost_so_far = np.zeros(graph.shape)
    q = queue.PriorityQueue()
    graph[start[0], start[1]] = -1
    q.put((0,start))
    while not q.empty():
        #print(q.queue)
        curr = q.get()[1]
        #print("curr", curr)
        #input()
        curr_cost = cost_so_far[curr[0], curr[1]] 
        for i, direction in enumerate(DIRECTIONS):
            nextLoc = (curr[0] + direction[0], curr[1] + direction[1])
            cost = math.sqrt((direction[0] ** 2) + (direction[1] ** 2)) + curr_cost
            if isValidPoint(graph, nextLoc) and ((graph[nextLoc[0], nextLoc[1]] == 0) or (cost < cost_so_far[nextLoc[0], nextLoc[1]])):
                #print("Updated")
                priority = cost + curr_cost + euc_dist(nextLoc, end)
                #print(direction, euc_dist(nextLoc, end), priority)
                q.put((priority, nextLoc))
                cost_so_far[nextLoc[0], nextLoc[1]] = cost + curr_cost
                graph[nextLoc[0], nextLoc[1]] = i + 1
                if nextLoc == end:
                    return graph
    return graph

def isValidPoint(graph, p):
    i, j = p
    if i < 0 or i >= graph.shape[0]:
        return False
    if j < 0 or j >= graph.shape[1]:
        return False
    return True

def backtrace(graph, end):
    path = []
    x, y = end
    curr = graph[x, y]
    while(curr != 0 and curr != -1):
        move_x, move_y = DIRECTIONS[curr - 1]
        x, y = x - move_x, y - move_y
        path.append((x,y))
        curr = graph[x, y]
    return path

def dist_between_blobs(a,b):
    x1, y1 = a["coords"]
    x2, y2 = b["coords"]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) **2)

def fill_grid(grid, enemies):
    for e in enemies:
        x, y = [int(x) for x in a["coords"]]
        radius = int(a["radius"])
        left = math.max(0, x - radius)
        top = math.max(0, y - radius)
        right = math.min(grid.shape[0] - 1, x + radius)
        bottom = math.min(grid.shape[1] - 1, y + radius)
        grid[top:bottom, left:right] = -1

async def action_request(data):
    # define grid
    grid = np.zeros((1000,1000), dtype=int)

    state = data["state"]
    my_blobs = data["my_blobs"]
    state_id = data["state_id"]
    food = [o for o in state if o["is_food"]]
    target = food[random.randint(0, len(food) - 1)]
    enemies = [o for o in state if (not o["is_food"]) and (o != my_blobs[0])]

    print("Data Obtained")


    fill_grid(grid, enemies)

    print("Grid filled")

    blob_coords = [int(x) for x in my_blobs[0]["coords"]]
    target_coords = [int(x) for x in target["coords"]]
    

    traced_graph = a_star(grid, (blob_coords[1], blob_coords[0]), (target_coords[1], target_coords[0]))
    
    print("Breadth first complete")
     
    path = backtrace(traced_graph, target_coords)

    print("Backtrace Complete")
    print(path)
    

    if len(path) > 1:
        f_x, f_y = path[-1]
        food_x  = f_x - my_blobs[0]["coords"][0]
        food_y  = f_y - my_blobs[0]["coords"][1]
    else:
        food_x = random.randint(-1, 1)
        food_y = random.randint(-1, 1)

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
    await sio.connect("http://142.93.112.226:4004")
    await sio.emit("register", {"name": "elnardu" + str(random.randint(1, 100))})
    await sio.wait()


sio.on("action_request", action_request)
sio.on("error", error_handler)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start(sio))

