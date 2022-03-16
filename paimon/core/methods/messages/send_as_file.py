# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia

__all__ = ['SendAsFile']

import os
import inspect
from typing import Union, Optional

import aiofiles

from paimon import logging, Config
from paimon.utils import secure_text
from ...ext import RawClient
from ... import types

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  :::::  %s  :::::  !>>>"


class SendAsFile(RawClient):  # pylint: disable=missing-class-docstring
    async def send_as_file(self,
                           chat_id: Union[int, str],
                           text: str,
                           filename: str = "output.txt",
                           force_document: bool = True,
                           caption: str = '',
                           log: Union[bool, str] = False,
                           reply_to_message_id: Optional[int] = None) -> 'types.bound.Message':
        """\nYou can send large outputs as file

        Example:
                @paimon.send_as_file(chat_id=12345, text="hello")

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages)
                you can simply use "me" or "self".
                For a contact that exists in your Telegram address book
                you can use his phone number (str).

            text (``str``):
                Text of the message to be sent.

            filename (``str``, *optional*):
                file_name for output file.
                
            force_document (``bool``, *optional*):
                Pass True to force sending files as document. Useful for video files that need to be sent as
                document messages instead of video messages.
                Defaults to True.


            caption (``str``, *optional*):
                caption for output file.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

        Returns:
            On success, the sent Message is returned.
        """
        if text and chat_id not in Config.AUTH_CHATS:
            text = secure_text(str(text))
        async with aiofiles.open(filename, "w+", encoding="utf8") as out_file:
            await out_file.write(text)
        _LOG.debug(_LOG_STR, f"Uploading {filename} To Telegram")
        msg = await self.send_document(chat_id=chat_id,
                                       document=filename,
                                       force_document=True,
                                       caption=caption[:1024],
                                       disable_notification=True,
                                       reply_to_message_id=reply_to_message_id)
        os.remove(filename)
        module = inspect.currentframe().f_back.f_globals['__name__']
        if log:
            await self._channel.fwd_msg(msg, module if isinstance(log, bool) else log)
        return types.bound.Message.parse(self, msg, module=module)
