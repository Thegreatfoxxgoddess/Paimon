import asyncio
import os
from re import match

import aiofiles
from selenium import webdriver

from paimon import Config, Message, paimon


@paimon.on_cmd("webss", about={"header": "Get snapshot of a website"})
async def webss(message: Message):
    if Config.GOOGLE_CHROME_BIN is None:
        await message.edit("`need to install Google Chrome. Module Stopping`", del_in=5)
        return
    link_match = match(r"\bhttps?://.*\.\S+", message.input_str)
    if not link_match:
        await message.err("I need a valid link to take screenshots from.")
        return
    link = link_match.group()
    await message.edit("`Processing ...`")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = Config.GOOGLE_CHROME_BIN
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--test-type")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(link)
    height = driver.execute_script(
        "return Math.max(document.body.scrollHeight, document.body.offsetHeight, "
        "document.documentElement.clientHeight, document.documentElement.scrollHeight, "
        "document.documentElement.offsetHeight);"
    )
    width = driver.execute_script(
        "return Math.max(document.body.scrollWidth, document.body.offsetWidth, "
        "document.documentElement.clientWidth, document.documentElement.scrollWidth, "
        "document.documentElement.offsetWidth);"
    )
    await asyncio.sleep(5)
    driver.set_window_size(width + 125, height + 70)
    wait_for = height / 1000
    await message.edit(
        f"`Generating screenshot of the page...`"
        f"\n`Height of page = {height}px`"
        f"\n`Width of page = {width}px`"
        f"\n`Waiting ({int(wait_for)}s) for the page to load.`"
    )
    await asyncio.sleep(5)
    await asyncio.sleep(int(wait_for))
    im_png = driver.get_screenshot_as_png()
    driver.close()
    message_id = message.message_id
    if message.reply_to_message:
        message_id = message.reply_to_message.message_id
    file_path = os.path.join(Config.DOWN_PATH, "screenshot.png")
    async with aiofiles.open(file_path, "wb") as out_file:
        await out_file.write(im_png)
    await asyncio.gather(
        message.delete(),
        message.client.send_document(
            chat_id=message.chat.id,
            document=file_path,
            caption=link,
            reply_to_message_id=message_id,
        ),
    )
    os.remove(file_path)
    driver.quit()
