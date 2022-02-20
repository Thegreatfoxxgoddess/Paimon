import os

import requests
from pyrogram.types import Message
from pyrogram.errors import MediaEmpty, WebpageCurlFailed
from wget import download
from paimon import Message, paimon

WALL_H_API = os.environ.get("WALL_H_API")


@paimon.on_cmd(
    "walls",
    about={
        "header": "Search Wallpaper",
        "description": "Search and Download Wallpapers from Nekos-life and upload to Telegram",
        "usage": "{tr}wall [Query]",
        "examples": "{tr}walls paimon",
    },
)
async def wall_(message: Message):
    request = requests.get("https://nekos.life/api/v2/img/wallpaper")
    grab = request.json().get("url")
    await message.client.send_document(
        message.chat.id,
        grab,
    )


@paimon.on_cmd(
    "wallpaper",
    about={
        "header": "Search Wallpaper",
        "description": "Search and Download Wallpapers from Nekos-life and upload to Telegram",
        "usage": "{tr}wall [Query]",
        "examples": "{tr}wall paimon",
    },
)
async def wall_(message: Message):
    await message.edit("`searching ...`", del_in=3)
    r = requests.get("https://wallhaven.cc/api/v1/collections")
    r.json().get("url")
    await send_walls(message, link)
except (MediaEmpty, WebpageCurlFailed):
    link = download(link)
    await send_walls(message, link)
    os.remove(link)


async def send_walls(message: Message, link: str):
    await message.client.send_photo(
        message.chat.id,
        g,
    )
