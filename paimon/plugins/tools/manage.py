""" manage your paimon :) """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia

import asyncio
import os

from paimon import Config, Message, paimon
from paimon.helpers import Start
from paimon.plugins import ROOT
from paimon.utils import get_import_path


@paimon.on_cmd(
    "status",
    about={
        "header": "list plugins, commands, filters status",
        "flags": {"-p": "plugin", "-c": "command", "-f": "filter"},
        "usage": "{tr}status [flags] [name]",
        "examples": [
            "{tr}status",
            "{tr}status -p",
            "{tr}status -p gdrive",
            "{tr}status -c {tr}gls",
        ],
    },
    del_pre=True,
    allow_channels=False,
)
async def status(message: Message) -> None:
    """view current status"""
    name_ = message.filtered_input_str
    type_ = list(message.flags)
    if not type_:
        out_str = f"""**--paimon status--**

🗃 **Plugins** : `{len(paimon.manager.plugins)}`
        ✅ **Loaded** : `{len(paimon.manager.loaded_plugins)}`
        ➕ **Enabled** : `{len(paimon.manager.enabled_plugins)}`
        ➖ **Disabled** : `{len(paimon.manager.disabled_plugins)}`
        ❎ **Unloaded** : `{len(paimon.manager.unloaded_plugins)}`

⚔ **Commands** : `{len(paimon.manager.commands)}`
        ✅ **Loaded** : `{len(paimon.manager.loaded_commands)}`
        ➕ **Enabled** : `{len(paimon.manager.enabled_commands)}`
        ➖ **Disabled** : `{len(paimon.manager.disabled_commands)}`
        ❎ **Unloaded** : `{len(paimon.manager.unloaded_commands)}`

⚖ **Filters** : `{len(paimon.manager.filters)}`
        ✅ **Loaded** : `{len(paimon.manager.loaded_filters)}`
        ➕ **Enabled** : `{len(paimon.manager.enabled_filters)}`
        ➖ **Disabled** : `{len(paimon.manager.disabled_filters)}`
        ❎ **Unloaded** : `{len(paimon.manager.unloaded_filters)}`
"""
    elif "p" in type_:
        if name_:
            if name_ in paimon.manager.plugins:
                plg = paimon.manager.plugins[name_]
                out_str = f"""🗃 **--Plugin Status--** 🗃

🔖 **Name** : `{plg.name}`
📝 **Doc** : `{plg.doc}`
✅ **Loaded** : `{plg.is_loaded}`
➕ **Enabled** : `{plg.is_enabled}`

⚔ **Commands** : `{len(plg.commands)}`
        `{'`,    `'.join((cmd.name for cmd in plg.commands))}`
        ✅ **Loaded** : `{len(plg.loaded_commands)}`
        ➕ **Enabled** : `{len(plg.enabled_commands)}`
        ➖ **Disabled** : `{len(plg.disabled_commands)}`
        `{'`,    `'.join((cmd.name for cmd in plg.disabled_commands))}`
        ❎ **Unloaded** : `{len(plg.unloaded_commands)}`
        `{'`,    `'.join((cmd.name for cmd in plg.unloaded_commands))}`

⚖ **Filters** : `{len(plg.filters)}`
        ✅ **Loaded** : `{len(plg.loaded_filters)}`
        ➕ **Enabled** : `{len(plg.enabled_filters)}`
        `{'`,    `'.join((flt.name for flt in plg.enabled_filters))}`
        ➖ **Disabled** : `{len(plg.disabled_filters)}`
        `{'`,    `'.join((flt.name for flt in plg.disabled_filters))}`
        ❎ **Unloaded** : `{len(plg.unloaded_filters)}`
        `{'`,    `'.join((flt.name for flt in plg.unloaded_filters))}`
"""
            else:
                await message.err(f"plugin : `{name_}` not found!")
                return
        else:
            out_str = f"""🗃 **--Plugins Status--** 🗃

🗂 **Total** : `{len(paimon.manager.plugins)}`
✅ **Loaded** : `{len(paimon.manager.loaded_plugins)}`
➕ **Enabled** : `{len(paimon.manager.enabled_plugins)}`
➖ **Disabled** : `{len(paimon.manager.disabled_plugins)}`
        `{'`,    `'.join((cmd.name for cmd in paimon.manager.disabled_plugins))}`
❎ **Unloaded** : `{len(paimon.manager.unloaded_plugins)}`
        `{'`,    `'.join((cmd.name for cmd in paimon.manager.unloaded_plugins))}`
"""
    elif "c" in type_:
        if name_:
            if not name_.startswith(Config.CMD_TRIGGER):
                n_name_ = Config.CMD_TRIGGER + name_
            if name_ in paimon.manager.commands:
                cmd = paimon.manager.commands[name_]
            elif n_name_ in paimon.manager.commands:
                cmd = paimon.manager.commands[n_name_]
            else:
                await message.err(f"command : {name_} not found!")
                return
            out_str = f"""⚔ **--Command Status--** ⚔

🔖 **Name** : `{cmd.name}`
📝 **Doc** : `{cmd.doc}`
🤖 **Via Bot** : `{cmd.allow_via_bot}`
✅ **Loaded** : `{cmd.is_loaded}`
➕ **Enabled** : `{cmd.is_enabled}`
"""
        else:
            out_str = f"""⚔ **--Commands Status--** ⚔

🗂 **Total** : `{len(paimon.manager.commands)}`
✅ **Loaded** : `{len(paimon.manager.loaded_commands)}`
➕ **Enabled** : `{len(paimon.manager.enabled_commands)}`
➖ **Disabled** : `{len(paimon.manager.disabled_commands)}`
        `{'`,    `'.join((cmd.name for cmd in paimon.manager.disabled_commands))}`
❎ **Unloaded** : `{len(paimon.manager.unloaded_commands)}`
        `{'`,    `'.join((cmd.name for cmd in paimon.manager.unloaded_commands))}`
"""
    elif "f" in type_:
        if name_:
            if name_ in paimon.manager.filters:
                flt = paimon.manager.filters[name_]
                out_str = f"""⚖ **--Filter Status--** ⚖

🔖 **Name** : `{flt.name}`
📝 **Doc** : `{flt.doc}`
🤖 **Via Bot** : `{flt.allow_via_bot}`
✅ **Loaded** : `{flt.is_loaded}`
➕ **Enabled** : `{flt.is_enabled}`
"""
            else:
                await message.err(f"filter : {name_} not found!")
                return
        else:
            out_str = f"""⚖ **--Filters Status--** ⚖

🗂 **Total** : `{len(paimon.manager.filters)}`
✅ **Loaded** : `{len(paimon.manager.loaded_filters)}`
➕ **Enabled** : `{len(paimon.manager.enabled_filters)}`
        `{'`,    `'.join((flt.name for flt in paimon.manager.enabled_filters))}`
➖ **Disabled** : `{len(paimon.manager.disabled_filters)}`
        `{'`,    `'.join((flt.name for flt in paimon.manager.disabled_filters))}`
❎ **Unloaded** : `{len(paimon.manager.unloaded_filters)}`
        `{'`,    `'.join((flt.name for flt in paimon.manager.unloaded_filters))}`
"""
    else:
        await message.err("invalid input flag!")
        return
    await message.edit(out_str.replace("        ``\n", ""), del_in=0)


