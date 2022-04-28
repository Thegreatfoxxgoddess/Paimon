# convert telegram files

import io
import os
import time
from datetime import datetime
from pathlib import Path

import stagger
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery

from paimon import Config, Message, paimon
from paimon.plugins.misc.download import tg_download
from paimon.utils import humanbytes, progress, take_screen_shot
from paimon.utils.exceptions import ProcessCanceled

LOGGER = paimon.getLogger(__name__)
CHANNEL = paimon.getCLogger(__name__)

LOGO_PATH = "resources/logo_x.png"


@paimon.on_cmd(
    "r",
    about={
        "header": "Convert telegram files",
        "usage": "reply {tr}r to any media",
    },
    del_pre=True,
    check_downpath=True,
)
async def convert_(message: Message):
    """convert telegram files"""
    await message.edit("`converting...`")
    if message.reply_to_message and message.reply_to_message.media:
        message.text = "0"
        await _handle_message(message)
    else:
        await message.edit("Please read `.help r`", del_in=5)


@paimon.on_cmd(
    "re",
    about={
        "header": "Rename telegram files",
        "flags": {"-d": "upload as document", "-wt": "without thumb"},
        "usage": "{tr}rename [flags] [new_name_with_extension] : reply to telegram media",
        "examples": "{tr}rename -d test.mp4",
    },
    del_pre=True,
    check_downpath=True,
)
async def rename_(message: Message):
    """rename telegram files"""
    if not message.filtered_input_str:
        await message.err("new name not found!")
        return
    await message.edit("`Trying to Rename ...`")
    if message.reply_to_message and message.reply_to_message.media:
        await _handle_message(message)
    else:
        await message.edit("Please read `.help rename`", del_in=5)


async def _handle_message(message: Message) -> None:
    try:
        dl_loc, _ = await tg_download(message, message.reply_to_message)
    except ProcessCanceled:
        await message.edit("`Process Canceled!`", del_in=5)
    except Exception as e_e:  # pylint: disable=broad-except
        await message.err(str(e_e))
    else:
        await message.delete()
        await upload(message=message, path=Path(dl_loc), del_path=True)


async def upload_path(message: Message, path: Path, del_path: bool):
    file_paths = []
    if path.exists():

        def explorer(_path: Path) -> None:
            if _path.is_file() and _path.stat().st_size:
                file_paths.append(_path)
            elif _path.is_dir():
                for i in sorted(_path.iterdir()):
                    explorer(i)

        explorer(path)
    else:
        path = path.expanduser()
        str_path = os.path.join(*(path.parts[1:] if path.is_absolute() else path.parts))
        for p in Path(path.root).glob(str_path):
            file_paths.append(p)
    current = 0
    for p_t in file_paths:
        current += 1
        try:
            await upload(
                message=message,
                path=p_t,
                del_path=del_path,
                extra=f"{current}/{len(file_paths)}",
            )
        except FloodWait as f_e:
            time.sleep(f_e.x)  # asyncio sleep ?
        if message.process_is_canceled:
            break


async def upload(
    message: Message,
    path: Path,
    del_path: bool = False,
    callback: CallbackQuery = None,
    extra: str = "",
    with_thumb: bool = True,
    custom_thumb: str = "",
    log: bool = True,
):
    if "wt" in message.flags:
        with_thumb = False
    if path.name.lower().endswith((".mkv", ".mp4", ".webm")) and (
        "d" not in message.flags
    ):
        return await vid_upload(
            message=message,
            path=path,
            del_path=del_path,
            callback=callback,
            extra=extra,
            with_thumb=with_thumb,
            custom_thumb=custom_thumb,
            log=log,
        )
    elif path.name.lower().endswith((".mp3", ".flac", ".wav", ".m4a")) and (
        "d" not in message.flags
    ):
        return await audio_upload(
            message=message,
            path=path,
            del_path=del_path,
            callback=callback,
            extra=extra,
            with_thumb=with_thumb,
            log=log,
        )
    elif path.name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")) and (
        "d" not in message.flags
    ):
        await photo_upload(message, path, del_path, extra)
    else:
        await doc_upload(message, path, del_path, extra, with_thumb)


