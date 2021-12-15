import os

import tracemoepy
from aiohttp import ClientSession

from paimon import Config, Message, paimon
from paimon.utils import progress, take_screen_shot


@paimonx.on_cmd(
    "ars",
    about={
        "header": "Anime Reverse Search",
        "description": "Reverse Search any anime by providing "
        "a snap, or short clip of anime.",
        "usage": "{tr}ars [reply to Photo/Gif/Video]",
    },
)
async def trace_bek(message: Message):
    """Reverse Search Anime Clips/Photos"""
    dls_loc = await media_to_image(message)
    if dls_loc:
        async with ClientSession() as session:
            tracemoe = tracemoepy.AsyncTrace(session=session)
            search = await tracemoe.search(dls_loc, upload_file=True)
            os.remove(dls_loc)
            result = search["docs"][0]
            caption = (
                f"**Title**: **{result['title_english']}**\n"
                f"   🇯🇵 (`{result['title_romaji']} - {result['title_native']}`)\n"
                f"\n**Anilist ID:** `{result['anilist_id']}`"
                f"\n**Similarity**: `{result['similarity']*100}`"
                f"\n**Episode**: `{result['episode']}`"
            )
            preview = await tracemoe.natural_preview(search)
        with open("preview.mp4", "wb") as f:
            f.write(preview)
        await message.reply_video("preview.mp4", caption=caption)
        os.remove("preview.mp4")
        await message.delete()
