#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia

urlEncode() {
    echo "<code>$(echo "${1#\~}" | sed -E 's/(\\t)|(\\n)/ /g' |
        curl -Gso /dev/null -w %{url_effective} --data-urlencode @- "" | cut -c 3-)</code>"
}
