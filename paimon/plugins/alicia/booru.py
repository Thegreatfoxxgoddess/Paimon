### By Ryuk ###


import asyncio
import json
import os
from random import choice

from booru import Gelbooru
from pyrogram.errors import MediaEmpty, WebpageCurlFailed
from paimon import Message, paimon
from wget import download

client = Gelbooru()


@paimon.on_cmd(
    "booru",
    about={
        "header": "Get images from Danbooru",
        "usage": " {tr}booru query\n",
        "flags": " -a : to get 10 results.",
    },
)
async def get_booru(message: Message):
    query_ = message.filtered_input_str
    try:
        booru = json.loads(
            await client.get_image(query=query_.replace(" ", "_"), limit=69, page=1)
        )
    except ValueError:
        return await message.edit("No results found, Check the query.", del_in=5)
    count = 0
    if "-a" in message.flags:
        while count < 10:
            _media = choice(booru)
            try:
                count +=1
                await send_booru(message, _media)
            except (MediaEmpty, WebpageCurlFailed):
                count -=1
    else:
        _media = choice(booru)
        try:
            await send_booru(message, _media)
        except (MediaEmpty, WebpageCurlFailed):
            _media = download(_media)
            await send_booru(message, _media)
            os.remove(_media)


async def send_booru(message: Message, _media: str):
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else None
    if _media.lower().endswith((".gif", ".mp4")):
        await message.reply_video(video=_media, reply_to_message_id=reply_id)
    elif _media.lower().endswith((".jpeg", ".jpg", ".png", ".webp")):
        await message.reply_photo(photo=_media, reply_to_message_id=reply_id)
