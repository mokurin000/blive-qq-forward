# -*- coding: utf-8 -*-
import os
from datetime import datetime

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()
_start = datetime.now()


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_at_message_create(self, message: Message):
        """
        消息回调
        """

        channel_id = message.channel_id
        username = message.author.username
        guild_id = message.guild_id

        _log.info(
            f"received {message.content} by {username} from {guild_id}-{channel_id}"
        )

        if message.content.strip().endswith("/状态"):
            roles = await self.api.get_guild_roles(guild_id)
            print(roles)

        await self.api.post_message(
            channel_id=channel_id,
            content=(
                "你好呀~ 我是Blive推送姬，请多多指教~\n"
                f"username: {username}\n"
                f"gulid_id: {guild_id}\n"
                f"channel_id: {channel_id}\n"
            ),
        )


if __name__ == "__main__":
    intents = botpy.Intents(public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])
