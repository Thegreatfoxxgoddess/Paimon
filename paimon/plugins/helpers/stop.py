# this plugin is made for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)
# stolen by Alícia dark

import re

from paimon import Config


def forbidden_sudo(msg, cmd: str) -> bool:
    if msg.from_user.id not in Config.SUDO_USERS:
        return False
    return bool(
        re.search(
            rf"^(\{Config.CMD_TRIGGER})|(\{Config.SUDO_TRIGGER})(addsudo)|(delsudo)|(addscmd).*",
            cmd,
        )
    )
