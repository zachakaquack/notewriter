import json


base_path = "/home/zach/Desktop/college/programming/python/mkdown/files"


def get_config():
    with open(f"{base_path}/settings.json", "r") as f:
        return json.load(f)


def get_notes_in_config():
    return get_config()["notes"]


def get_base_path():
    return base_path


def get_settings():
    return get_config()["settings"]
