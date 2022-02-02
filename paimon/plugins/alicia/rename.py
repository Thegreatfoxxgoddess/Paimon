from paimon import paimon 
import io
import os
import re
import time
from datetime import datetime
from pathlib import Path


@paimon.on_cmd(
    "r",
    about={
        "header": "Rename telegram files",
        "flags": {"-d": "upload as document", "-wt": "without thumb"},
        "usage": "{tr}rename [flags] [new_name_with_extension] : reply to telegram media",
        "examples": "{tr}rename -d test.mp4",
    },
    del_pre=True,
    check_downpath=True,
)
async def rename_(message: Message):
    """rename telegram files"""
    if not message.filtered_input_str:
        await message.err("new name not found!")
        return
    await message.edit("`Trying to Rename ...`")
    if message.reply_to_message and message.reply_to_message.media:
        await _handle_message(message)
    else:
        await message.edit("Please read `.help rename`", del_in=5)