@paimon.on_cmd(
    "enable",
    about={
        "header": "enable plugins, commands, filters",
        "flags": {"-p": "plugin", "-c": "command", "-f": "filter"},
        "usage": "{tr}enable [flags] [name | names]",
        "examples": ["{tr}enable -p gdrive", "{tr}enable -c gls gup"],
    },
    del_pre=True,
    allow_channels=False,
)
async def enable(message: Message) -> None:
    """enable plugins, commands, filters"""
    if not message.flags:
        await message.err("flag required!")
        return
    if not message.filtered_input_str:
        await message.err("name required!")
        return
    await message.edit("`Enabling...`")
    names_ = message.filtered_input_str.split(" ")
    type_ = list(message.flags)
    if "p" in type_:
        found = set(names_).intersection(set(paimon.manager.plugins))
        if found:
            out = await paimon.manager.enable_plugins(list(found))
            if out:
                out_str = "**--Enabled Plugin(s)--**\n\n"
                for plg_name, cmds in out.items():
                    out_str += f"**{plg_name}** : `{'`,    `'.join(cmds)}`\n"
            else:
                out_str = f"already enabled! : `{'`,    `'.join(names_)}`"
        else:
            await message.err(f"plugins : {', '.join(names_)} not found!")
            return
    elif "c" in type_:
        for t_name in names_:
            if not t_name.startswith(Config.CMD_TRIGGER):
                names_.append(Config.CMD_TRIGGER + t_name)
        found = set(names_).intersection(set(paimon.manager.commands))
        if found:
            out = await paimon.manager.enable_commands(list(found))
            if out:
                out_str = "**--Enabled Command(s)--**\n\n"
                out_str += f"`{'`,    `'.join(out)}`"
            else:
                out_str = f"already enabled! : `{'`,    `'.join(names_)}`"
        else:
            await message.err(f"commands : {', '.join(names_)} not found!")
            return
    elif "f" in type_:
        found = set(names_).intersection(set(paimon.manager.filters))
        if found:
            out = await paimon.manager.enable_filters(list(found))
            if out:
                out_str = "**--Enabled Filter(s)--**\n\n"
                out_str += f"`{'`,    `'.join(out)}`"
            else:
                out_str = f"already enabled! : `{'`,    `'.join(names_)}`"
        else:
            await message.err(f"filters : {', '.join(names_)} not found!")
            return
    else:
        await message.err("invalid input flag!")
        return
    await message.edit(out_str, del_in=0, log=__name__)


