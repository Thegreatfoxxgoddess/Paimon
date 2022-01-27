
# All rights reserved.

import wikipedia

from paimon import paimon, Message


@paimon.on_cmd("wiki", about={
    'header': "do a Wikipedia search",
    'flags': {'-l': "limit the number of returned results (defaults to 5)"},
    'usage': "{tr}wiki [flags] [query | reply to msg]",
    'examples': "{tr}wiki -l5 paimon"})
async def wiki_pedia(message: Message):
    await message.edit("Processing ...")
    query = message.filtered_input_str
    flags = message.flags
    limit = int(flags.get('-l', 5))
    if message.reply_to_message:
        query = message.reply_to_message.text
    if not query:
        await message.err(text="Give a query or reply to a message to wikipedia!")
        return
    try:
        wikipedia.set_lang("en")
        results = wikipedia.search(query)
    except Exception as e:
        await message.err(e)
        return
    output = ""
    for i, s in enumerate(results, start=1):
        page = wikipedia.page(s)
        url = page.url
        output += f"[{s}]({url})\n"
        if i == limit:
            break
    output = f"**Wikipedia Search:**\n`{query}`\n\n**Results:**\n{output}"
    await message.edit_or_send_as_file(text=output, caption=query,
                                       disable_web_page_preview=True)
