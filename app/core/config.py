from dotenv import load_dotenv

import os

load_dotenv()

URL = os.getenv("URL")
ECHO = os.getenv("ECHO") == True
SMSC_LOGIN = os.getenv("SMSC_LOGIN")
SMSC_PSW = os.getenv("SMSC_PSW")
SMSC_TG = os.getenv("SMSC_TG")
SMSC_URL = os.getenv("SMSC_URL")