@paimon.on_cmd(
    "disable",
    about={
        "header": "disable plugins, commands, filters",
        "flags": {"-p": "plugin", "-c": "command", "-f": "filter"},
        "usage": "{tr}disable [flags] [name | names]",
        "examples": ["{tr}disable -p gdrive", "{tr}disable -c gls gup"],
    },
    del_pre=True,
    allow_channels=False,
)
async def disable(message: Message) -> None:
    """disable plugins, commands, filters"""
    if not message.flags:
        await message.err("flag required!")
        return
    if not message.filtered_input_str:
        await message.err("name required!")
        return
    await message.edit("`Disabling...`")
    names_ = message.filtered_input_str.split(" ")
    type_ = list(message.flags)
    if "p" in type_ and names_:
        found = set(names_).intersection(set(paimon.manager.plugins))
        if found:
            out = await paimon.manager.disable_plugins(list(found))
            if out:
                out_str = "**--Disabled Plugin(s)--**\n\n"
                for plg_name, cmds in out.items():
                    out_str += f"**{plg_name}** : `{'`,    `'.join(cmds)}`\n"
            else:
                out_str = f"already disabled! : `{'`,    `'.join(names_)}`"
        else:
            await message.err(f"plugins : {', '.join(names_)} not found!")
            return
    elif "c" in type_ and names_:
        for t_name in names_:
            if not t_name.startswith(Config.CMD_TRIGGER):
                names_.append(Config.CMD_TRIGGER + t_name)
        found = set(names_).intersection(set(paimon.manager.commands))
        if found:
            out = await paimon.manager.disable_commands(list(found))
            if out:
                out_str = "**--Disabled Command(s)--**\n\n"
                out_str += f"`{'`,    `'.join(out)}`"
            else:
                out_str = f"already disabled! : `{'`,    `'.join(names_)}`"
        else:
            await message.err(f"commands : {', '.join(names_)} not found!")
            return
    elif "f" in type_ and names_:
        found = set(names_).intersection(set(paimon.manager.filters))
        if found:
            out = await paimon.manager.disable_filters(list(found))
            if out:
                out_str = "**--Disabled Filter(s)--**\n\n"
                out_str += f"`{'`,    `'.join(out)}`"
            else:
                out_str = f"already disabled! : `{'`,    `'.join(names_)}`"
        else:
            await message.err(f"filters : {', '.join(names_)} not found!")
            return
    else:
        await message.err("invalid input flag!")
        return
    await message.edit(out_str, del_in=0, log=__name__)


