# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia

__all__ = ['Chats']

from .conversation import Conversation
from .send_read_acknowledge import SendReadAcknowledge


class Chats(Conversation, SendReadAcknowledge):
    """ methods.chats """
