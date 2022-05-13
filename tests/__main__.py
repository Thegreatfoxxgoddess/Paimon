# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia

import os

from paimon import paimon


async def _worker() -> None:
    chat_id = int(os.environ.get("CHAT_ID") or 0)
    type_ = 'unofficial' if os.path.exists("../paimon/plugins/unofficial") else 'main'
    await paimon.send_message(chat_id, f'`{type_} build completed!`')

if __name__ == "__main__":
    paimon.begin(_worker())
    print('paimon test is complete!')
