import os
from dotenv import load_dotenv

load_dotenv()

import socket
from pytz import timezone
import logging

log = logging.getLogger(__name__)

def getDefaultBool(var, default):
    return bool(int(os.getenv(var, default)))

HOSTNAME = socket.gethostname()

# env vars
# Slack webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
# Webhook for sending debug information
DEBUG_WEBHOOK = os.getenv("DEBUG_WEBHOOK", "")
DEBUG = getDefaultBool("DEBUG", 0)
DEBUG_HEALTHCHECK = getDefaultBool("DEBUG_HEALTHCHECK", 1)

# Use to override default webhook messaging settings
# Bots username
BOT_NAME = os.getenv("BOT_NAME", 'World Cup Bot')
# Bots avatar
ICON_EMOJI = os.getenv("ICON_EMOJI", ':soccer:')
# Channel to send messages to. Ex: 'random'
CHANNEL = os.getenv("CHANNEL", "")
# Channel to send debug messages
DEBUG_CHANNEL = os.getenv("DEBUG_CHANNEL", '')

TIMEZONE = timezone(os.getenv("TIMEZONE", "UTC"))
NO_SLACK = getDefaultBool("NO_SLACK", 1)

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
LOGGING_FORMAT = os.getenv("LOGGING_FORMAT", '%(asctime)s %(name)s [%(levelname)s]: %(message)s')
COLOR_LOGS = getDefaultBool("COLOR_LOGS", 0)

ONLY_SEND_DAILY_MATCHES_ONCE = getDefaultBool("ONLY_SEND_DAILY_MATCHES_ONCE", 0)
