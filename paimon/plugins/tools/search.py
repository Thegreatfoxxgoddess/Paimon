# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia

from paimon import Message, paimon


@paimon.on_cmd(
    "s",
    about={"header": "search commands in paimon", "examples": "{tr}s wel"},
    allow_channels=False,
)
async def search(message: Message):
    cmd = message.input_str
    if not cmd:
        await message.err(text="Enter any keyword to search in commands")
        return
    found = [i for i in sorted(list(paimon.manager.enabled_commands)) if cmd in i]
    out_str = "`\n`".join(found)
    if found:
        out = f"**--I found [{len(found)}] commands for-- : `{cmd}`**\n\n`{out_str}`"
    else:
        out = f"__command not found for__ : `{cmd}`"
    await message.edit(text=out, del_in=0)
