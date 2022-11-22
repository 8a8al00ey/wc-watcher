import requests
import logging
import json

from . import settings

log = logging.getLogger(__name__)

def send_event(event, url=settings.WEBHOOK_URL, channel=''):
    if settings.NO_SLACK:
        log.info("{}\n".format(event))
        return

    log.debug("send event: {}".format(event))
    headers = {'Content-Type': 'application/json'}
    payload = { 'text': event }

    #if channel is not '':
    #     payload['channel'] = channel
    # elif settings.CHANNEL is not '':
    #     payload['channel'] = CHANNEL

    # if settings.BOT_NAME is not '':
    #     payload['username'] = BOT_NAME
    # if settings.ICON_EMOJI is not '':
    #     payload['icon_emoji'] = ICON_EMOJI

    try:
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as ex:
        log.error('Failed to send message: {}'.format(ex))
        return
    except requests.exceptions.ConnectionError as ex:
        log.error('Failed to send message: {}'.format(ex))
        return
