# image convert by @eightbituwu

import os

from PIL import Image

from paimon import Message, paimon


@paimon.on_cmd(
    "png",
    about={
        "header": "Convert telegram files",
        "usage": "reply {tr}png on some photo/sticker",
    },
)
async def convert_(message: Message):
    """convert telegram files"""
    replied = message.reply_to_message
    await message.edit("`processing...`")
    if not replied:
        return await message.err("`Reply to some media.`")
    media = await message.reply_to_message.download()
    if not media.endswith(
        (".jpg", ".gif", ".png", ".bmp", ".tif", ".webm", ".webp" ".mp3")
    ):
        os.remove(media)
        return await message.err("`not supported`")
    try:
        await message.edit("`converting...`")
        img = Image.open(media).convert("RGB")
        img.save("converted.png", "png")
        await message.delete()
        msg = "__Made by [paimon](https://t.me/candys_bot)__"
        await message.client.send_document(
            chat_id=message.chat.id, document="converted.png", caption=msg
        )
    except Exception as e:
        return message.err(e)
    os.remove(media)
    os.remove("converted.png")
