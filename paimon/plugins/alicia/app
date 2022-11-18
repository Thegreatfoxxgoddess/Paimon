from paimon import Message, paimon


@paimon.on_cmd(
    "app",
    about={
        "header": "Search application details of any app"
    },
)
async def app(message: Message):
    try:
        await message.edit("`searching...`")
        app_name = message.filtered_input_str
        page = requests.get(
            f"https://search.f-droid.org/?q={app_name}"
        )
        await message.edit(results)
