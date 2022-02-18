import requests
from pyrogram.types import Message

from paimon import Message, paimon


@paimon.on_cmd(
    "wallpaper",
    about={
        "header": "Search Wallpaper",
        "flags": {
            "-l": "Limit of Wallpapers",
            "-doc": "Send as Documents (Recommended)",
        },
        "description": "Search and Download Hd Wallpaper from Unsplash and upload to Telegram",
        "usage": "{tr}wall [Query]",
        "examples": "{tr}wall luffy",
    },
)
async def wall_(msg: Message):
    r = requests.get("https://nekos.life/api/v2/img/wallpaper")
    g = r.json().get("url")
    await paimon.send_document(
        message.chat.id,
        g,
    )
