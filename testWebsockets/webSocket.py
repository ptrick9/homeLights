import asyncio
import websockets
import json



configs = ['a', 'b', 'c', 'd', 'e']

colors = {'a':[0x123456, 0x234567, 0x345678]}





async def hello(websocket, path):
    name = await websocket.recv()

    if name == 'configs':
        c = {'command': 'config', 'config':configs}
        j = json.dumps(c)
        await websocket.send(j)
    elif 'detail' in name:
        configName = name.split(':')[1]
        c = {'command': 'data', 'config-name':configName, 'data':colors[configName]}
        j = json.dumps(c)
        await websocket.send(j)
    else:
        data = name.split(',')
        name = data[1]
        for color in data[2:]:
            print(color)


start_server = websockets.serve(hello, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()