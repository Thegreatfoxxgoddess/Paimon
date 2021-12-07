"""Last FM"""

# Copyright (C) 2020 BY paimon-X.
# All rights reserved.
# Inspiration from @lastfmrobot <mainly> (owned by @dangou on telegram) and...
# TheRealPhoenixBot owned by rsktg
# Code re-written by code-rgb
# For improvements Pull Request or lostb053.github.io

import asyncio

from paimon import Config, Message, get_collection, paimon
from paimon.lastfm import auth_, info, recs, ri, tglst, user

du = "https://last.fm/user/"


@paimon.on_cmd(
    "toggleprofile",
    about={
        "header": "Toggle LastFM Profile",
        "description": "toggle lastfm profile to be shown or hidden",
        "usage": "{tr}toggleprofile",
    },
)
async def toggle_lastfm_profile_(message: Message):
    """Toggle LastFM Profile"""
    data = await get_collection("CONFIGS").find_one({"_id": "SHOW_LASTFM"})
    tgl = "Hide" if data and data["on"] == "Show" else "Show"
    await asyncio.gather(
        get_collection("CONFIGS").update_one(
            {"_id": "SHOW_LASTFM"},
            {"$set": {"on": tgl}},
            upsert=True,
        ),
    )
    await message.edit("`Settings updated`", del_in=5)


@paimon.on_cmd(
    "lp",
    about={
        "header": "Get Lastfm now playing",
        "usage": "{tr}lp [lastfm username] (optional)",
    },
)
async def last_fm_(message: Message):
    """Currently Playing"""
    query = message.input_str or Config.LASTFM_USERNAME
    view_data = (await recs(query, "recenttracks", 3))[1]
    recent_song = view_data["recenttracks"]["track"]
    if len(recent_song) == 0:
        return await message.err("No Recent Tracks found", del_in=5)
    qd = f"[{query}]({du}{query})" if message.input_str else await user()
    if recent_song[0].get("@attr"):
        song_ = recent_song[0]
        sn, an = song_["name"], song_["artist"]["#text"]
        gt = (await info("track", query, an, sn))[1]["track"]
        y = [
            i.replace(" ", "_").replace("-", "_")
            for i in [tg["name"] for tg in gt["toptags"]["tag"]]
        ]
        z = [k for k in y if y != [] and k.lower() in tglst()]
        neutags = " #".join(z[i] for i in range(min(len(z), 4)))
        img = ri(recent_song[0].get("image")[3].get("#text"))
        rep = f"[\u200c]({img})**{qd}** is currently listening to: \n🎧  `{an} - {sn}`"
        rep += ", ♥️" if gt["userloved"] != "0" else ""
        rep += f"\n#{neutags}" if neutags != "" else ""
    else:
        rep = f"**{qd}** was listening to ...\n"
        for song_ in recent_song:
            sn, an = song_["name"], song_["artist"]["#text"]
            rep += f"\n🎧  {an} - {sn}"
            rep += (
                ", ♥️"
                if (await info("track", query, an, sn))[1]["track"]["userloved"] != "0"
                else ""
            )
        playcount = view_data.get("recenttracks").get("@attr").get("total")
        rep += f"`\n\nTotal Scrobbles = {playcount}`"
    await message.edit(rep)


@paimon.on_cmd(
    "linfo",
    about={
        "header": "Get Lastfm user info",
        "usage": "{tr}linfo [lastfm username] (optional)",
    },
)
async def last_fm_user_info_(message: Message):
    """Shows User Info"""
    query = message.input_str or Config.LASTFM_USERNAME
    lastuser = (await info("user", query, "", ""))[1]["user"]
    lastimg = lastuser.get("image")[3].get("#text")
    result = ""
    result += f"[\u200c]({lastimg})" if lastimg else ""
    qd = f"[{query}]({du}{query})" if message.input_str else await user()
    result += f"LastFM User Info for **{qd}**:\n**User:** {query}\n"
    name = lastuser.get("realname")
    result += f"  🔰 **Name:** {name}\n" if name != "" else ""
    result += f"  🎵 **Total Scrobbles:** {lastuser['playcount']}\n"
    country = lastuser.get("country")
    result += f"  🌍 **Country:** {country}\n" if country != "None" else ""
    await message.edit(result)


@paimon.on_cmd(
    "pc",
    about={
        "header": "Get Lastfm user playcount",
        "usage": "{tr}pc [lastfm username] (optional)",
    },
)
async def last_pc_(message: Message):
    """Shows Playcount"""
    query = message.input_str or Config.LASTFM_USERNAME
    lastuser = (await info("user", query, "", ""))[1]["user"]["playcount"]
    qd = f"[{query}]({du}{query})" if message.input_str else await user()
    await message.edit(
        f"{qd}'s playcount:\n{lastuser}",
        disable_web_page_preview=True,
    )


