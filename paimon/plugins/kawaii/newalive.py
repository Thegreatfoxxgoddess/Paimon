# new alive plugin for paimon edited by @eightbituwu

"""new alive for paimon"""

from telegraph import upload_file

from paimon import Message, get_collection, get_version, paimon
from paimon.plugins.bot.alive import Bot_Alive
from paimon.utils import rand_array
from paimon.versions import __python_version__

SAVED = get_collection("ALIVE_DB")

ALIVE_MSG = {}


async def _init():
    global ALIVE_MEDIA, ALIVE_MSG  # pylint: disable=global-statement
    link = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    if link:
        ALIVE_MEDIA = link["link"]
    _AliveMsg = await SAVED.find_one({"_id": "CUSTOM_MSG"})
    if _AliveMsg:
        ALIVE_MSG = _AliveMsg["data"]


@paimon.on_cmd(
    "setamedia",
    about={
        "header": "Set alive media",
        "description": "Voçê pode definir uma mídia para aparecer em seu Alive",
    },
)
async def ani_save_media_alive(message: Message):
    """set media alive"""
    query = message.input_str
    replied = message.reply_to_message
    if replied:
        file = await paimon.download_media(replied)
        iurl = upload_file(file)
        media = f"https://telegra.ph{iurl[0]}"
        await SAVED.update_one(
            {"_id": "ALIVE_MEDIA"}, {"$set": {"link": media}}, upsert=True
        )
        await message.edit("`Alive Media definida com sucesso!`", del_in=5, log=True)
    elif query:
        await SAVED.update_one(
            {"_id": "ALIVE_MEDIA"}, {"$set": {"link": query}}, upsert=True
        )
        await message.edit("`Alive Media definida com sucesso!`", del_in=5, log=True)
    else:
        await message.err("Invalid Syntax")


@paimon.on_cmd(
    "setamsg",
    about={
        "header": "Define uma mensagem para alive",
        "description": "Voçê pode definir uma mensagem para aparecer em seu Alive",
    },
)
async def save_msg_alive(message: Message):
    """set alive msg"""
    rep = message.input_or_reply_str
    if not rep:
        return await message.edit(
            "`Você precisa digitar ou responder a uma mensagem pra salva-la`", del_in=6
        )
    if rep:
        await SAVED.update_one(
            {"_id": "ALIVE_MSG"}, {"$set": {"data": rep}}, upsert=True
        )
        await message.edit(
            "`Mensagem para alive definida com sucesso!`", del_in=5, log=True
        )
    else:
        await message.err("Invalid Syntax")


@paimon.on_cmd(
    "ialive",
    about={
        "header": "Alive apenas",
    },
)
async def view_del_ani(message: Message):
    """new alive"""
    _findpma = await SAVED.find_one({"_id": "ALIVE_MEDIA"})
    _findamsg = await SAVED.find_one({"_id": "ALIVE_MSG"})
    if _findpma is None:
        return await message.err("`Alive Media não está definida.`", del_in=5)
    if _findamsg is None:
        mmsg = rand_array(FRASES)
    else:
        mmsg = _findamsg.get("data")
    media = _findpma.get("link")
    msg = "hey there, paimon is here 💕💕"
    alive_msg = f"""
{msg}

{mmsg}
    ✨ [lil ol meh](https://t.me/eightbituwu) | 👾 [repo](https://github.com/Thegreatfoxxgoddess/Paimon)
"""
    if media.endswith((".gif", ".mp4")):
        await message.client.send_animation(
            chat_id=message.chat.id, animation=media, caption=alive_msg
        )
    else:
        await message.client.send_photo(
            chat_id=message.chat.id, photo=media, caption=alive_msg
        )
    await message.delete()


@paimon.on_cmd(
    "delamsg",
    about={
        "header": "Delete alive message",
        "description": "Returns Alive's message to default",
    },
)
async def del_a_msg(message: Message):
    """del msg alive"""
    _findamsg = await SAVED.find_one({"_id": "ALIVE_MSG"})
    if _findamsg is None:
        await message.edit("`You haven't set a message for Alive yet`", del_in=5)
    else:
        await SAVED.find_one_and_delete({"_id": "ALIVE_MSG"})
        await message.edit("`Alive msg excluida`", del_in=5, log=True)


FRASES = (
    "morning cutie",
    "hello mommy",
    "ohayo onisan",
    "yamete",
    "yamero",
)
