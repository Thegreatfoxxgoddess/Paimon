# plugin for paimon-X by @Kakashi_HTK(tg)/@ashwinstr(gh)
# please ask before porting to other bots, thank you


from os import system

from git import Repo
from git.exc import GitCommandError

from paimon import Config, Message, paimon


@paimon.on_cmd(
    "update_f",
    about={
        "header": "check update commits",
        "usage": "{tr}update_f",
    },
)
async def fetch_(message: Message):
    """check update commits"""
    repo = Repo()
    branch = "master"
    try:
        out = _get_updates(repo, branch)
    except GitCommandError as g_e:
        if "128" in str(g_e):
            system(
                f"git fetch {Config.UPSTREAM_REMOTE} {branch} && git checkout -f {branch}"
            )
            out = _get_updates(repo, branch)
    if out:
        change_log = f"**New UPDATE available for [{branch}]:\n\nCHANGELOG **\n\n"
        await message.edit_or_send_as_file(
            change_log + out, disable_web_page_preview=True
        )
    else:
        await message.edit(f"**Paimon is up-to-date with [{branch}]**", del_in=5)


def _get_updates(repo: Repo, branch: str) -> str:
    repo.remote(Config.UPSTREAM_REMOTE).fetch(branch)
    upst = Config.UPSTREAM_REPO.rstrip("/")
    out = ""
    upst = Config.UPSTREAM_REPO.rstrip("/")
    for i in repo.iter_commits(f"HEAD..{Config.UPSTREAM_REMOTE}/{branch}"):
        out += (
            f"**#{i.count()}** : [{i.summary}]({upst}/commit/{i})  __{i.author}__\n\n"
        )
    return out