@paimon.on_cmd(
    "loved",
    about={
        "header": "Get Lastfm Loved Tracks",
        "usage": "{tr}loved [lastfm username] (optional)",
    },
)
async def last_fm_loved_tracks_(message: Message):
    """Shows Liked Songs"""
    query = message.input_str or Config.LASTFM_USERNAME
    tracks = (await recs(query, "lovedtracks", 20))[1]["lovedtracks"]["track"]
    if len(tracks) == 0:
        return await message.edit("You Don't have any Loved tracks yet.")
    qd = f"[{query}]({du}{query})" if message.input_str else await user()
    rep = f"**{qd}'s Liked (♥️) Tracks**"
    for song_ in tracks:
        song_name, artist_name = song_["name"], song_["artist"]["name"]
        rep += f"\n🎧  **{artist_name}** - {song_name}"
    await message.edit(rep, disable_web_page_preview=True)


@paimon.on_cmd(
    "hp",
    about={
        "header": "Get Upto 20 recently played LastFm Songs",
        "usage": "{tr}hp [lastFM username] (optional)",
    },
)
async def last_fm_played_(message: Message):
    """Shows Recently Played Songs"""
    query = message.input_str or Config.LASTFM_USERNAME
    recent_song = (await recs(query, "recenttracks", 20))[1]["recenttracks"]["track"]
    if len(recent_song) == 0:
        return await message.err("No Recent Tracks found", del_in=5)
    qd = f"[{query}]({du}{query})" if message.input_str else await user()
    rep = f"**{qd}**'s recently played 🎵 songs:\n"
    for song_ in recent_song:
        sn, an = song_["name"], song_["artist"]["#text"]
        rep += f"\n🎧  {an} - {sn}"
        rep += (
            ", ♥️"
            if (await info("track", query, an, sn))[1]["track"]["userloved"] != "0"
            else ""
        )
    await message.edit(rep, disable_web_page_preview=True)


@paimon.on_cmd(
    "loveit",
    about={
        "header": "love recently playing song",
        "usage": "{tr}loveit",
    },
)
async def last_fm_love_(message: Message):
    """Loves Currently Playing Song"""
    await message.edit("Loving Currently Playing...")
    recent_song = (await recs(Config.LASTFM_USERNAME, "recenttracks", 2))[1][
        "recenttracks"
    ]["track"]
    if len(recent_song) == 0 or not recent_song[0].get("@attr"):
        return await message.err("No Currently Playing Track found", del_in=10)
    song_ = recent_song[0]
    anm, snm = song_["artist"]["#text"], song_["name"]
    auth_().get_track(anm, snm).love()
    img = ri(song_.get("image")[3].get("#text"))
    await message.edit(
        f"Loved currently playing track...\n`{anm} - {snm}` [\u200c]({img})"
    )


@paimon.on_cmd(
    "unloveit",
    about={
        "header": "unlove recently playing song",
        "usage": "{tr}unloveit",
    },
)
async def last_fm_unlove_(message: Message):
    """UnLoves Currently Playing Song"""
    await message.edit("UnLoving Currently Playing...")
    recent_song = (await recs(Config.LASTFM_USERNAME, "recenttracks", 2))[1][
        "recenttracks"
    ]["track"]
    if len(recent_song) == 0 or not recent_song[0].get("@attr"):
        return await message.err("No Currently Playing Track found", del_in=10)
    song_ = recent_song[0]
    anm, snm = song_["artist"]["#text"], song_["name"]
    auth_().get_track(anm, snm).unlove()
    img = ri(song_.get("image")[3].get("#text"))
    await message.edit(
        f"UnLoved currently playing track...\n`{anm} - {snm}` [\u200c]({img})"
    )


# inspired from @lastfmrobot's compat
@paimon.on_cmd(
    "compat",
    about={
        "header": "Compat",
        "description": "check music compat level with other lastfm users",
        "usage": "{tr}compat lastfmuser or {tr}compat lastfmuser1|lastfmuser2",
    },
)
async def lastfm_compat_(message: Message):
    """Shows Music Compatibility"""
    msg = message.input_str
    if not msg:
        return await message.edit("Please check `{tr}help Compat`")
    diff = "|" in msg
    us1, us2 = msg.split("|") if diff else Config.LASTFM_USERNAME, msg
    ta = "topartists"
    ta1, ta2 = (await recs(us1, ta, 500))[1][ta]["artist"], (await recs(us2, ta, 500))[
        1
    ][ta]["artist"]
    ad1, ad2 = [n["name"] for n in ta1], [n["name"] for n in ta2]
    display = f"**{us1 if diff else await user()}** and **[{us2}]({du}{us2})**"
    comart = [value for value in ad2 if value in ad1]
    disart = ", ".join({comart[r] for r in range(min(len(comart), 5))})
    compat = min((len(comart) * 100 / 40), 100)
    rep = f"{display} both listen to __{disart}__...\nMusic Compatibility is **{compat}%**"
    await message.edit(rep, disable_web_page_preview=True)
