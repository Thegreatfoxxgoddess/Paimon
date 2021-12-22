#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia

. init/logbot/logbot.sh
. init/utils.sh
. init/checks.sh

trap handleSigTerm TERM
trap handleSigInt INT
trap 'echo hi' USR1

initpaimon() {
    printLogo
    assertPrerequisites
    sendMessage "Initializing paimon ..."
    assertEnvironment
    editLastMessage "Starting paimon ..."
    printLine
}

startpaimon() {
    startLogBotPolling
    runPythonModule paimon "$@"
}

stoppaimon() {
    sendMessage "Finishing paimon ..."
    endLogBotPolling
}

handleSigTerm() {
    log "logging out with SIGTERM (143) ..."
    stoppaimon
    exit 143
}

handleSigInt() {
    log "logging out with SIGINT (130) ..."
    stoppaimon
    exit 130
}

runpaimon() {
    initpaimon
    startpaimon "$@"
    local code=$?
    stoppaimon
    return $code
}
