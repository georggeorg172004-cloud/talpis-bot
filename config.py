import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "0"))
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "1g1jj_ifBAErWexiS_XehNn1dfHH87rQMHHWQHwR9538")
SHEET_GID = os.getenv("SHEET_GID", "459982512")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))
SNAPSHOT_FILE = "snapshot.json"

_raw = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS: set[int] = (
    {int(x.strip()) for x in _raw.split(",") if x.strip().isdigit()}
    if _raw else set()
)
