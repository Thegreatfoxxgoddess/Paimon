import os

from gtts import gTTS
from hachoir.metadata import extractMetadata as XMan
from hachoir.parser import createParser as CPR

from paimon import Message, paimon


@paimon.on_cmd(
    "tts",
    about={
        "header": "Text To Speech (default language is en)",
        "examples": ["{tr}tts (In reply)", "{tr}tts -en I do as the crystal guides"],
    },
)
async def text_to_speech(message: Message):
    req_file_name = "gtts.mp3"
    reply = message.reply_to_message
    input_str = message.input_str
    def_lang = "en"
    text = ""
    if input_str:
        input_str = input_str.strip()
        if reply:
            if (
                (reply.text or reply.caption)
                and len(input_str.split()) == 1
                and input_str.startswith("-")
            ):
                def_lang = input_str[1:]
                text = reply.text or reply.caption
        else:
            i_split = input_str.split(None, 1)
            if len(i_split) == 2 and i_split[0].startswith("-"):
                def_lang = i_split[0][1:]
                text = i_split[1]
            else:
                text = input_str
    elif reply and (reply.text or reply.caption):
        text = reply.text or reply.caption
    if not text:
        await message.err(
            ":: Input Not Found ::\nProvide text to convert to voice !", del_in=7
        )
        return
    try:
        await message.edit("Processing..")
        speeched = gTTS(text, lang=def_lang)
        speeched.save(req_file_name)
        meta = XMan(CPR(req_file_name))
        a_len = 0
        a_cap = f"Language Code:  **{def_lang.upper()}**"
        if meta and meta.has("duration"):
            a_len = meta.get("duration").seconds
        await message.edit("Uploading...")
        await message.client.send_voice(
            chat_id=message.chat.id,
            voice=req_file_name,
            caption=a_cap,
            duration=a_len,
            reply_to_message_id=reply.message_id if reply else None,
        )
        os.remove(req_file_name)
        await message.delete()
    except Exception as err:
        await message.err(str(err))
