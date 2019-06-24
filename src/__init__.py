import logging
from . import settings

logging.basicConfig(
    level=settings.LOGGING_LEVEL,
    format=settings.LOGGING_FORMAT,
)

log = logging.getLogger(__name__)

if settings.NO_SLACK:
    log.warn("===================================================================")
    log.warn("Running in NO_SLACK mode, sending events to stdout instead of slack")
    log.warn("===================================================================\n")

log.info("WEBHOOK_URL: %s" % settings.WEBHOOK_URL)
log.info("DEBUG_WEBHOOK: %s" % settings.DEBUG_WEBHOOK)
log.info("DEBUG: %s" % settings.DEBUG)
log.info("BOT_NAME: %s" % settings.BOT_NAME)
log.info("ICON_EMOJI: %s" % settings.ICON_EMOJI)
log.info("CHANNEL: %s" % settings.CHANNEL)
log.info("DEBUG_CHANNEL: %s" % settings.DEBUG_CHANNEL)
log.info("TIMEZONE: %s" % settings.TIMEZONE)
