# pylint: disable=invalid-name, missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# Edited by Alicia


from pyrogram import Client

API_KEY = int(input("Enter API_ID: "))
API_HASH = input("Enter API_HASH: ")
with Client(':memory:', api_id=API_KEY, api_hash=API_HASH) as app:
	app.send_message(            
	  "me", f"#paimon #HU_STRING_SESSION\n\n```{await paimon.export_session_string()}```")
	print("Pronto !, string de sessão foi enviada para mensagens salvas!")

