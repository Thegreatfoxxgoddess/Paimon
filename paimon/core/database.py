# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia

__all__ = ['get_collection']

import asyncio
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticClient, AgnosticDatabase, AgnosticCollection

from paimon import logging, Config, logbot

_LOG = logging.getLogger(__name__)
_LOG_STR = "$$$>>> %s <<<$$$"

logbot.edit_last_msg("Connecting to Database ...", _LOG.info, _LOG_STR)

_MGCLIENT: AgnosticClient = AsyncIOMotorClient(Config.DB_URI)
_RUN = asyncio.get_event_loop().run_until_complete

if "paimon" in _RUN(_MGCLIENT.list_database_names()):
    _LOG.info(_LOG_STR, "Paimon Database Found :) => Agora logando nele...")
else:
    _LOG.info(_LOG_STR, "Paimon database not found :( => Creating new Database...")

_DATABASE: AgnosticDatabase = _MGCLIENT["paimon"]
_COL_LIST: List[str] = _RUN(_DATABASE.list_collection_names())


def get_collection(name: str) -> AgnosticCollection:
    """ Create or get collection from your database """
    if name in _COL_LIST:
        _LOG.debug(_LOG_STR, f"{name} Found collection :) => now logging into it...")
    else:
        _LOG.debug(_LOG_STR, f"{name} Collection not found :( => creating new collection...")
    return _DATABASE[name]


def _close_db() -> None:
    _MGCLIENT.close()


logbot.del_last_msg()
