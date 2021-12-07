""" Sangmata """

# By @Krishna_Singhal

from pyrogram.errors.exceptions.bad_request_400 import YouBlockedUser

from paimon import Message, paimon
from paimon.utils.exceptions import StopConversation


@paimon.on_cmd(
    "sg",
    about={
        "header": "Sangmata gives you user's last updated names and usernames.",
        "flags": {"-u": "To get Username history of a User"},
        "usage": "{tr}sg [Reply to user]\n" "{tr}sg -u [Reply to user]",
    },
)
async def sangmata_(message: Message):
    """Get User's Updated previous Names and Usernames"""
    replied = message.reply_to_message
    if not replied:
        await message.err("```Reply to get Name and Username History...```", del_in=5)
        return
    user = replied.from_user.id
    chat = "@Sangmatainfo_bot"
    await message.edit("```Getting info, please wait...```")
    msgs = []
    ERROR_MSG = "For your kind information, you blocked @Sangmatainfo_bot, Unblock it"
    try:
        async with paimon.conversation(chat) as conv:
            try:
                await conv.send_message("/search_id {}".format(user))
            except YouBlockedUser:
                await message.err(f"**{ERROR_MSG}**", del_in=5)
                return
            msgs.append(await conv.get_response(mark_read=True))
            msgs.append(await conv.get_response(mark_read=True))
            msgs.append(await conv.get_response(timeout=3, mark_read=True))
    except StopConversation:
        pass
    name = "Name History"
    username = "Username History"
    for msg in msgs:
        if "-u" in message.flags:
            if msg.text.startswith("No records found"):
                await message.edit(
                    "```User never changed his/her Username...```", del_in=20
                )
                return
            if msg.text.startswith(username):
                await message.edit(f"`{msg.text}`")
        else:
            if msg.text.startswith("No records found"):
                await message.edit(
                    "```User never changed his/her Name...```", del_in=20
                )
                return
            if msg.text.startswith(name):
                await message.edit(f"`{msg.text}`")
