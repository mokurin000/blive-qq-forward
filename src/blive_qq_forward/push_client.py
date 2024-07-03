from datetime import datetime

import botpy
from botpy import logging
from botpy.errors import ServerError
from botpy.message import Message, MessageAudit

from blive_qq_forward import settings
from blive_qq_forward.settings import save_settings

_log = logging.get_logger()
_start = datetime.now()


class PushClient(botpy.Client):
    async def on_ready(self):
        assert self.robot is not None
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_at_message_create(self, message: Message):
        """
        消息回调
        """

        channel_id = message.channel_id
        username = message.author.username
        user_id = message.author.id
        guild_id = message.guild_id

        super_admins = settings.super_admins
        channels = settings.channels

        _log.info(
            f"received {message.content} by {username} from {guild_id}-{channel_id}"
        )

        msg = "你好呀~ 我是Blive推送姬，请多多指教~"
        command = message.content.strip()

        if command.endswith("/菜单"):
            msg = (
                "/菜单 显示当前菜单\n"
                "/状态 显示用户、频道ID\n"
                "/启用 启用频道推送\n"
                "/禁用 禁用频道推送\n"
            )

        if command.endswith("/状态"):
            dur_secs = int((datetime.now() - _start).total_seconds())
            dur_mins = dur_secs // 60
            dur_secs = dur_secs % 60
            dur_hours = dur_mins // 60
            dur_mins = dur_mins % 60
            dur_days = dur_hours // 24
            dur_hours = dur_hours % 24
            msg = (
                f"username: {username}\n"
                f"user_id: {user_id}\n"
                f"gulid_id: {guild_id}\n"
                f"channel_id: {channel_id}\n"
                "\n"
                f"已运行时间：{dur_days}d{dur_hours}h{dur_mins}m{dur_secs}s"
            )

        if command.endswith("/启用"):
            # pylint: disable=unsupported-membership-test
            if super_admins is not None and user_id in super_admins:
                if message.channel_id not in channels:
                    channels.append(channel_id)
                    msg = f"频道 {channel_id} 启用成功！"
                    _log.info(f"已启用频道 {channel_id} 的推送")
                    save_settings()
                else:
                    msg = f"频道 {channel_id} 已启用！"

            else:
                _log.warn(f"非法命令！{username} ({user_id})")
                msg = f"很抱歉，{username}，您无权使用该命令！\n管理员列表：\n{"\n".join(super_admins)}"

        if command.endswith("/禁用"):
            # pylint: disable=unsupported-membership-test
            if super_admins is not None and user_id in super_admins:
                if message.channel_id in channels:
                    channels.remove(channel_id)
                    msg = f"频道 {channel_id} 禁用成功！"
                    _log.info(f"已禁用频道 {channel_id} 的推送")
                    save_settings()
                else:
                    msg = f"频道 {channel_id} 已禁用！"

            else:
                _log.warn(f"非法命令！{username} ({user_id})")
                msg = f"很抱歉，{username}，您无权使用该命令！\n管理员列表：\n{"\n".join(super_admins)}"

        await self.send_message(channel_id=channel_id, content=msg, msg_id=message.id)

    async def on_message_audit_pass(self, message: MessageAudit):
        """
        监听审核通过
        """
        _log.info(f"Message {message.message_id} passed audit!")

    async def on_message_audit_reject(self, message: MessageAudit):
        """
        监听审核不通过
        """
        _log.warn(f"Message {message.message_id} was rejected!")

    async def send_message(self, channel_id: str, content: str, **kwargs):
        try:
            await self.api.post_message(
                channel_id=channel_id,
                content=content,
                **kwargs,
            )
        except ServerError:
            # 跳过审查报错
            pass