async def doc_upload(
    message: Message,
    path,
    del_path: bool = False,
    extra: str = "",
    with_thumb: bool = True,
    force_document: bool = True,
):
    str_path = str(path)
    sent: Message = await message.client.send_message(
        message.chat.id, f"`Uploading {str_path} as a doc ... {extra}`"
    )
    start_t = datetime.now()
    thumb = None
    if with_thumb:
        thumb = await get_thumb(str_path)
    await message.client.send_chat_action(message.chat.id, "upload_document")
    try:
        msg = await message.client.send_document(
            chat_id=message.chat.id,
            document=str_path,
            thumb=thumb,
            force_document=True,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(message, f"uploading {extra}", str_path),
        )
    except ValueError as e_e:
        await sent.edit(f"Skipping `{str_path}` due to {e_e}")
    except Exception as u_e:
        await sent.edit(str(u_e))
        raise u_e
    else:
        await sent.delete()
        await finalize(message, msg, start_t)
        if os.path.exists(str_path) and del_path:
            os.remove(str_path)


async def vid_upload(
    message: Message,
    path,
    del_path: bool = False,
    callback: CallbackQuery = None,
    extra: str = "",
    with_thumb: bool = True,
    custom_thumb: str = "",
    log: bool = True,
):
    str_path = str(path)
    thumb = None
    if with_thumb:
        if custom_thumb:
            try:
                thumb = await check_thumb(custom_thumb)
            except Exception as e_r:
                await CHANNEL.log(str(e_r))
        if not thumb:
            thumb = await get_thumb(str_path)
    duration = 0
    metadata = extractMetadata(createParser(str_path))
    if metadata and metadata.has("duration"):
        duration = metadata.get("duration").seconds
    sent: Message = await message.client.send_message(
        message.chat.id, f"`Uploading {str_path} as a video ... {extra}`"
    )
    start_t = datetime.now()
    await message.client.send_chat_action(message.chat.id, "upload_video")
    width = 0
    height = 0
    if thumb:
        t_m = extractMetadata(createParser(thumb))
        if t_m and t_m.has("width"):
            width = t_m.get("width")
        if t_m and t_m.has("height"):
            height = t_m.get("height")
    try:
        msg = await message.client.send_video(
            chat_id=message.chat.id,
            video=str_path,
            duration=duration,
            thumb=thumb,
            width=width,
            height=height,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(message, f"uploading {extra}", str_path, callback),
        )
    except ValueError as e_e:
        await sent.edit(f"Skipping `{str_path}` due to {e_e}")
    except Exception as u_e:
        await sent.edit(str(u_e))
        raise u_e
    else:
        await sent.delete()
        await remove_thumb(thumb)
        if log:
            await finalize(message, msg, start_t)
        if os.path.exists(str_path) and del_path:
            os.remove(str_path)
        return msg


async def check_thumb(thumb_path: str):
    f_path = os.path.splitext(thumb_path)
    if f_path[1] != ".jpg":
        new_thumb_path = f"{f_path[0]}.jpg"
        Image.open(thumb_path).convert("RGB").save(new_thumb_path, "JPEG")
        os.remove(thumb_path)
        thumb_path = new_thumb_path
    return thumb_path


