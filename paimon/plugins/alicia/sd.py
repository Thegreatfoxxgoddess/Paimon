# kanged from github.com/UsergeTeam/userge

from paimon import paimon, Message


@paimon.on_cmd("sd (?:(\\d+)?\\s?(.+))", about={
    'header': "make self-destructable messages",
    'usage': "{tr}sd [test]\n{tr}sd [timeout in seconds] [text]"})
async def selfdestruct(message: Message):
    seconds = int(message.matches[0].group(1) or 0)
    text = str(message.matches[0].group(2))
    await message.edit(text=text, del_in=seconds)
