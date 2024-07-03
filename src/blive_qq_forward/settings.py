import os

CONFIGURATION_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

appid = ""
secret = ""
super_admins: list[str] | None = None
channels: list[str] | None = None
room_ids: list[int] | None = None


def get_settings() -> dict:
    return {
        "appid": appid,
        "secret": secret,
        "super_admins": super_admins,
        "channels": channels,
        "room_ids": room_ids,
    }


def save_settings():
    import yaml

    with open(CONFIGURATION_PATH, "w", encoding="utf-8") as f:
        yaml.dump(get_settings(), f)