@paimon.on_cmd(
    "load",
    about={
        "header": "load plugins, commands, filters",
        "flags": {"-p": "plugin", "-c": "command", "-f": "filter"},
        "usage": "{tr}load [reply to plugin] to load from file\n"
        "{tr}load [flags] [name | names]",
        "examples": ["{tr}load -p gdrive", "{tr}load -c gls gup"],
    },
    del_pre=True,
    allow_channels=False,
)
async def load(message: Message) -> None:
    """load plugins, commands, filters"""
    if message.flags:
        if not message.filtered_input_str:
            await message.err("name required!")
            return
        await message.edit("`Loading...`")
        names_ = message.filtered_input_str.split(" ")
        type_ = list(message.flags)
        if "p" in type_:
            found = set(names_).intersection(set(paimon.manager.plugins))
            if found:
                out = await paimon.manager.load_plugins(list(found))
                if out:
                    out_str = "**--Loaded Plugin(s)--**\n\n"
                    for plg_name, cmds in out.items():
                        out_str += f"**{plg_name}** : `{'`,    `'.join(cmds)}`\n"
                else:
                    out_str = f"already loaded! : `{'`,    `'.join(names_)}`"
            else:
                await message.err(f"plugins : {', '.join(names_)} not found!")
                return
        elif "c" in type_:
            for t_name in names_:
                if not t_name.startswith(Config.CMD_TRIGGER):
                    names_.append(Config.CMD_TRIGGER + t_name)
            found = set(names_).intersection(set(paimon.manager.commands))
            if found:
                out = await paimon.manager.load_commands(list(found))
                if out:
                    out_str = "**--Loaded Command(s)--**\n\n"
                    out_str += f"`{'`,    `'.join(out)}`"
                else:
                    out_str = f"already loaded! : `{'`,    `'.join(names_)}`"
            else:
                await message.err(f"commands : {', '.join(names_)} not found!")
                return
        elif "f" in type_:
            found = set(names_).intersection(set(paimon.manager.filters))
            if found:
                out = await paimon.manager.load_filters(list(found))
                if out:
                    out_str = "**--Loaded Filter(s)--**\n\n"
                    out_str += f"`{'`,    `'.join(out)}`"
                else:
                    out_str = f"already loaded! : `{'`,    `'.join(names_)}`"
            else:
                await message.err(f"filters : {', '.join(names_)} not found!")
                return
        else:
            await message.err("invalid input flag!")
            return
        await message.edit(out_str, del_in=0, log=__name__)
    else:
        await message.edit("`Loading...`")
        restart_ = False
        replied = message.reply_to_message
        if replied and replied.document:
            file_ = replied.document
            if file_.file_name.endswith(".py") and file_.file_size < 2**20:
                if not os.path.isdir(Config.TMP_PATH):
                    os.makedirs(Config.TMP_PATH)
                t_path = os.path.join(Config.TMP_PATH, file_.file_name)
                if os.path.isfile(t_path):
                    os.remove(t_path)
                    restart_ = True
                await replied.download(file_name=t_path)
                plugin = get_import_path(ROOT, t_path)
                try:
                    await paimon.load_plugin(plugin, reload_plugin=True)
                    await paimon.finalize_load()
                except (ImportError, SyntaxError, NameError) as i_e:
                    await message.err(i_e)
                else:
                    out_ = f"`Loaded {plugin} `"
                    del_in_ = 3
                    if restart_:
                        out_ += "`and now restarting...`"
                        del_in_ = -1
                    end_msg = await message.edit(out_, del_in=del_in_, log=__name__)
                    if restart_:
                        await Start.save_msg(
                            end_msg, f"`Plugin {plugin} loaded successfully...`"
                        )
                        asyncio.get_event_loop().create_task(paimon.restart())
            else:
                await message.edit("`Plugin Not Found`")
        else:
            await message.edit(f"pls check `{Config.CMD_TRIGGER}help load` !")


