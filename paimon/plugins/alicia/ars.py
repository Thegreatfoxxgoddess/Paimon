# anime reverse search

import os

import tracemoepy
from aiohttp import ClientSession
from tracemoepy.errors import ServerError

from paimon import Config, Message, paimon
from paimon.utils import progress, take_screen_shot


@paimon.on_cmd(
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
    replied = message.reply_to_message
    if not replied:
        await message.edit("Ara Ara... Reply to a Media Senpai")
        return
    if not (replied.photo or replied.video or replied.animation):
        await message.err("Nani, reply to gif/photo/video")
        return
    if not os.path.isdir(Config.DOWN_PATH):
        os.makedirs(Config.DOWN_PATH)
    await message.edit("He he, let me use my skills")
    dls = await message.client.download_media(
        message=message.reply_to_message,
        file_name=Config.DOWN_PATH,
        progress=progress,
        progress_args=(message, "Downloading Media"),
    )
    dls_loc = os.path.join(Config.DOWN_PATH, os.path.basename(dls))
    if replied.animation or replied.video:
        img_loc = os.path.join(Config.DOWN_PATH, "trace.png")
        await take_screen_shot(dls_loc, 0, img_loc)
        if not os.path.lexists(img_loc):
            await message.err("Media not found...", del_in=5)
            return
        os.remove(dls_loc)
        dls_loc = img_loc
    if dls_loc:
        async with ClientSession() as session:
            tracemoe = tracemoepy.AsyncTrace(session=session)
            try:
                search = await tracemoe.search(dls_loc, upload_file=True)
            except ServerError:
                try:
                    search = await tracemoe.search(dls_loc, upload_file=True)
                except ServerError:
                    await message.reply("Couldnt parse results!!!")
                    return
            result = search["result"][0]
            caption_ = (
                f"**Title**: {result['anilist']['title']['english']}"
                f" (`{result['anilist']['title']['native']}`)\n"
                f"\n**Anilist ID:** `{result['anilist']['id']}`"
                f"\n**Similarity**: `{(str(result['similarity']*100))[:5]}`"
                f"\n**Episode**: `{result['episode']}`"
            )
            preview = result["video"]
        await message.reply_video(preview, caption=caption_)
        await message.delete()
