""" kang stickers """
# All rights reserved.

import io
import os
import random

from PIL import Image
from pyrogram import emoji
from pyrogram.errors import StickersetInvalid, YouBlockedUser
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName

from paimon import Config, Message, paimon
from paimon.utils import media_to_image
from paimon.utils.tools import runcmd


@paimon.on_cmd(
    "kang",
    about={
        "header": "kangs stickers or creates new ones",
        "flags": {"-s": "without link", "-d": "without trace"},
        "usage": "Reply {tr}kang [emoji('s)] [pack number] to a sticker or "
        "an image to kang it to your userbot pack.",
        "examples": [
            "{tr}kang",
            "{tr}kang -s",
            "{tr}kang -d",
            "{tr}kang 🤔😎",
            "{tr}kang 2",
            "{tr}kang 🤔🤣😂 2",
        ],
    },
    allow_channels=False,
    allow_via_bot=False,
)
async def kang_(message: Message):
    """kang um sticker"""
    user = await paimon.get_me()
    replied = message.reply_to_message
    media = None
    emoji_ = None
    is_anim = False
    is_video = False
    resize = False
    if replied and replied.media:
        if replied.photo:
            resize = True
        elif replied.document and "image" in replied.document.mime_type:
            resize = True
        elif replied.document and "tgsticker" in replied.document.mime_type:
            is_anim = True
        elif (
            replied.document
            and "video" in replied.document.mime_type
            and replied.document.file_size <= 10485760
        ):
            resize = True
            is_video = True
        elif replied.animation:
            resize = True
            is_video = True
        elif replied.sticker:
            if not replied.sticker.file_name:
                await message.edit("`The sticker has no name!`")
                return
            emoji_ = replied.sticker.emoji
            is_anim = replied.sticker.is_animated
            is_video = replied.sticker.is_video
            if not (
                replied.sticker.file_name.endswith(".tgs")
                or replied.sticker.file_name.endswith(".webm")
            ):
                resize = True
        else:
            await message.edit("`unsupported file!`")
            return
        await message.edit(f"`{random.choice(KANGING_STR)}`")
        media = await paimon.download_media(message=replied, file_name=Config.DOWN_PATH)
    else:
        await message.edit("`I can't kang this...`")
        return
    if media:
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
            emoji_ = "✨"

        a_name = user.first_name
        u_name = user.username
        u_name = "@" + u_name if u_name else user.first_name or user.id
        packname = f"a{user.id}_by_x_{pack}"
        custom_packnick = (
            Config.CUSTOM_PACK_NAME or f"{a_name}'s sticker pack({u_name})"
        )
        packnick = f"{custom_packnick} Vol.{pack}"
        cmd = "/newpack"
        if resize:
            media = await resize_media(media, is_video)
        if is_anim:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"
        if is_video:
            packname += "_video"
            packnick += " (Video)"
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
                    await message.edit("first **unblock** @Stickers")
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                msg = await conv.get_response(mark_read=True)
                limit = "50" if (is_anim or is_video) else "120"
                while limit in msg.text:
                    pack += 1
                    packname = f"a{user.id}_by_paimon_{pack}"
                    packnick = f"{custom_packnick} Vol.{pack}"
                    if is_anim:
                        packname += "_anim"
                        packnick += " (Animated)"
                    if is_video:
                        packname += "_video"
                        packnick += " (Video)"
                    await message.edit(
                        "`Switching to Pack "
                        + str(pack)
                        + "`due to insufficient space`"
                    )
                    await conv.send_message(packname)
                    msg = await conv.get_response(mark_read=True)
                    if msg.text == "Pacote inválido selecionado.":
                        await conv.send_message(cmd)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packnick)
                        await conv.get_response(mark_read=True)
                        await conv.send_document(media)
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
                        if "-d" in message.flags:
                            await message.delete()
                        else:
                            out = (
                                "__kanged__"
                                if "-s" in message.flags
                                else f"[kanged](t.me/addstickers/{packname})"
                            )
                            await message.edit(
                                f"**Sticker** {out} __in a Different Pack__**!**"
                            )
                        return
                await conv.send_document(media)
                rsp = await conv.get_response(mark_read=True)
                if "Sorry, the file type is invalid." in rsp.text:
                    await message.edit(
                        "`Failed to add sticker, use` @Stickers "
                        "`bot to add the sticker manually.`"
                    )
                    return
                await conv.send_message(emoji_)
                await conv.get_response(mark_read=True)
                await conv.send_message("/done")
                await conv.get_response(mark_read=True)
        else:
            await message.edit("`creating new pack...`")
            async with paimon.conversation("Stickers") as conv:
                try:
                    await conv.send_message(cmd)
                except YouBlockedUser:
                    await message.edit("`first **unblock** @Stickers`")
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packnick)
                await conv.get_response(mark_read=True)
                await conv.send_document(media)
                rsp = await conv.get_response(mark_read=True)
                if "Sorry, the file type is invalid." in rsp.text:
                    await message.edit(
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
        if "-d" in message.flags:
            await message.delete()
        else:
            out = (
                "__kanged__"
                if "-s" in message.flags
                else f"[kanged](t.me/addstickers/{packname})"
            )
            await message.edit(f"**Sticker** {out}**!**")
        if os.path.exists(str(media)):
            os.remove(media)


@paimon.on_cmd(
    "stickerinfo",
    about={
        "header": "get sticker pack info",
        "usage": "reply {tr}stkrinfo to any sticker",
    },
)
async def sticker_pack_info_(message: Message):
    """get sticker pack info"""
    replied = message.reply_to_message
    if not replied:
        await message.err("`I can't fetch info from nothing, can I ?!`")
        return
    if not replied.sticker:
        await message.err("`Reply to a sticker to get the pack details`")
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
        f"**Video:** `{get_stickerset.set.gifs}`\n"
        f"**Animated:** `{get_stickerset.set.animated}`\n"
        f"**Stickers In Pack:** `{get_stickerset.set.count}`\n"
        f"**Emojis In Pack:**\n{' '.join(pack_emojis)}"
    )
    await message.edit(out_str)


async def resize_media(media: str, video: bool) -> str:
    """Resize the given media to 512x512"""
    if video:
        resized_video = f"{media}.webm"
        cmd = (
            f"ffmpeg -i {media} -ss 00:00:00 -to 00:00:03 -map 0:v"
            + f" -c:v libvpx-vp9 -vf scale=512:512:force_original_aspect_ratio=decrease,fps=fps=30 {resized_video}"
        )
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

    await message.edit(f'Searching for sticker packs for "`{query_}`"...')
    titlex = f'<b>Sticker Packs For:</b> "<u>{query_}</u>"\n'
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


KANGING_STR = ("kanging this sticker...",)


@paimon.on_cmd(
    "imgs",
    about={
        "header": "convert to image",
        "description": "convert GIF/sticker/vídeo/thumbnail of music in image into jpg format",
        "usage": "{tr}imgs [reply to a media]",
    },
)
async def img(message: Message):
    if not message.reply_to_message:
        await message.edit("Reply to a media...", del_in=5)
        return
    reply_to = message.reply_to_message.message_id
    await message.edit("converting...", del_in=5)
    file_name = "paimon.jpg"
    down_file = os.path.join(Config.DOWN_PATH, file_name)
    if os.path.isfile(down_file):
        os.remove(down_file)
    image = await media_to_image(message)
    await message.reply_photo(image, reply_to_message_id=reply_to)
    os.remove(image)
