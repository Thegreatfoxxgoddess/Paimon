""" kang stickers """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia

import io
import os
import random

from bs4 import BeautifulSoup as bs
from PIL import Image
from pyrogram import emoji
from pyrogram.errors import StickersetInvalid, YouBlockedUser
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName

from paimon import Config, Message, paimon
from paimon.utils import get_response, media_to_image


@paimon.on_cmd(
    "kang",
    about={
        "header": "steal stickers or create new ones",
        "flags": {"-s": "no link", "-d": "silent kang"},
        "usage": "reply {tr}kang [emoji('s)] [numero do pack] a um sticker ou "
        "an image to put it in your userbot package.",
        "examples": [
            "{tr}kang",
            "{tr}kang -s",
            "{tr}kang -d",
            "{tr}kang 🤔",
            "{tr}kang 2",
            "{tr}kang 🤔 2",
        ],
    },
    allow_channels=False,
    allow_via_bot=False,
)
async def kang_(message: Message):
    """kang a sticker"""
    user = await paimon.get_me()
    replied = message.reply_to_message
    photo = None
    emoji_ = None
    is_anim = False
    resize = False
    if replied and replied.media:
        if replied.photo:
            resize = True
        elif replied.document and "image" in replied.document.mime_type:
            resize = True
        elif replied.document and "tgsticker" in replied.document.mime_type:
            is_anim = True
        elif replied.sticker:
            if not replied.sticker.file_name:
                await message.edit("`sticker has no name!`")
                return
            emoji_ = replied.sticker.emoji
            is_anim = replied.sticker.is_animated
            if not replied.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            await message.edit("`Unsupported file!`")
            return
        await message.edit(f"`{random.choice(KANGING_STR)}`")
        photo = await paimon.download_media(message=replied, file_name=Config.DOWN_PATH)
    else:
        await message.edit("`i can't steal this...`")
        return
    if photo:
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
            emoji_ = "🤔"

        u_name = user.username
        u_name = "@" + u_name if u_name else user.first_name or user.id
        packname = f"a{user.id}_by_x_{pack}"
        custom_packnick = Config.CUSTOM_PACK_NAME or f"{u_name}'s kang pack"
        packnick = f"{custom_packnick} Vol.{pack}"
        cmd = "/newpack"
        if resize:
            photo = resize_photo(photo)
        if is_anim:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"
        exist = False
        try:
            exist = await message.client.send(
                GetStickerSet(stickerset=InputStickerSetShortName(short_name=packname))
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
                limit = "50" if is_anim else "120"
                while limit in msg.text:
                    pack += 1
                    packname = f"a{user.id}_by_paimon_{pack}"
                    packnick = f"{custom_packnick} Vol.{pack}"
                    if is_anim:
                        packname += "_anim"
                        packnick += " (Animated)"
                    await message.edit(
                        "`Switching to " + str(pack) + " due to insufficient space`"
                    )
                    await conv.send_message(packname)
                    msg = await conv.get_response(mark_read=True)
                    if msg.text == "Pacote inválido selecionado.":
                        await conv.send_message(cmd)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packnick)
                        await conv.get_response(mark_read=True)
                        await conv.send_document(photo)
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
                                else f"[roubado](t.me/addstickers/{packname})"
                            )
                            await message.edit(
                                f"**Sticker** {out} __in a different package__**!**"
                            )
                        return
                await conv.send_document(photo)
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
            await message.edit("`Preparing a new pack...`")
            async with paimon.conversation("Stickers") as conv:
                try:
                    await conv.send_message(cmd)
                except YouBlockedUser:
                    await message.edit("primeiro **desbloqueie** @Stickers")
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packnick)
                await conv.get_response(mark_read=True)
                await conv.send_document(photo)
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
                else f"[roubado](t.me/addstickers/{packname})"
            )
            await message.edit(f"**Sticker** {out}**!**")
        if os.path.exists(str(photo)):
            os.remove(photo)


@paimon.on_cmd(
    "stkrinfo",
    about={
        "header": "get sticker pack information",
        "usage": "reply {tr}stkrinfo to any sticker",
    },
)
async def sticker_pack_info_(message: Message):
    """get sticker pack information"""
    replied = message.reply_to_message
    if not replied:
        await message.edit("`I can't get information out of nothing, can i?!`")
        return
    if not replied.sticker:
        await message.edit("`Reply to a sticker for package details`")
        return
    await message.edit("`getting details of the sticker pack, please wait...`")
    get_stickerset = await message.client.send(
        GetStickerSet(
            stickerset=InputStickerSetShortName(short_name=replied.sticker.set_name)
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    out_str = (
        f"**Sticker title:** `{get_stickerset.set.title}\n`"
        f"**Sticker short name:** `{get_stickerset.set.short_name}`\n"
        f"**Archived:** `{get_stickerset.set.archived}`\n"
        f"**Official:** `{get_stickerset.set.official}`\n"
        f"**Masks:** `{get_stickerset.set.masks}`\n"
        f"**Animated:** `{get_stickerset.set.animated}`\n"
        f"**stickers in the pack:** `{get_stickerset.set.count}`\n"
        f"**Emojis in the pack:**\n{' '.join(pack_emojis)}"
    )
    await message.edit(out_str)


def resize_photo(photo: str) -> io.BytesIO:
    """Resize the photo provided to 512x512"""
    image = Image.open(photo)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width * scale), int(image.height * scale))
    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = io.BytesIO()
    resized_photo.name = "sticker.png"
    image.save(resized_photo, "PNG")
    os.remove(photo)
    return resized_photo


KANGING_STR = ("me kanging this sticker uwu",)


# Based on:
# https://github.com/AnimeKaizoku/SaitamaRobot/blob/10291ba0fc27f920e00f49bc61fcd52af0808e14/SaitamaRobot/modules/stickers.py#L42
@paimon.on_cmd(
    "stickers",
    about={
        "header": "Search for sticker packs",
        "usage": "Reply {tr}stickers or " "{tr}stickers [text]",
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
            "responder a um usuário ou fornecer texto para pesquisar pacotes de adesivos",
            del_in=3,
        )

    await message.edit(f'Looking for "`{query_}`"...')
    titlex = f'<b>Sticker packs for:</b> "<u>{query_}</u>"\n'
    sticker_pack = ""
    try:
        text = await get_response.text(
            f"https://combot.org/telegram/stickers?q={query_}"
        )
    except ValueError:
        return await message.err(
            "A resposta não foi 200!, Api está tendo alguns problemas\nTente novamente mais tarde.",
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
        sticker_pack = "`Not found!`"
    await message.edit((titlex + sticker_pack), disable_web_page_preview=True)


# import from oub-remix to ux by Itachi_HTK/ashwinstr


@paimon.on_cmd(
    "imgs",
    about={
        "header": "convert things to image",
        "description": "convert GIF/sticker/vídeo/thumbnail of music in image in jpg format",
        "usage": "{tr}imgs [respond to a media]",
    },
)
async def img(message: Message):
    if not message.reply_to_message:
        await message.edit("reply to a media...", del_in=5)
        return
    reply_to = message.reply_to_message.message_id
    await message.edit("converting...", del_in=5)
    file_name = "paimon_convert.jpg"
    down_file = os.path.join(Config.DOWN_PATH, file_name)
    if os.path.isfile(down_file):
        os.remove(down_file)
    image = await media_to_image(message)
    await message.reply_photo(image, reply_to_message_id=reply_to)
