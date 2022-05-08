# Copyright (C) 2020 by paimonTeam@Github, < https://github.com/paimonTeam >.
#
# This file is part of < https://github.com/paimonTeam/paimon > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/paimon/blob/master/LICENSE >
#
# All rights reserved.

import traceback

import aiohttp

from paimon import Config, Message, logging, paimon, pool
from paimon.plugins.help import CHANNEL
from paimon.utils import post_to_telegraph as ptgh

_URL = "https://spaceb.in/" if Config.HEROKU_APP else "https://nekobin.com/"

_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


@paimon.on_cmd(
    "logs",
    about={
        "header": "check paimon-X logs",
        "flags": {
            "-d": "get logs in document",
            "-h": "get heroku logs",
            "-l": "heroku logs lines limit : default 100",
        },
    },
    allow_channels=False,
)
async def check_logs(message: Message):
    """check logs"""
    await message.edit("`checking logs ...`")
    if "-h" in message.flags and Config.HEROKU_APP:
        limit = int(message.flags.get("-l", 100))
        logs = await pool.run_in_thread(Config.HEROKU_APP.get_log)(lines=limit)
        await message.client.send_as_file(
            chat_id=message.chat.id,
            text=logs,
            filename="paimon-heroku.log",
            caption=f"paimon-heroku.log [ {limit} lines ]",
        )
    elif "-d" not in message.flags:
        try:
            with open("logs/paimon.log", "r") as d_f:
                text = d_f.read()
            async with aiohttp.ClientSession() as ses:
                async with ses.post(
                    _URL + "api/documents", json={"content": text}
                ) as resp:
                    if resp.status == 201:
                        try:
                            response = await resp.json()
                            key = response["result"]["key"]
                            file_ext = ".txt"
                            final_url = _URL + key + file_ext
                            final_url_raw = f"{_URL}raw/{key}{file_ext}"
                            reply_text = "**Here Are Your Logs** :\n"
                            reply_text += f"• [NEKO/SPACE]({final_url})            • [RAW]({final_url_raw})"
                            await message.edit(
                                reply_text, disable_web_page_preview=True
                            )
                            paste_ = True
                        except BaseException:
                            await paimon.send_message(
                                Config.LOG_CHANNEL_ID,
                                f"Failed to load <b>logs</b> in Neko/Spacebin,\n<b>ERROR</b>:`{traceback.format_exc()}`",
                            )
                            paste_ = False
                    if resp.status != 201 or not paste_:
                        await message.edit(
                            "`Failed to reach Neko/Spacebin! Sending as document...`",
                            del_in=5,
                        )
                        await CHANNEL.log(str(resp.status))
                        await message.client.send_document(
                            chat_id=message.chat.id,
                            document="logs/paimon.log",
                            caption="**paimon-X Logs**",
                        )
        except BaseException as e:
            await message.edit(
                "`Failed to reach Neko/Spacebin! Sending as document...`", del_in=5
            )
            await CHANNEL.log(f"<b>ERROR:</b> {e}")
            await message.client.send_document(
                chat_id=message.chat.id,
                document="logs/paimon.log",
                caption="**paimon-X Logs**",
            )
    else:
        await message.delete()
        await message.client.send_document(
            chat_id=message.chat.id,
            document="logs/paimon.log",
            caption="**paimon-X Logs**",
        )


@paimon.on_cmd(
    "setlvl",
    about={
        "header": "set logger level, default to info",
        "types": ["debug", "info", "warning", "error", "critical"],
        "usage": "{tr}setlvl [level]",
        "examples": ["{tr}setlvl info", "{tr}setlvl debug"],
    },
)
async def set_level(message: Message):
    """set logger level"""
    await message.edit("`setting logger level ...`")
    level = message.input_str.lower()
    if level not in _LEVELS:
        await message.err("unknown level !")
        return
    for logger in (logging.getLogger(name) for name in logging.root.manager.loggerDict):
        logger.setLevel(_LEVELS[level])
    await message.edit(
        f"`successfully set logger level as` : **{level.upper()}**", del_in=3
    )


@paimon.on_cmd(
    "tlogs",
    about={
        "header": "check paimon logs",
    },
    allow_channels=False,
)
async def tlogs(message: Message):
    with open("logs/paimon.log", "r") as d_f:
        text = d_f.read()
    link = ptgh(f"Paimon Logs", text)
    return await message.edit(
        f"Here are the [<b>logs</b>]({link}).",
        disable_web_page_preview=True,
    )
