# Slack wc-watcher
This bot uses the undocumented FIFA API's to report on World Cup matches. It will check every 60 seconds for new events. The following events are reported:
+ Goals scored
+ Yellow/Red cards
+ Substitutions
+ Match start/stop
+ Penalty kicks missed/scored

### Sample
[![sample](https://github.com/ImDevinC/wc-watcher/raw/master/ss.png)](#sample)

### Usage
1. Setup a new Slack App (https://api.slack.com/apps) with Webhook permission
1. Copy `.env.template` to `.env`
1. In `.env`, change `WEBHOOK_URL` to point to your Slack webhook
    + If you want to see debug information, which currently pings a heartbeat every hour, also fill in the `DEBUG_WEBHOOK` url with a Slack webhook and set `DEBUG = True`
    + You can also set `WC_COMPETITION = None` in `src/fifa.py` to get all current FIFA matches and see what the output looks like. Just make sure to change it back to `WC_COMPETITION = 17` for world cup only
1. In `.env`, change `CHANNEL` to the desired channel in your Slack space
1. Use `pip install -r requirements.txt`
1. Run `python main.py`

### Card emoji
1. Go to https://slack.com/customize/emoji
1. Enter `yellow_card` as name
1. Upload `card_yellow.png`
1. Save emoji

Repeat for `red_card` and `card_red.png`

## Docker

Build docker image

```
docker build -t soccerbot .
```

Run in `NO_SLACK` mode (outputs events to terminal instead of sending to Slack)
```
docker run --rm -it -e NO_SLACK=True soccerbot
```