async def audio_upload(
    message: Message,
    path,
    del_path: bool = False,
    callback: CallbackQuery = None,
    extra: str = "",
    with_thumb: bool = True,
    log: bool = True,
):
    title = None
    artist = None
    thumb = None
    duration = 0
    str_path = str(path)
    humanbytes(os.stat(str_path).st_size)
    if with_thumb:
        try:
            album_art = stagger.read_tag(str_path)
            if album_art.picture and not os.path.lexists(Config.THUMB_PATH):
                bytes_pic_data = album_art[stagger.id3.APIC][0].data
                bytes_io = io.BytesIO(bytes_pic_data)
                image_file = Image.open(bytes_io)
                image_file.save("album_cover.jpg", "JPEG")
                thumb = "album_cover.jpg"
        except stagger.errors.NoTagError:
            pass
        if not thumb:
            thumb = await get_thumb(str_path)
    metadata = extractMetadata(createParser(str_path))
    if metadata and metadata.has("title"):
        title = metadata.get("title")
    if metadata and metadata.has("artist"):
        artist = metadata.get("artist")
    if metadata and metadata.has("duration"):
        duration = metadata.get("duration").seconds
    sent: Message = await message.client.send_message(
        message.chat.id, f"`Uploading {str_path} as audio ... {extra}`"
    )
    start_t = datetime.now()
    await message.client.send_chat_action(message.chat.id, "upload_audio")
    try:
        msg = await message.client.send_audio(
            chat_id=message.chat.id,
            audio=str_path,
            thumb=thumb,
            title=title,
            performer=artist,
            duration=duration,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(message, f"uploading {extra}", str_path, callback),
        )
    except ValueError as e_e:
        await sent.edit(f"Skipping `{str_path}` due to {e_e}")
    except Exception as u_e:
        await sent.edit(str(u_e))
        raise u_e
    else:
        await sent.delete()
        if log:
            await finalize(message, msg, start_t)
        if os.path.exists(str_path) and del_path:
            os.remove(str_path)
    if os.path.lexists("album_cover.jpg"):
        os.remove("album_cover.jpg")
    return msg


async def photo_upload(message: Message, path, del_path: bool = False, extra: str = ""):
    str_path = str(path)
    sent: Message = await message.client.send_message(
        message.chat.id, f"`Uploading {path.name} as photo ... {extra}`"
    )
    start_t = datetime.now()
    await message.client.send_chat_action(message.chat.id, "upload_photo")
    try:
        msg = await message.client.send_photo(
            chat_id=message.chat.id,
            photo=str_path,
            parse_mode="html",
            disable_notification=True,
            progress=progress,
            progress_args=(message, f"uploading {extra}", str_path),
        )
    except ValueError as e_e:
        await sent.edit(f"Skipping `{str_path}` due to {e_e}")
    except Exception as u_e:
        await sent.edit(str(u_e))
        raise u_e
    else:
        await sent.delete()
        await finalize(message, msg, start_t)
        if os.path.exists(str_path) and del_path:
            os.remove(str_path)


async def get_thumb(path: str = ""):
    if os.path.exists(Config.THUMB_PATH):
        return Config.THUMB_PATH
    if path:
        types = (".jpg", ".webp", ".png")
        if path.endswith(types):
            return None
        file_name = os.path.splitext(path)[0]
        for type_ in types:
            thumb_path = file_name + type_
            if os.path.exists(thumb_path):
                if type_ != ".jpg":
                    new_thumb_path = f"{file_name}.jpg"
                    Image.open(thumb_path).convert("RGB").save(new_thumb_path, "JPEG")
                    os.remove(thumb_path)
                    thumb_path = new_thumb_path
                return thumb_path
        metadata = extractMetadata(createParser(path))
        if metadata and metadata.has("duration"):
            return await take_screen_shot(path, metadata.get("duration").seconds)
    if os.path.exists(LOGO_PATH):
        return LOGO_PATH
    return None


async def remove_thumb(thumb: str) -> None:
    if (
        thumb
        and os.path.exists(thumb)
        and thumb != LOGO_PATH
        and thumb != Config.THUMB_PATH
    ):
        os.remove(thumb)


async def finalize(message: Message, msg: Message, start_t):
    await CHANNEL.fwd_msg(msg)
    await message.client.send_chat_action(message.chat.id, "cancel")
    if message.process_is_canceled:
        await message.edit("`Process Canceled!`", del_in=5)
    else:
        end_t = datetime.now()
        m_s = (end_t - start_t).seconds
        await message.edit(f"Uploaded in {m_s} seconds", del_in=0.5)
