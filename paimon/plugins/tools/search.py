# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia

from paimon import Message, paimon


@paimon.on_cmd(
    "s",
    about={"header": "procure comandos no paimon", "examples": "{tr}s wel"},
    allow_channels=False,
)
async def search(message: Message):
    cmd = message.input_str
    if not cmd:
        await message.err(text="Insira uma palavra para procurar um comando")
        return
    found = [i for i in sorted(list(paimon.manager.enabled_commands)) if cmd in i]
    out_str = "    ".join(found)
    if found:
        out = f"**--Eu encontrei ({len(found)}) comandos para-- : `{cmd}`**\n\n`{out_str}`"
    else:
        out = f"__nenhum comando encontrado para__ : `{cmd}`"
    await message.edit(text=out, del_in=0)
