# Modulo print by @Hitalo portado para paimon

from io import BytesIO

import httpx

from paimon import Message, paimon


@paimon.on_cmd(
    "print",
    about={
        "header": "Site Screenshot",
        "description": "Obtenha screenshot de algum site",
        "usage": "{tr}print [link]",
    },
)
async def printer(message: Message):
    text = message.input_str
    if not text:
        return await message.edit("Please specify a url")
    await message.edit("`taking screenshot...`")
    async with httpx.AsyncClient(http2=True, timeout=1000) as http:
        r = await http.get("https://amn-api.herokuapp.com/print", params=dict(q=text))
        bio = BytesIO(r.read())
    await http.aclose()
    bio.name = "screenshot.png"
    await message.delete()
    await message.client.send_document(chat_id=message.chat.id, photo=bio)
