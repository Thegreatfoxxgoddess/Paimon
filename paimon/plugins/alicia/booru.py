import random

import requests

from paimon import Message, paimon


@paimon.on_cmd(
    "boru",
    about={"download images from danbooru"},
)
async def booru(message: Message):
    query = message.input_str
    resp = requests.get(f"https://danbooru.donmai.us/posts.json?tags={query}")
    link = resp.json()
    r = random.choice(link)
    pic = r["large_file_url"]
    if "-d" in message.flags:
        await message.reply_document(pic)
    else:
        await message.reply_photo(pic)
