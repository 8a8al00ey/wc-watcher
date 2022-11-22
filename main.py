from src import settings, fifa, slack

import time
import os
import asyncio
import logging
from datetime import datetime, timedelta, date
from concurrent.futures import ProcessPoolExecutor

log = logging.getLogger(__name__)

def heart_beat():
    count = 0
    slack.send_event('Coming up on {}'.format(settings.HOSTNAME), url=settings.DEBUG_WEBHOOK, channel=settings.DEBUG_CHANNEL)
    if settings.DEBUG_HEALTHCHECK:
        while True:
            count = count + 1
            if count >= 60:
                count = 0
                slack.send_event('Health ping from {}'.format(settings.HOSTNAME), url=settings.DEBUG_WEBHOOK, channel=settings.DEBUG_CHANNEL)
            time.sleep(60)

def main():
    while True:
        if fifa.should_send_daily_matches():
            daily_matches = fifa.get_daily_matches()
            log.debug(f"daily_matches == {daily_matches}")
            if daily_matches != '':
                slack.send_event(daily_matches)
                fifa.save_last_daily_matches_sent()
        log.debug("checking events update...")
        events = fifa.check_for_updates()
        for event in events:
            if event['debug'] == True and settings.DEBUG and settings.DEBUG_WEBHOOK != '':
                slack.send_event(event['message'], url=settings.DEBUG_WEBHOOK, channel=settings.DEBUG_CHANNEL)
                log.debug("Before sending to slack, DEBUG")
            else:
                log.debug("Before sending to slack")       
                slack.send_event(event['message'])
        log.debug("Sleeping...")       
        time.sleep(60)

if __name__ == '__main__':
    executor = ProcessPoolExecutor(2)
    loop = asyncio.get_event_loop()

    try:
        tasks = [asyncio.ensure_future(loop.run_in_executor(executor, main))]
        if settings.DEBUG and settings.DEBUG_WEBHOOK != '':
            tasks.append(asyncio.ensure_future(loop.run_in_executor(executor, heart_beat)))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        log.info("Cleaning up...")
        [task.cancel() for task in tasks if not task.cancelled()]
        executor.shutdown(wait=True)
        loop.close()
