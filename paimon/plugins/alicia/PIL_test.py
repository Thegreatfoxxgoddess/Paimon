import os
import textwrap

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from paimon import Config, Message, paimon


@paimon.on_cmd(
    "imging",
    about={
        "header": "testing images module",
        "usage": "{tr}imging [text]",
    },
)
async def image_ing(message: Message):
    reply_ = message.reply_to_message
    if not reply_:
        return await message.edit("`Reply to image...`", del_in=5)
    down_ = await paimon.download_media(reply_)
    img = Image.open(down_)
    draw_ = ImageDraw.Draw(img)
    draw_.text((28, 36), "TESTING", fill=(255, 0, 0))
    save_ = f"{Config.DOWN_PATH}/TESTING.png"
    img.save(save_)
    await message.reply_photo(save_)
    os.remove(down_)
    os.remove(save_)


@paimon.on_cmd(
    "pfp_stick",
    about={
        "header": "testing images module",
        "usage": "{tr}pfp_stick",
    },
)
async def pfp_stick_(message: Message):
    await message.edit("`Sending...`")
    reply_ = message.reply_to_message
    pfp_id = (
        reply_.from_user.photo.big_file_id
        if reply_
        else message.from_user.photo.big_file_id
    )
    down_pfp = await paimon.download_media(pfp_id)
    o_pfp = Image.open(down_pfp).convert("RGB")
    npImage = np.array(o_pfp)
    h_, w_ = o_pfp.size

    alpha = Image.new("L", o_pfp.size, 0)
    draw = ImageDraw.Draw(alpha)
    draw.pieslice([0, 0, h_, w_], 0, 360, fill=255)

    npAlpha = np.array(alpha)

    npImage = np.dstack((npImage, npAlpha))

    save_ = f"{Config.DOWN_PATH}/TESTING.webp"
    Image.fromarray(npImage).save(save_)

    await message.reply_document(save_)
    os.remove(save_)


@paimon.on_cmd(
    "rect",
    about={
        "header": "testing images module",
        "usage": "{tr}rect",
    },
)
async def rect_angle(message: Message):
    await message.edit("Making quote...", del_in=5)
    reply_ = message.reply_to_message
    name_ = reply_.from_user.first_name if reply_ else message.from_user.first_name
    text_ = reply_.text if reply_ else message.input_str or ""
    font_ = "resources/Roboto-Regular.ttf"
    f_h = 15
    b_font_ = "resources/lucidagrandebold.ttf"
    b_f_h = 25
    w_, h_ = (40 + max((len(name_) * 5), (len(text_) * 5)) + 40), (
        15 + b_f_h + 10 + f_h + 15
    )
    img_1 = Image.new("RGB", (w_, h_), "white")
    draw_1 = ImageDraw.Draw(img_1)
    draw_1.rounded_rectangle(
        [30, 0, w_, h_], fill="white", outline="white", width=1, radius=20
    )
    n_Font = ImageFont.truetype(b_font_, 12)
    draw_1.text((40, 15), text=name_, font=n_Font, fill=(115, 147, 179))
    t_Font = ImageFont.truetype(font_, 10)
    draw_1.text((40, (h_ - 30)), text=text_, font=t_Font, fill=(0, 0, 0))
    npImage_1 = np.array(img_1)

    alpha_1 = Image.new("L", (w_, h_), 0)
    draw_r = ImageDraw.Draw(alpha_1)
    draw_r.rounded_rectangle(
        [30, 0, w_, h_], fill="white", outline="white", width=1, radius=20
    )

    npAlpha_1 = np.array(alpha_1)

    npImage_1 = np.dstack((npImage_1, npAlpha_1))

    path_ = f"{Config.DOWN_PATH}/rect.webp"
    Image.fromarray(npImage_1).save(path_)

    await message.reply_document(path_)
    os.remove(path_)


