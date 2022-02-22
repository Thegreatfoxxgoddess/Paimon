import os

from paimon import Message, paimon
from paimon.helpers import msg_type


@paimon.on_cmd(
    "r",
    about={
        "header": "document to compressed media and vice versa",
        "flags": {
            "-d": "convert to document",
        },
        "usage": "{tr}comp [flag (optional)]",
    },
)
async def compress_(message: Message):
    """document to compressed media and vice versa"""
    reply_ = message.reply_to_message
    if not reply_:
        return await message.edit("`Reply to media...`", del_in=5)
    down_ = await paimon.download_media(reply_)
    if "-d" in message.flags:
        await message.reply("`Processing document...`")
        await paimon.send_document(
            message.chat.id,
            down_,
            force_document=True,
            reply_to_message_id=reply_.message_id,
        )
        await message.delete()
        os.remove(down_)
        return
    await message.reply("`Compressing...`")
    if msg_type(reply_) == "photo":
        await paimon.send_photo(
            message.chat.id, down_, reply_to_message_id=reply_.message_id
        )
    elif msg_type(reply_) == "video":
        await paimon.send_video(
            message.chat.id, down_, reply_to_message_id=reply_.message_id
        )
    else:
        await reply_.reply("The replied document is not compressible...", del_in=5)
    await message.delete()
    os.remove(down_)
