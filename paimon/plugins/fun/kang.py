""" kang stickers """

# Copyright (C) 2020 by paimonTeam@Github, < https://github.com/paimonTeam >.
#
# This file is part of < https://github.com/paimonTeam/paimon > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/paimon/blob/master/LICENSE >
#
# All rights reserved.

import io
import os

from bs4 import BeautifulSoup as bs
from PIL import Image
from pyrogram import emoji
from pyrogram.errors import StickersetInvalid, YouBlockedUser
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName

from paimon import Config, Message, get_collection, paimon
from paimon.helpers import Media_Info
from paimon.utils import get_response, runcmd

SAVED_SETTINGS = get_collection("CONFIGS")


async def _init() -> None:
    found = await SAVED_SETTINGS.find_one({"_id": "LOG_KANG"})
    if found:
        Config.LOG_KANG = found["switch"]
    else:
        Config.LOG_KANG = True


@paimon.on_cmd(
    "log_kang",
    about={
        "header": "toggle 'kang in log channel' switch",
        "flags": {
            "-c": "check",
        },
        "usage": "{tr}log_kang",
    },
)
async def log_kang(message: Message):
    if "-c" in message.flags:
        out_ = "ON" if Config.LOG_KANG else "OFF"
        return await message.edit(f"`Logging kang in channel is {out_}.", del_in=5)
    if Config.LOG_KANG:
        Config.LOG_KANG = False
        await SAVED_SETTINGS.update_one(
            {"_id": "LOG_KANG"}, {"$set": {"switch": False}}, upsert=True
        )
    else:
        Config.LOG_KANG = True
        await SAVED_SETTINGS.update_one(
            {"_id": "LOG_KANG"}, {"$set": {"switch": True}}, upsert=True
        )


