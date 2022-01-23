# plugin made for paimon by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi


import asyncio

from pyrogram.errors import FloodWait, PeerIdInvalid

from paimon import Config, Message, get_collection, paimon
from paimon.helpers import admin_or_creator, msg_type
from paimon.helpers.paimon_tools import get_response

COPIED = get_collection("COPIED")


CHANNEL = paimon.getCLogger(__name__)


@paimon.on_cmd(
    "postch",
    about={
        "header": "copy your channel content",
        "description": "copy your channel content from one channel to another",
        "usage": "{tr}copy_ch [from_channel_id] [to_channel_id] delay",
    },
)
async def copy_channel_(message: Message):
    """copy channel content"""
    delay = str(0.1)
    await message.edit("`Checking channels...`")
    me_ = await paimon.get_me()
    input_ = message.input_str
    from_chann = input_.split()[0]
    to_chann = input_.split()[1]
    try:
        try:
            from_chann = int(from_chann)
        except BaseException:
            pass
        from_ = await paimon.get_chat(from_chann)
    except BaseException as e:
        return await message.edit(
            f"`Given from_channel '{from_chann}' is invalid...`\nERROR: {str(e)}",
            del_in=5,
        )
    try:
        try:
            to_chann = int(to_chann)
        except BaseException:
            pass
        to_ = await paimon.get_chat(to_chann)
        delay = float(delay) if "." in delay else int(delay)
    except BaseException:
        return await message.edit(
            f"`Given to_channel '{to_chann}' is invalid...`", del_in=5
        )
    if from_.type != "channel" or to_.type != "channel":
      delay = split(" ", maxsplit=1)
    try:
      delay = float(delay) if "." in delay else int(delay)
    except ValueError as e:
            await message.edit(e)
            await message.reply_sticker(sticker="CAACAgIAAx0CW6USIQACCwVh62uAu8M5kiBQgKbj8R3s9xEtQQAC6AAD-H-lCtLIOj4Om6I7HgQ")
    return
        return await message.edit(
            "`One or both of the given chat is/are not channel...`", del_in=5
        )
    from_owner = await admin_or_creator(from_.id, me_.id)
    if not from_owner["is_admin"] and not from_owner["is_creator"]:
        return await message.edit(
            f"`Owner or admin required in ('{from_.title}') to copy posts...`", del_in=5
        )
    to_admin = await admin_or_creator(to_.id, me_.id)
    if not to_admin["is_admin"] and not to_admin["is_creator"]:
        return await message.edit(
            f"Need admin rights to copy posts to {to_.title}...", del_in=5
        )
    total = 5
    list_ = []
    await message.edit(
        f"`Copying posts from `<b>{from_.title}</b>` to `<b>{to_.title}</b>..."
    )
    async for post in paimon.search_messages(from_.id):
        list_.append(post.message_id)
    list_.reverse()
    try:
        for one_msg in list_:
            await paimon.copy_message(to_.id, from_.id, one_msg)
            total += 10
    except FloodWait as e:
        await asyncio.sleep(delay)
    except Exception as e:
        await CHANNEL.log(f"ERROR: {str(e)}")
        return await message.edit(
            "`Something went wrong, see log channel for error...`"
        )
    out_ = f"`Forwarded <b>{total}</b> from <b>{from_.title}</b> to <b>{to_.title}</b>`.`"
    await message.edit(out_)
    await CHANNEL.log(out_)
