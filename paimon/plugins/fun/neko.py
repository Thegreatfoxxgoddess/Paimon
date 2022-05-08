import re

import httpx

from paimon import Message, paimon


@paimon.on_cmd(
    "neko",
    about={
        "header": "Get stuff from nekos.life",
        "usage": "{tr}neko",
    },
)
async def random_neko(message: Message):
    while True:
        await message.delete()
        reply = message.reply_to_message
        reply_id = reply.message_id if reply else None
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get("https://nekos.life/")
            midia = re.findall(
                r"<meta property=\"og:image\" content=\"(.*)\"/>", r.text
            )[0]
            return await message.client.send_photo(
                chat_id=message.chat.id, photo=midia, reply_to_message_id=reply_id
            )
        except BaseException:
            pass


@paimon.on_cmd(
    "cat",
    about={
        "header": "get kittens",
        "usage": "{tr}cat",
    },
)
async def random_cat(message: Message):
    async with httpx.AsyncClient() as client:
        reply = message.reply_to_message
        reply_id = reply.message_id if reply else None
        r = await client.get("https://api.thecatapi.com/v1/images/search")
    if not r.status_code == 200:
        return await message.edit(f"<b>Error!</b> <code>{r.status_code}</code>")
    cat = r.json
    await message.delete()
    await message.client.send_photo(
        chat_id=message.chat.id, photo=(cat()[0]["url"]), reply_to_message_id=reply_id
    )


@paimon.on_cmd(
    "dog",
    about={
        "header": "get puppies",
        "usage": "{tr}dog",
    },
)
async def random_dog(message: Message):
    async with httpx.AsyncClient() as client:
        reply = message.reply_to_message
        reply_id = reply.message_id if reply else None
        r = await client.get("https://api.thedogapi.com/v1/images/search")
    if not r.status_code == 200:
        return await message.edit(f"<b>Error!</b> <code>{r.status_code}</code>")
    dog = r.json
    await message.delete()
    await message.client.send_photo(
        chat_id=message.chat.id, photo=(dog()[0]["url"]), reply_to_message_id=reply_id
    )
