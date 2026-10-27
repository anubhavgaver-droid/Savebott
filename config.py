# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os

# Login feature, if you want then True , if you don't want then False
LOGIN_SYSTEM = bool(os.environ.get('LOGIN_SYSTEM', True)) # True or False

if LOGIN_SYSTEM == False:
    # if login system is False then fill your tg account session below 
    STRING_SESSION = os.environ.get("STRING_SESSION", "BQJGR_0AiZju-oXhEUl1X0RMYwqTWWYrusBnugBLu6vdyxtxCZVFo-VSdPXvbmMr39WDc7ViZnGIQpMslQsNKVC147SShOUIboBokInO0Ec7iVV-106nn73segROEEGDkROV0MruK-_NkdvJW4iO9OCP8jklYIQ9iRul7771Fd7Pzz0M325k4zGry8q47vDszhIbi3drK7y4DG50E0So5VNvaGMHX9F1VQYsZ45aRoDG_RnO0ew8UzieXRwqYMYkT9AZy_qOiAygIPrF4bn8AukCEgRemNO1WkiEoEVxCir3g4iFXBFsUsT3z0MZpixAyH9xMcUsFHeBZJYzR1CLe9gSAcohrwAAAAFflE-jAA")
else:
    STRING_SESSION = None

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8305985325:AAEeNzWRLLbBuB4SSGnxWIGC_GTTiAujNVc")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "38160381"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "9f7879d8793fd4bfd887d023cc1d3872")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "5898522531"))

# Admin Username for Plan Purchase Contact Button (Yahan apna username likhein @ ke bina)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "KCXRY")

# Your Channel Id In Which Bot Upload Downloaded Video/File/Message etc.
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")

# Your Mongodb Database Url
DB_URI = os.environ.get("DB_URI", "mongodb+srv://Anubhav09:kalu1234@anubhav09.ljn6xdp.mongodb.net/?appName=Anubhav09") 
DB_NAME = os.environ.get("DB_NAME", "vjsavecontentbot")

# Increase time as much as possible to avoid floodwait, spamming and tg account ban issues.
WAITING_TIME = int(os.environ.get("WAITING_TIME", "10")) # time in seconds

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
