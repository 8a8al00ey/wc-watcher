import os
import socket
from pytz import timezone
import logging

log = logging.getLogger(__name__)

HOSTNAME = socket.gethostname()

# env vars
# Slack webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
# Webhook for sending debug information
DEBUG_WEBHOOK = os.getenv("DEBUG_WEBHOOK", "")
DEBUG = eval(os.getenv("DEBUG", "False"))
DEBUG_HEALTHCHECK = eval(os.getenv("DEBUG_HEALTHCHECK", "True"))

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
NO_SLACK = eval(os.getenv("NO_SLACK", "False"))

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
LOGGING_FORMAT = os.getenv("LOGGING_FORMAT", '%(asctime)s,%(msecs)d %(levelname)s: %(message)s')
