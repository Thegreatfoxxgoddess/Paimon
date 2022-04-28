from telegraph import upload_file

from paimon import Message, get_collection, paimon

SAVED = get_collection("TESTE_DB")


async def _init():
    global ALIVE_MEDIA  # pylint: disable=global-statement
    link = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    if link:
        ALIVE_MEDIA = link["link"]


@paimon.on_cmd(
    "settest",
    about={
        "header": "apenas teste",
    },
)
async def ani_save_media_alive(message: Message):
    """Set Media DB"""
    query = message.input_str
    replied = message.reply_to_message
    if replied:
        file = await paimon.download_media(replied)
        iurl = upload_file(file)
        media = f"https://telegra.ph{iurl[0]}"
        await SAVED.update_one(
            {"_id": "ALIVE_MEDIA"}, {"$set": {"link": media}}, upsert=True
        )
        await message.edit("`Alive Media definida com sucesso!`")
    elif query:
        await SAVED.update_one(
            {"_id": "ALIVE_MEDIA"}, {"$set": {"link": query}}, upsert=True
        )
        await message.edit("`Alive Media definida com sucesso!`")
    else:
        await message.err("Invalid Syntax")


@paimon.on_cmd(
    "vtest",
    about={
        "header": "Alive Media Settings",
        "flags": {"-d": "Delete test", "-v": "Ver test", "-a": "Send Animation"},
    },
)
async def view_del_ani(message: Message):
    """View or Delete Alive Media"""
    if not message.flags:
        await message.err("Flag Required")
        return
    media = ""
    msg = "ᴏɪ ᴍᴇsᴛʀᴇ, ᴋᴀɴɴᴀx ɪ'ᴛs ᴀʟɪᴠᴇ"
    async for link in SAVED.find():
        media += f"{link['link']}"
    if media:
        if "-d" in message.flags:
            await SAVED.drop()
            await message.edit("`Alive Media excluída!`")
        if "-v" in message.flags:
            await message.edit(media)
        if "-a" in message.flags:
            await message.client.send_animation(
                chat_id=message.chat.id, animation=media, caption=msg
            )
    else:
        await message.err("`Alive Media não está definida.`")
