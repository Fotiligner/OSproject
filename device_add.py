import json
import os

output_path = 'devices.jsonl'

with open(output_path, mode='a') as writer:
    dict = {}
    dict['name'] = "printer"
    dict["count"] = 3
    dict["type"] = "output"

    data = json.dumps(dict)
    writer.write(data)

with open(output_path, mode='a') as writer:
    dict = {}
    dict['name'] = "scanner"
    dict["count"] = 4
    dict["type"] = "input"

    data = json.dumps(dict)
    writer.write(data)

with open(output_path, mode='a') as writer:
    dict = {}
    dict['name'] = "keyboard"
    dict["count"] = 3
    dict["type"] = "input"

    data = json.dumps(dict)
    writer.write(data)