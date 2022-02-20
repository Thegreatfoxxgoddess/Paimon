import os

import requests
from pyrogram.errors import MediaEmpty, WebpageCurlFailed
from pyrogram.types import Message
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
    await message.paimon.send_document(
        message.chat.id,
        grab,
    )


@paimon.on_cmd(
    "wallpaper",
    about={
        "header": "fetch walls from WallHeaven",
        "flags": {
            "-n": "nsfw",
        },
        "usage": "{tr}walls",
    },
)
async def wall_heaven(message: Message):
    "fetch walls from WallHeaven"
    if WALL_H_API:
        api_ = WALL_H_API
        api_found = True
    else:
        api_found = False
    query_ = message.filtered_input_str
    if not query_:
        query_ = "wallpaper"
    link_ = "https://wallhaven.cc/api/v1/search"
    if api_found:
        link_ += f"?apikey={api_}"
    pure = "001" if "-n" in message.flags else "110"
    param = {"q": query_, "sorting": "random", "purity": pure}
    req = requests.get(link_, params=param)
    r = req.json().get("data")
    #    await message.reply_or_send_as_file(r)
    try:
        await paimon.send_document(message.chat.id, r[0]["url"])
    except (MediaEmpty, WebpageCurlFailed):
        download(r[0]["url"])
        await paimon.send_document(message.chat.id)
