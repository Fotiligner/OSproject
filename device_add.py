import json
import os

output_path = 'device.json'

with open(output_path, mode='w') as writer:
    dict = {}
    dict['printer'] = 3
    dict['scanner'] = 4
    dict['keyboard'] = 2

    data = json.dumps(dict)
    writer.write(data)