""" setup AFK mode """

import asyncio
from paimon.utils.functions import rand_array
import time
from random import choice, randint

from paimon import Config, Message, filters, get_collection, paimon
from paimon.utils import time_formatter

CHANNEL = paimon.getCLogger(__name__)
SAVED_SETTINGS = get_collection("CONFIGS")
AFK_COLLECTION = get_collection("AFK")

IS_AFK = False
IS_AFK_FILTER = filters.create(lambda _, __, ___: bool(IS_AFK))
REASON = ""
TIME = 0.0
USERS = {}


async def _init() -> None:
    global IS_AFK, REASON, TIME  # pylint: disable=global-statement
    data = await SAVED_SETTINGS.find_one({"_id": "AFK"})
    if data:
        IS_AFK = data["on"]
        REASON = data["data"]
        TIME = data["time"] if "time" in data else 0
    async for _user in AFK_COLLECTION.find():
        USERS.update(
            {_user["_id"]: [_user["pcount"], _user["gcount"], _user["men"]]})


@paimon.on_cmd(
    "afk",
    about={
        "header": "Set to AFK mode",
        "description": "Sets its status to AFK. Respond to anyone who marks you/PM's.\n"
        "Turn off AFK when you type something.",
        "usage": "{tr}afk or {tr}afk [reason]",
    },
    allow_channels=False,
)
async def active_afk(message: Message) -> None:
    """turn on or off away mode"""
    global REASON, IS_AFK, TIME  # pylint: disable=global-statement
    IS_AFK = True
    TIME = time.time()
    REASON = message.input_str
    going_sleep = rand_array(GOING_SLEEP)
    await asyncio.gather(
        CHANNEL.log(f"afk.\n <i>{REASON}</i>"),
        message.edit(
            f"<a href={going_sleep}>\u200c</a>🥱 going away, see you later.", del_in=0),
        AFK_COLLECTION.drop(),
        SAVED_SETTINGS.update_one(
            {"_id": "AFK"},
            {"$set": {"on": True, "data": REASON, "time": TIME}},
            upsert=True,
        ),
    )


@paimon.on_filters(
    IS_AFK_FILTER
    & ~filters.me
    & ~filters.bot
    & ~filters.user(Config.TG_IDS)
    & ~filters.edited
    & (
        filters.mentioned
        | (
            filters.private
            & ~filters.service
            & (
                filters.create(lambda _, __, ___: Config.ALLOW_ALL_PMS)
                | Config.ALLOWED_CHATS
            )
        )
    ),
    allow_via_bot=False,
)
async def handle_afk_incomming(message: Message) -> None:
    """handles ad messages received when you are away"""
    if not message.from_user:
        return
    user_id = message.from_user.id
    chat = message.chat
    user_dict = await message.client.get_user_dict(user_id)
    afk_time = time_formatter(round(time.time() - TIME))
    coro_list = []
    sleeping = rand_array(AFK_SLEEPING)
    if user_id in USERS:
        if not (USERS[user_id][0] + USERS[user_id][1]) % randint(2, 4):
            if REASON:
                out_str = (
                    f"▸ heyy, I'm afk {afk_time}.\n"
                    f"▸ reason: <i>{REASON}</i>"
                )
            else:
                out_str = choice(AFK_REASONS)
            await message.reply(out_str)
        if chat.type == "private":
            USERS[user_id][0] += 1
        else:
            USERS[user_id][1] += 1
    else:
        if REASON:
            out_str = (
                f"▸ heyy, I'm afk {afk_time}.\n"
                f"▸ reason: <i>{REASON}</i>"
            )
        else:
            afkout = rand_array(AFK_REASONS)
            out_str = f"<i>{afkout}</i>"
        await message.reply(out_str)
        if chat.type == "private":
            USERS[user_id] = [1, 0, user_dict["mention"]]
        else:
            USERS[user_id] = [0, 1, user_dict["mention"]]
    if chat.type == "private":
        coro_list.append(
            CHANNEL.log(
                f"#PRIVATE\n{user_dict['mention']} you sent messages\n\n" f"Message: <i>{message.text}</i>"
            )
        )
    else:
        coro_list.append(
            CHANNEL.log(
                "#GRUPO\n"
                f"{user_dict['mention']} mentioned you in [{chat.title}](http://t.me/{chat.username})\n\n"
                f"<i>{message.text}</i>\n\n"
                f"[Ver Mensagem](https://t.me/c/{str(chat.id)[4:]}/{message.message_id})"
            )
        )
    coro_list.append(
        AFK_COLLECTION.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "pcount": USERS[user_id][0],
                    "gcount": USERS[user_id][1],
                    "men": USERS[user_id][2],
                }
            },
            upsert=True,
        )
    )
    await asyncio.gather(*coro_list)


