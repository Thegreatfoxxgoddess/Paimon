# Plugin ytdl for paimon by @fnixdev
#
# for kangs check #tags

from __future__ import unicode_literals

import glob
import json
import os
from pathlib import Path

from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL

from paimon import Config, Message, paimon

from ..bot.utube_inline import BASE_YT_URL, get_yt_video_id

LOGGER = paimon.getLogger(__name__)


@paimon.on_cmd(
    "song",
    about={
        "header": "Music Downloader",
        "description": "Download songs using yt_dlp",
        "options": {"-f": "to download in flac format"},
        "examples": [
            "{tr}song link",
            "{tr}song name of song",
            "{tr}song -f name of song",
        ],
    },
)
async def song_(message: Message):
    query = message.input_str
    if not query:
        return await message.edit("`what do you want me to do?!`", del_in=5)
    await message.edit("`pls wait ...`")
    link = await get_link(query)
    aud_opts = {
        "outtmpl": os.path.join(Config.DOWN_PATH, "%(title)s.%(ext)s"),
        "logger": LOGGER,
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "format": "bestaudio/best",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            },
            {"key": "EmbedThumbnail"},
            {"key": "FFmpegMetadata"},
        ],
        "quiet": True,
    }
    filename_, capt_, duration_ = extract_inf(link, aud_opts)
    if filename_ == 0:
        _fpath = ""
        for _path in glob.glob(os.path.join(Config.DOWN_PATH, "*")):
            if not _path.lower().endswith((".jpg", ".png", ".webp")):
                _fpath = _path
        if not _fpath:
            await message.err("nothing found !")
            return
        await message.reply_audio(audio=Path(_fpath), caption=capt_, duration=duration_)
        os.remove(Path(_fpath))
    else:
        await message.edit(str(filename_))


@paimon.on_cmd(
    "video",
    about={
        "header": "Video Downloader",
        "description": "Download videos using yt_dlp",
        "examples": [
            "{tr}video link",
            "{tr}video video name",
        ],
    },
)
async def vid_(message: Message):
    query = message.input_str
    if not query:
        return await message.edit("`input smth ?!`", del_in=5)
    await message.edit("`hold on ...`")
    vid_opts = {
        "outtmpl": os.path.join(Config.DOWN_PATH, "%(title)s.%(ext)s"),
        "logger": LOGGER,
        "writethumbnail": False,
        "prefer_ffmpeg": True,
        "format": "bestvideo+bestaudio/best",
        "postprocessors": [{"key": "FFmpegMetadata"}],
        "quiet": True,
    }
    link = await get_link(query)
    await message.edit("`processing...`")
    filename_, capt_, duration_ = extract_inf(link, vid_opts)
    if filename_ == 0:
        _fpath = ""
        for _path in glob.glob(os.path.join(Config.DOWN_PATH, "*")):
            if not _path.lower().endswith((".jpg", ".png", ".webp")):
                _fpath = _path
        if not _fpath:
            return await message.err("nothing found !")
        await message.delete()
        await message.reply_video(video=Path(_fpath), caption=capt_, duration=duration_)
        os.remove(Path(_fpath))
    else:
        await message.edit(str(filename_))


# retunr regex link or get link with query
async def get_link(query):
    vid_id = get_yt_video_id(query)
    link = f"{BASE_YT_URL}{vid_id}"
    if vid_id is None:
        try:
            res_ = SearchVideos(query, offset=1, mode="json", max_results=1)
            link = json.loads(res_.result())["search_result"][0]["link"]
            return link
        except Exception as e:
            LOGGER.exception(e)
            return e
    else:
        return link


def extract_inf(url, _opts):
    try:
        x = YoutubeDL(_opts)
        infoo = x.extract_info(url, False)
        x.process_info(infoo)
        duration_ = infoo["duration"]
        title_ = infoo["title"].replace("/", "_")
        channel_ = infoo["channel"]
        views_ = infoo["view_count"]
        capt_ = f"<a href={url}><b>{title_}</b></a>\n❯ duration: {duration_}\n❯ Views: {views_}\n❯ channel: {channel_}"
        dloader = x.download(url)
    except Exception as y_e:  # pylint: disable=broad-except
        LOGGER.exception(y_e)
        return y_e
    else:
        return dloader, capt_, duration_
