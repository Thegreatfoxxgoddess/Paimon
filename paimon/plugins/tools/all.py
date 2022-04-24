# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia

from paimon import Message, paimon

from .. import get_all_plugins


@paimon.on_cmd("plugins", about={"header": "list all plugins in plugins/ path"})
async def getplugins(message: Message):
    raw_ = get_all_plugins()
    out_str = f"**--({len(raw_)}) Plugins Available!--**\n\n"
    for plugin in ("/".join(i.split(".")) for i in raw_):
        out_str += f"    `{plugin}.py`\n"
    await message.edit(text=out_str, del_in=0)