@paimon.on_cmd(
    "qt",
    about={
        "header": "testing images module",
        "flags": {
            "-f": "fake quote with input text",
        },
        "usage": "{tr}qt",
    },
)
async def cu_tee(message: Message):
    await message.edit("Making quote...", del_in=5)
    reply_ = message.reply_to_message
    name_ = reply_.from_user.first_name if reply_ else message.from_user.first_name
    if "-f" in message.flags:
        no_input = False
        if reply_:
            text_ = message.filtered_input_str
            if not text_:
                no_input = True
        else:
            no_input = True
        if no_input:
            return await message.edit(
                "`Reply to a user with custom input...`", del_in=3
            )
    else:
        text_ = reply_.text if reply_ else message.filtered_input_str or ""
    font_ = "resources/Roboto-Regular.ttf"
    f_h = 25
    b_font_ = "resources/lucidagrandebold.ttf"
    b_f_h = 30
    n_Font = ImageFont.truetype(b_font_, b_f_h)
    n_Font_size = n_Font.getsize(name_)[0]
    t_Font = ImageFont.truetype(font_, f_h)
    t_Font_size = t_Font.getsize_multiline(text_)
    t_Font_h = t_Font_size[1]
    t_Font_size = t_Font_size[0]
    if t_Font_size > (512 - (100 - 15 - 15)):
        text_wrap = textwrap.wrap(text_, 30)
        text_ = "\n".join(text_wrap)
        t_Font_size = t_Font.getsize_multiline(text_)
        t_Font_h = t_Font_size[1]
        t_Font_size = t_Font_size[0]
    w_, h_ = (95 + max(n_Font_size, t_Font_size) + 35), (15 + b_f_h + 15 + t_Font_h + 5)
    pfp_w, pfp_h = 90, 90
    img_1 = Image.new("RGB", (512, max(h_, pfp_h) + 1), "white")
    alpha_1 = Image.new("L", (512, max(h_, pfp_h) + 1), 0)

    draw_1 = ImageDraw.Draw(img_1)
    draw_r = ImageDraw.Draw(alpha_1)

    draw_1.rounded_rectangle(
        [100, 0, min(w_, 512), h_], fill="white", outline="white", width=1, radius=20
    )
    draw_r.rounded_rectangle(
        [100, 0, min(w_, 512), h_], fill="white", outline="white", width=1, radius=20
    )

    draw_1.text((115, 15), text=name_, font=n_Font, fill=(0, 0, 128))
    draw_1.text((115, 45), text=text_, font=t_Font, fill=(0, 0, 0))

    npImage_1 = np.array(img_1)
    npAlpha_1 = np.array(alpha_1)

    npImage_1 = np.dstack((npImage_1, npAlpha_1))

    # round pfp
    pfp_id = (
        reply_.from_user.photo.big_file_id
        if reply_
        else message.from_user.photo.big_file_id
    )
    down_pfp = await paimon.download_media(pfp_id)
    o_pfp = Image.open(down_pfp).convert("RGB")
    o_pfp = o_pfp.resize((pfp_w, pfp_h))
    npImage_2 = np.array(o_pfp)

    alpha_2 = Image.new("L", (pfp_w, pfp_h), 0)
    draw_2 = ImageDraw.Draw(alpha_2)
    draw_2.pieslice([0, 0, pfp_w, pfp_h], 0, 360, fill=255)

    npAlpha_2 = np.array(alpha_2)
    npImage_2 = np.dstack((npImage_2, npAlpha_2))

    path_r = f"{Config.DOWN_PATH}/quoted_r.webp"
    path_p = f"{Config.DOWN_PATH}/quoted_p.webp"

    Image.fromarray(npImage_1).save(path_r)
    Image.fromarray(npImage_2).save(path_p)

    open_r = Image.open(path_r)
    open_r = open_r.convert("RGBA")
    open_p = Image.open(path_p)
    open_p = open_p.convert("RGBA")

    open_r.paste(open_p, (0, max(0, (h_ - 90))))
    save_ = f"{Config.DOWN_PATH}/quoted.webp"
    open_r.save(save_)

    await reply_.reply_document(save_)
    os.remove(path_r)
    os.remove(path_p)
    os.remove(save_)
