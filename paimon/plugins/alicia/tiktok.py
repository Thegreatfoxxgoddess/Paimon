# tiktok downloader

import os

from wget import download

from paimon import Config, Message, paimon
from paimon.utils import get_response

API = "https://hadi-api.herokuapp.com/api/tiktok"


@paimon.on_cmd(
    "tiktok",
    about={
        "header": "Tiktok Downloader",
        "description": "download tiktok videos with link",
        "usage": "{tr}tiktok link",
    },
)
async def ttdown_(message: Message):
    link = message.input_or_reply_str
    await message.edit("`pls wait...`")
    if "tiktok.co" not in link:
        return await message.edit("`This is not a tiktok link`")
    params = {
        "url": link,
    }
    try:
        response = await get_response.json(link=API, params=params)
    except ValueError:
        return await message.err("API Inactive", del_in=5)
    if not response["status"] == 200:
        return await message.err(
            "There was an error querying the video data, check if you entered the link correctly.",
            del_in=10,
        )
    await message.edit("`Processing...`")
    link_v = response["result"]["video"]["original"]
    vid = download(link_v, Config.DOWN_PATH)
    os.rename(vid, f"{Config.DOWN_PATH}video.mp4")

    await message.client.send_video(message.chat.id, f"{Config.DOWN_PATH}video.mp4")
    await message.delete()
    os.remove(f"{Config.DOWN_PATH}video.mp4")
