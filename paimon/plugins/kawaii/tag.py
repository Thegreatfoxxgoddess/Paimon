import asyncio
import html
import os

from pyrogram.errors import (
    BadRequest,
    PeerIdInvalid,
    UsernameInvalid,
    UsernameNotOccupied,
    UsernameOccupied,
)
from paimon import Config, Message, paimon

LOG = paimon.getLogger(__name__)

PATH = Config.DOWN_PATH + "chat_pic.jpg"


def mention_html(user_id, name):
    return '<a href="tg://user?id={}">{}</a>'.format(user_id, html.escape(name))
    
    
    
    
    

@paimon.on_cmd(
    "all",
    about={
        "header": "Tagall recent 100 members with caption",
        "usage": "{tr}tagall [Text | reply to text Msg]",
    },
    allow_via_bot=True,
    allow_private=False,
)
async def tagall_(message: Message):
    """Tag recent members"""
    c_title = message.chat.title
    c_id = message.chat.id
    await message.edit(f"@all")
    message_id = replied.message_id if replied else None
    try:
        async for members in message.client.iter_chat_members(c_id, filter="recent"):
            if not members.user.is_bot:
                u_id = members.user.id
                u_name = members.user.username or None
                f_name = (await message.client.get_user_dict(u_id))["fname"]
                text += f"@{u_name} " if u_name else f"[{f_name}](tg://user?id={u_id}) "
    except Exception as e:
        text += " " + str(e)
    await message.client.send_message(c_id, text, reply_to_message_id=message_id)

