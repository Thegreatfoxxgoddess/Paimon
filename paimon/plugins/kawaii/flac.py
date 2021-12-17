# plugin made for paimon by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi


from asyncio import gather

from paimon import paimon, Message
from paimon.config import Config


@paimon.on_cmd(
    "flac",
    about={
        "header": "FLAC music downloader",
        "usage": "{tr}flac [song name]",
    },
)
async def jio_music(message: Message):
    bot_ = "JioDLBot"
    query_ = message.input_str
    result = await paimon.get_inline_bot_results(bot_, query_)
    if not result.results:
        await message.edit(f"Song <code>{query_}</code> not found...", del_in=5)
        return
    try:
        log_ = await paimon.send_inline_bot_result(
            Config.LOG_CHANNEL_ID,
            query_id=result.query_id,
            result_id=result.results[0].id
        )
        await gather(
            paimon.copy_message(
                chat_id=message.chat.id,
                from_chat_id=Config.LOG_CHANNEL_ID,
                message_id=log_.updates[0].id,
            ),
            message.delete(),
        )
    except BaseException as e:
        await message.err(
            f"`Something unexpected happend.`\n<b>ERROR:</b> `{e}`", del_in=5
        )
