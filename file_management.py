import json

"""
i completely forgot that this was even a thing but i thing
some things somewhere depend on it so i'll keep it in i guess
"""

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

def get_note_by_uuid(uuid):
    notes = get_notes_in_config()

    for note in notes:
        if uuid == note['uuid']:
            return note
