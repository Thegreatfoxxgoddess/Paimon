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
    sendMessage "Inicializando paimon ..."
    assertEnvironment
    editLastMessage "Iniciando paimon ..."
    printLine
}

startpaimon() {
    startLogBotPolling
    runPythonModule paimon "$@"
}

stoppaimon() {
    sendMessage "Finalizando paimon ..."
    endLogBotPolling
}

handleSigTerm() {
    log "Saindo com SIGTERM (143) ..."
    stoppaimon
    exit 143
}

handleSigInt() {
    log "Saindo com SIGINT (130) ..."
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
