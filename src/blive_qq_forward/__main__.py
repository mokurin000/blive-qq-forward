# -*- coding: utf-8 -*-
import asyncio

import botpy
from botpy.ext.cog_yaml import read
from botpy.errors import ServerError

from blive_qq_forward import blive, settings
from blive_qq_forward.blive import init_logs
from blive_qq_forward.blive import make_multiple_clients, init_session_with_login
from blive_qq_forward.myclient import MyClient
from blive_qq_forward.settings import CONFIGURATION_PATH


bot_config = read(CONFIGURATION_PATH)


def load_settings():
    settings.appid = bot_config["appid"]
    settings.secret = bot_config["secret"]
    settings.super_admins = bot_config["super_admins"]
    settings.channels = bot_config["channels"]
    settings.room_ids = bot_config["room_ids"]


async def main():
    init_logs()
    load_settings()

    intents = botpy.Intents(public_guild_messages=True, message_audit=True)

    session = await init_session_with_login()

    client = MyClient(intents=intents)
    blive.qqbot_client = client
    blive_clients = make_multiple_clients(session=session, room_ids=settings.room_ids)

    try:
        await client.start(appid=settings.appid, secret=settings.secret)
    except ServerError:
        pass

    try:
        await asyncio.gather(*(client.join() for client in blive_clients))
    finally:
        await asyncio.gather(*(client.stop_and_close() for client in blive_clients))


if __name__ == "__main__":
    asyncio.run(main())