@paimon.on_cmd(
    "unload",
    about={
        "header": "unload plugins, commands, filters",
        "flags": {"-p": "plugin", "-c": "command", "-f": "filter"},
        "usage": "{tr}unload [flags] [name | names]",
        "examples": ["{tr}unload -p gdrive", "{tr}unload -c gls gup"],
    },
    del_pre=True,
    allow_channels=False,
)
async def unload(message: Message) -> None:
    """unload plugins, commands, filters"""
    if not message.flags:
        await message.err("flag required!")
        return
    if not message.filtered_input_str:
        await message.err("name required!")
        return
    await message.edit("`UnLoading...`")
    names_ = message.filtered_input_str.split(" ")
    type_ = list(message.flags)
    if "p" in type_ and names_:
        found = set(names_).intersection(set(paimon.manager.plugins))
        if found:
            out = await paimon.manager.unload_plugins(list(found))
            if out:
                out_str = "**--Unloaded Plugin(s)--**\n\n"
                for plg_name, cmds in out.items():
                    out_str += f"**{plg_name}** : `{'`,    `'.join(cmds)}`\n"
            else:
                out_str = f"already unloaded! : `{'`,    `'.join(names_)}`"
        else:
            await message.err(f"plugins : {', '.join(names_)} not found!")
            return
    elif "c" in type_ and names_:
        for t_name in names_:
            if not t_name.startswith(Config.CMD_TRIGGER):
                names_.append(Config.CMD_TRIGGER + t_name)
        found = set(names_).intersection(set(paimon.manager.commands))
        if found:
            out = await paimon.manager.unload_commands(list(found))
            if out:
                out_str = "**--Unloaded Command(s)--**\n\n"
                out_str += f"`{'`,    `'.join(out)}`"
            else:
                out_str = f"already unloaded! : `{'`,    `'.join(names_)}`"
        else:
            await message.err(f"commands : {', '.join(names_)} not found!")
            return
    elif "f" in type_ and names_:
        found = set(names_).intersection(set(paimon.manager.filters))
        if found:
            out = await paimon.manager.unload_filters(list(found))
            if out:
                out_str = "**--Unloaded Filter(s)--**\n\n"
                out_str += f"`{'`,    `'.join(out)}`"
            else:
                out_str = f"already unloaded! : `{'`,    `'.join(names_)}`"
        else:
            await message.err(f"filters : {', '.join(names_)} not found!")
            return
    else:
        await message.err("invalid input flag!")
        return
    await message.edit(out_str, del_in=0, log=__name__)


@paimon.on_cmd("reload", about={"header": "Reload all plugins"}, allow_channels=False)
async def reload_(message: Message) -> None:
    """Reload all plugins"""
    await message.edit("`Reloading All Plugins`")
    await message.edit(
        f"`Reloaded {await paimon.reload_plugins()} Plugins`", del_in=3, log=__name__
    )


@paimon.on_cmd(
    "clear", about={"header": "clear all save filters in DB"}, allow_channels=False
)
async def clear_(message: Message) -> None:
    """clear all save filters in DB"""
    await message.edit("`Clearing DB...`")
    await message.edit(
        f"**Cleared Filters** : `{await paimon.manager.clear()}`",
        del_in=3,
        log=__name__,
    )
