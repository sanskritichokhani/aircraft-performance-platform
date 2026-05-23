import json

def load_aircraft(filepath):
    with open(filepath, "r") as f:
        return json.load(f)