@paimon.on_cmd(
    "kang",
    about={
        "header": "kangs stickers or creates new ones",
        "flags": {
            "-s": "without link",
            "-d": "without trace",
            "-f": "fast-forward video stickers to fit in 3 seconds",
        },
        "usage": "Reply {tr}kang [emoji('s)] [pack number] to a sticker or "
        "an image to kang it to your userbot pack.",
        "examples": [
            "{tr}kang",
            "{tr}kang -s",
            "{tr}kang -d",
            "{tr}kang ✨",
            "{tr}kang 2",
            "{tr}kang ✨ 2",
        ],
    },
    allow_channels=False,
    allow_via_bot=False,
)
async def kang_(message: Message):
    """kang a sticker"""
    user = await paimon.get_me()
    replied = message.reply_to_message
    if Config.LOG_KANG:
        await message.edit("`me stealing this...`", del_in=6)
        kang_msg = await paimon.send_message(
            Config.LOG_CHANNEL_ID, "`theft in progress...`"
        )
    else:
        kang_msg = await message.edit("`me stealing this...`")
    media_ = None
    emoji_ = None
    is_anim = False
    is_video = False
    resize = False
    ff_vid = False
    if replied and replied.media:
        if replied.photo:
            resize = True
        elif replied.document and "image" in replied.document.mime_type:
            resize = True
            replied.document.file_name
        elif replied.document and "tgsticker" in replied.document.mime_type:
            is_anim = True
            replied.document.file_name
        elif replied.document and "video" in replied.document.mime_type:
            resize = True
            is_video = True
            ff_vid = True if "-f" in message.flags else False
        elif replied.animation:
            resize = True
            is_video = True
            ff_vid = True if "-f" in message.flags else False
        elif replied.video:
            resize = True
            is_video = True
            ff_vid = True if "-f" in message.flags else False
        elif replied.sticker:
            if not replied.sticker.file_name:
                await kang_msg.edit("`Sticker has no Name!`")
                return
            emoji_ = replied.sticker.emoji
            is_anim = replied.sticker.is_animated
            is_video = replied.sticker.is_video
            if not (
                replied.sticker.file_name.endswith(".tgs")
                or replied.sticker.file_name.endswith(".webm")
            ):
                resize = True
                ff_vid = True if "-f" in message.flags else False
        else:
            await kang_msg.edit("`Unsupported File!`")
            return
        await kang_msg.edit(f"`{KANGING_STR}`")
        media_ = await paimon.download_media(
            message=replied, file_name=f"{Config.DOWN_PATH}"
        )
    else:
        await kang_msg.edit("`I can't kang that...`")
        return
    if media_:
        args = message.filtered_input_str.split()
        pack = 1
        if len(args) == 2:
            emoji_, pack = args
        elif len(args) == 1:
            if args[0].isnumeric():
                pack = int(args[0])
            else:
                emoji_ = args[0]

        if emoji_ and emoji_ not in (
            getattr(emoji, _) for _ in dir(emoji) if not _.startswith("_")
        ):
            emoji_ = None
        if not emoji_:
            emoji_ = "👀"

        a_name = user.first_name
        u_name = user.username
        u_name = "@" + u_name if u_name else user.first_name or user.id
        packname = f"a{user.id}_{user.username}"
        custom_packnick = Config.CUSTOM_PACK_NAME or f"{a_name}'s sticker pack"
        packnick = f"{a_name}'s stickers [{u_name}]"
        cmd = "/newpack"
        if resize:
            media_ = await resize_photo(media_, is_video, ff_vid)
        if is_anim:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"
        if is_video:
            packname += "_video"
            packnick += " "
            cmd = "/newvideo"
        exist = False
        try:
            exist = await message.client.send(
                GetStickerSet(
                    stickerset=InputStickerSetShortName(short_name=packname), hash=0
                )
            )
        except StickersetInvalid:
            pass
        if exist is not False:
            async with paimon.conversation("Stickers", limit=30) as conv:
                try:
                    await conv.send_message("/addsticker")
                except YouBlockedUser:
                    await kang_msg.edit("first **unblock** @Stickers")
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                msg = await conv.get_response(mark_read=True)
                limit = "50" if is_anim else "120"
                while limit in msg.text:
                    pack += 1
                    packname = f"a{user.id}_by_paimon_{pack}"
                    packnick = f"{custom_packnick} {pack}"
                    if is_anim:
                        packname += "_anim"
                        packnick += " (Animated)"
                    if is_video:
                        packname += "_video"
                        packnick += ""
                    await kang_msg.edit(
                        "`Switching to Pack "
                        + str(pack)
                        + " due to insufficient space`"
                    )
                    await conv.send_message(packname)
                    msg = await conv.get_response(mark_read=True)
                    if msg.text == "Invalid pack selected.":
                        await conv.send_message(cmd)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packnick)
                        await conv.get_response(mark_read=True)
                        await conv.send_document(media_)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(emoji_)
                        await conv.get_response(mark_read=True)
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response(mark_read=True)
                            await conv.send_message(f"<{packnick}>", parse_mode=None)
                        await conv.get_response(mark_read=True)
                        await conv.send_message("/skip")
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packname)
                        await conv.get_response(mark_read=True)
                        out = (
                            "__kanged__"
                            if "-s" in message.flags
                            else f"[stolen](t.me/addstickers/{packname})"
                        )
                        await kang_msg.edit(
                            f"**Sticker** {out} __in a Different Pack__**!**"
                        )
                        return
                try:
                    await conv.send_document(media_)
                except BaseException:
                    await paimon.send_message(Config.LOG_CHANNEL_ID, media_)
                rsp = await conv.get_response(mark_read=True)
                if "Sorry, the file type is invalid." in rsp.text:
                    await kang_msg.edit(
                        "`Failed to add sticker, use` @Stickers "
                        "`bot to add the sticker manually.`"
                    )
                    return
                await conv.send_message(emoji_)
                await conv.get_response(mark_read=True)
                await conv.send_message("/done")
                await conv.get_response(mark_read=True)
        else:
            await kang_msg.edit("`Brewing a new Pack...`")
            async with paimon.conversation("Stickers") as conv:
                try:
                    await conv.send_message(cmd)
                except YouBlockedUser:
                    await kang_msg.edit("first **unblock** @Stickers")
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packnick)
                await conv.get_response(mark_read=True)
                await conv.send_document(media_)
                rsp = await conv.get_response(mark_read=True)
                if "Sorry, the file type is invalid." in rsp.text:
                    await kang_msg.edit(
                        "`Failed to add sticker, use` @Stickers "
                        "`bot to add the sticker manually.`"
                    )
                    return
                await conv.send_message(emoji_)
                await conv.get_response(mark_read=True)
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response(mark_read=True)
                    await conv.send_message(f"<{packnick}>", parse_mode=None)
                await conv.get_response(mark_read=True)
                await conv.send_message("/skip")
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                await conv.get_response(mark_read=True)
        out = (
            "__kanged__"
            if "-s" in message.flags
            else f"[stolen](t.me/addstickers/{packname})"
        )
        await kang_msg.edit(f"**sticker** {out}**!**")
        if os.path.exists(str(media_)):
            os.remove(media_)


