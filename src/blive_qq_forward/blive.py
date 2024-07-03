# -*- coding: utf-8 -*-
import asyncio
import http.cookies
import logging

import aiohttp
from bilibili_api import CredentialNoSessdataException, login, user

import blivedm
import blivedm.models.web as web_models

logger = logging.getLogger(__package__)

# 直播间ID的取值看直播间URL
TEST_ROOM_IDS = [
    12235923,
    14327465,
    21396545,
    21449083,
    23105590,
]


async def main():
    logging.basicConfig(
        filename=f'{__package__}.log', level=logging.INFO, encoding="utf-8")
    logger.addHandler(logging.StreamHandler())

    # 这里填一个已登录账号的cookie的SESSDATA字段的值。不填也可以连接，但是收到弹幕的用户名会打码，UID会变成0
    sessdata = ""

    if not sessdata:
        try:
            cred = login.login_with_qrcode()
        except CredentialNoSessdataException:
            cred = None

        if cred is None or cred.sessdata is None:
            print("登录失败！")
        else:
            sessdata = cred.sessdata

    user_info = await user.get_self_info(credential=cred)
    print(f"登陆成功！欢迎回来，{user_info["name"]}")

    session = init_session(sessdata=sessdata)
    try:
        await run_multi_clients(session=session)
    finally:
        await session.close()


def init_session(sessdata: str = ""):
    cookies = http.cookies.SimpleCookie()
    cookies["SESSDATA"] = sessdata
    cookies["SESSDATA"]["domain"] = "bilibili.com"

    session = aiohttp.ClientSession()
    session.cookie_jar.update_cookies(cookies)
    return session


async def run_multi_clients(session):
    """
    演示同时监听多个直播间
    """
    clients = [
        blivedm.BLiveClient(room_id, session=session)
        for room_id in TEST_ROOM_IDS
    ]
    handler = MyHandler()
    for client in clients:
        client.set_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(client.join() for client in clients))
    finally:
        await asyncio.gather(*(client.stop_and_close() for client in clients))


class MyHandler(blivedm.BaseHandler):

    def _on_heartbeat(
        self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage
    ):
        logger.debug("[%d] %s", client.room_id, str(message))

    def _on_danmaku(
        self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage
    ):
        logger.info("[%d]-弹幕 %s：%s", client.room_id,
                    message.uname, message.msg)

    def _on_gift(self,
                 client: blivedm.BLiveClient,
                 message: web_models.GiftMessage):
        log = (
            f"[{client.room_id}] {message.uname} 赠送{
                message.gift_name}x{message.num}"
            f" （{message.coin_type}瓜子x{message.total_coin}）")
        logger.info(log)

    def _on_buy_guard(
        self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage
    ):
        log = f"[{client.room_id}] {message.username} 购买{message.gift_name}"
        logger.info(log)

    def _on_super_chat(
        self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage
    ):
        log = f"[{client.room_id}] 醒目留言 ¥{message.price} {
            message.uname}：{message.message}"
        logger.info(log)


if __name__ == "__main__":
    asyncio.run(main())