@paimon.on_filters(IS_AFK_FILTER & filters.outgoing, group=-1, allow_via_bot=False)
async def handle_afk_outgoing(message: Message) -> None:
    """handle outgoing messages when afk"""
    global IS_AFK  # pylint: disable=global-statement
    IS_AFK = False
    afk_time = time_formatter(round(time.time() - TIME))
    replied: Message = await message.reply("`I'm no longer afk!`", log=__name__)
    coro_list = []
    if USERS:
        p_msg = ""
        g_msg = ""
        p_count = 0
        g_count = 0
        for pcount, gcount, men in USERS.values():
            if pcount:
                p_msg += f"👤 {men} ✉️ **{pcount}**\n"
                p_count += pcount
            if gcount:
                g_msg += f"👥 {men} ✉️ **{gcount}**\n"
                g_count += gcount
        coro_list.append(
            replied.edit(
                f"`You received {p_count + g_count} messages while you were away.`"
                f"`Please check the log for more details.\n\nTimeout: {afk_time}`",
                del_in=3,
            )
        )
        out_str = (
            f"`You have received {p_count + g_count} messages` "
            + f"`in {len(USERS)} users while you were away!\nafk time: {afk_time}`\n"
        )
        if p_count:
            out_str += f"\n**{p_count} Private Messages:**\n\n{p_msg}"
        if g_count:
            out_str += f"\n**{g_count} Group Messages:**\n\n{g_msg}"
        coro_list.append(CHANNEL.log(out_str))
        USERS.clear()
    else:
        await asyncio.sleep(3)
        coro_list.append(replied.delete())
    coro_list.append(
        asyncio.gather(
            AFK_COLLECTION.drop(),
            SAVED_SETTINGS.update_one(
                {"_id": "AFK"}, {"$set": {"on": False}}, upsert=True
            ),
        )
    )
    await asyncio.gather(*coro_list)

AFK_SLEEPING = [
    "https://telegra.ph/file/ef265a6287049e9bf6824.gif",
    "https://telegra.ph/file/5d60fe4c8750dabb9eb3e.gif",
    "https://telegra.ph/file/64bbf555fe9cf1c94b46d.gif",
    "https://telegra.ph/file/d15a273f85da98cd3e074.gif",
    "https://telegra.ph/file/b80236c923f175916caf9.gif",
    "https://telegra.ph/file/b480496461fbff8b59b11.gif",
    "https://telegra.ph/file/b71b6ef1ced2a6f84aead.gif",
    "https://telegra.ph/file/68c4d082e5ff249d635a4.gif",
    "https://telegra.ph/file/a7fd2e42e75057fffc832.gif",
]

GOING_SLEEP = [
    "https://telegra.ph/file/8fd25eec31f120d6bbd58.gif",
    "https://telegra.ph/file/9de3192c439caf5d15818.gif",
    "https://telegra.ph/file/34fa0a6c2d5482fc2c6f8.gif",
    "https://telegra.ph/file/9feae7b9f33439f81f47e.gif",
    "https://telegra.ph/file/56ff50fadae0f00101b2c.gif",
    "https://telegra.ph/file/a3e14355fae9a44c7e91f.gif",
]

AFK_REASONS = (
    "I'm busy right now. Please talk in a bag and when I come back you can just give me the bag!",
    "I'm away right now. If you need anything, leave a message after the beep: \
`beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep!`",
    "You missed me, next time aim better.",
    "I'll be back in a few minutes and if I'm not...,\nwait longer.",
    "I'm not here right now, so I'm probably somewhere else.",
    "Roses are red,\nViolets are blue,\nLeave me a message,\nAnd I'll get back to you.",
    "Sometimes the best things in life are worth waiting for…\nI'll be right back.",
    "I'll be right back,\nbut if I'm not right back,\nI'll be back later.",
    "If you haven't figured it out already,\nI'm not here.",
    "I'm away over 7 seas and 7 countries,\n7 waters and 7 continents,\n7 mountains and 7 hills,\
7 plains and 7 mounds,\n7 pools and 7 lakes,\n7 springs and 7 meadows,\
7 cities and 7 neighborhoods,\n7 blocks and 7 houses...\
    Where not even your messages can reach me!",
    "I'm away from the keyboard at the moment, but if you'll scream loud enough at your screen,\
    I might just hear you.",
    "I went that way\n>>>>>",
    "I went this way\n<<<<<",
    "Please leave a message and make me feel even more important than I already am.",
    "If I were here,\nI'd tell you where I am.\n\nBut I'm not,\nso ask me when I return...",
    "I am away!\nI don't know when I'll be back!\nHopefully a few minutes from now!",
    "I'm not available right now so please leave your name, number, \
    and address and I will stalk you later. :P",
    "Sorry, I'm not here right now.\nFeel free to talk to my userbot as long as you like.\
I'll get back to you later.",
    "I bet you were expecting an away message!",
    "Life is so short, there are so many things to do...\nI'm away doing one of them..",
    "I am not here right now...\nbut if I was...\n\nwouldn't that be awesome?",
)
