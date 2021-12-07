#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia

Message() {
    . <(sed "s/_Message/$1/g" init/logbot/core/types/messageClass.sh)
}
