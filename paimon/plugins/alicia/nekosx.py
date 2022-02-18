import re

import httpx
import requests
from pyrogram import Client, filters, types
from pyrogram.types import Message

from paimon import paimon


@paimon.on_message(filters.command("baka"))
async def baka_(_, message: Message):
    r = requests.get("https://nekos.life/api/v2/img/baka")
    g = r.json().get("url")
    await message.reply_animation(g)


@paimon.on_message(filters.command(["wall", "wallpaper"]))
async def baka_(_, message: Message):
    r = requests.get("https://nekos.life/api/v2/img/wallpaper")
    g = r.json().get("url")
    await paimon.send_document(message.chat.id, g, caption="__Send by:__ @paimon")
