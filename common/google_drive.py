from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from typing import List

CREDENTIALS_FILE = "mycreds.txt"
NBA_TEAM_FOLDER_ID = "18AewcJS5xNzByu64Qgo_jDN8w9lWHcQ9"
NBA_PLAYER_FOLDER_ID = "1xj3llDpz3q1r338RYldWkmUFLNc8LZyT"

def upload_file(folder_id: str, path: str):
	try:
		gauth = GoogleAuth()

		gauth.LoadCredentialsFile(CREDENTIALS_FILE)
		if gauth.credentials is None:
			# Authenticate if they're not there
			gauth.LocalWebserverAuth()
		elif gauth.access_token_expired:
			# Refresh them if expired
			gauth.Refresh()
		else:
			# Initialize the saved creds
			gauth.Authorize()
		# Save the current credentials to a file
		gauth.SaveCredentialsFile(CREDENTIALS_FILE)

		# Creates local webserver and auto
		# handles authentication.
		gauth.LocalWebserverAuth()	
		drive = GoogleDrive(gauth)

		f = drive.CreateFile({'parents': [{'id': folder_id}]})
		f.SetContentFile(path)
		f.Upload()
		f = None
	except Exception as e:
		raise e
