import json

"""
i completely forgot that this was even a thing but i thing
some things somewhere depend on it so i'll keep it in i guess
"""

base_path = "/home/zach/Desktop/college/programming/python/mkdown/files"


def get_config() -> dict:
    with open(f"{base_path}/settings.json", "r") as f:
        return json.load(f)

def write_json(dictionary: dict) -> None:
    with open(f"{base_path}/settings.json", "w") as f:
        f.write(json.dumps(dictionary, indent=4))

def create_file(filename: str) -> None:
    path = get_base_path()
    with open(f"{path}/{filename}", "w") as f:
        f.write("")

def get_text_in_file(filename: str) -> str:
    path = get_base_path()
    with open(f"{path}/{filename}", "r") as f:
        return f.read()

def write_to_file(filename: str, contents: str) -> None:
    path = get_base_path()
    with open(f"{path}/{filename}", "w") as f:
        f.write(contents)

def get_notes_in_config() -> dict:
    return get_config()["notes"]


def get_base_path() -> str:
    return base_path


def get_settings():
    return get_config()["settings"]

def get_note_by_uuid(uuid: str) -> dict:
    notes = get_notes_in_config()

    for note in notes:
        if uuid == note['uuid']:
            return note
    else:
        return {}
