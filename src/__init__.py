import logging, coloredlogs
from . import settings

if settings.COLOR_LOGS:
  coloredlogs.install(
      level=settings.LOGGING_LEVEL,
      fmt=settings.LOGGING_FORMAT,
  )
else:
  logging.basicConfig(
      level=settings.LOGGING_LEVEL,
      format=settings.LOGGING_FORMAT,
  )

log = logging.getLogger(__name__)

log.info("setting up logging w/ level %s...",
         logging.getLevelName(log.getEffectiveLevel()))

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
log.info("ONLY_SEND_DAILY_MATCHES_ONCE: %s" % settings.ONLY_SEND_DAILY_MATCHES_ONCE)