@paimon.on_cmd(
    "stickerinfo",
    about={
        "header": "get sticker pack info",
        "usage": "reply {tr}stickerinfo to any sticker",
    },
)
async def sticker_pack_info_(message: Message):
    """get sticker pack info"""
    replied = message.reply_to_message
    if not replied:
        await message.edit("`I can't fetch info from nothing, can I ?!`")
        return
    if not replied.sticker:
        await message.edit("`Reply to a sticker to get the pack details`")
        return
    await message.edit("`Fetching details of the sticker pack, please wait..`")
    get_stickerset = await message.client.send(
        GetStickerSet(
            stickerset=InputStickerSetShortName(short_name=replied.sticker.set_name),
            hash=0,
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    out_str = (
        f"**Sticker Title:** `{get_stickerset.set.title}\n`"
        f"**Sticker Short Name:** `{get_stickerset.set.short_name}`\n"
        f"**Archived:** `{get_stickerset.set.archived}`\n"
        f"**Official:** `{get_stickerset.set.official}`\n"
        f"**Masks:** `{get_stickerset.set.masks}`\n"
        f"**Animated:** `{get_stickerset.set.animated}`\n"
        f"**Stickers In Pack:** `{get_stickerset.set.count}`\n"
        f"**Emojis In Pack:**\n{' '.join(pack_emojis)}"
    )
    await message.edit(out_str)


async def resize_photo(media: str, video: bool, fast_forward: bool) -> str:
    """Resize the given photo to 512x512"""
    if video:
        info_ = Media_Info.data(media)
        width = info_["pixel_sizes"][0]
        height = info_["pixel_sizes"][1]
        sec = info_["duration_in_ms"]
        s = sec / 1000

        if height == width:
            height, width = 512, 512
        elif height > width:
            height, width = 512, -1
        elif width > height:
            height, width = -1, 512

        resized_video = f"{media}.webm"
        if fast_forward:
            if s > 3:
                fract_ = 3 / s
                ff_f = round(fract_, 2)
                set_pts_ = ff_f - 0.01 if ff_f > fract_ else ff_f
                cmd_f = f"-filter:v 'setpts={set_pts_}*PTS',scale={width}:{height}"
            else:
                cmd_f = f"-filter:v scale={width}:{height}"
        else:
            cmd_f = f"-filter:v scale={width}:{height}"
        fps_ = float(info_["frame_rate"])
        fps_cmd = "-r 30 " if fps_ > 30 else ""
        cmd = f"ffmpeg -i {media} {cmd_f} -ss 00:00:00 -to 00:00:03 -an -c:v libvpx-vp9 {fps_cmd}-fs 256K {resized_video}"
        await runcmd(cmd)
        os.remove(media)
        return resized_video

    image = Image.open(media)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width * scale), int(image.height * scale))

    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = io.BytesIO()
    resized_photo.name = "sticker.png"
    image.save(resized_photo, "PNG")
    os.remove(media)
    return resized_photo


KANGING_STR = "me stealing this..."


# Based on:
# https://github.com/AnimeKaizoku/SaitamaRobot/blob/10291ba0fc27f920e00f49bc61fcd52af0808e14/SaitamaRobot/modules/stickers.py#L42
@paimon.on_cmd(
    "sticker",
    about={
        "header": "Search Sticker Packs",
        "usage": "Reply {tr}sticker or " "{tr}sticker [text]",
    },
)
async def sticker_search(message: Message):
    # search sticker packs
    reply = message.reply_to_message
    query_ = None
    if message.input_str:
        query_ = message.input_str
    elif reply and reply.from_user:
        query_ = reply.from_user.username or reply.from_user.id

    if not query_:
        return message.err(
            "reply to a user or provide text to search sticker packs", del_in=3
        )

    await message.edit(f'Searching for "`{query_}`"...')
    titlex = f'<b>sticker packs :</b> "<u>{query_}</u>"\n'
    sticker_pack = ""
    try:
        text = await get_response.text(
            f"https://combot.org/telegram/stickers?q={query_}"
        )
    except ValueError:
        return await message.err(
            "Response was not 200!, Api is having some issues\n Please try again later.",
            del_in=5,
        )
    soup = bs(text, "lxml")
    results = soup.find_all("div", {"class": "sticker-pack__header"})
    for pack in results:
        if pack.button:
            title_ = (pack.find("div", {"class": "sticker-pack__title"})).text
            link_ = (pack.a).get("href")
            sticker_pack += f"\n• [{title_}]({link_})"
    if not sticker_pack:
        sticker_pack = "`Not Found!`"
    await message.edit((titlex + sticker_pack), disable_web_page_preview=True)
